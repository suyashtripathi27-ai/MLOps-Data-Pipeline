from utils.kpi_helpers import (
    first_column, safe_numeric_series, safe_datetime_series, 
    safe_kpi, excluded_kpi
)
from utils.confidence_engine import evaluate_kpi_confidence
from utils.validator import SemanticValidator
from typing import Tuple, Optional, List, Any, Callable, Dict

class KPIEngine:
    """
    Central Corporate Dispatcher.
    Industry files ONLY talk to this class. This class talks to the rest of the utils folder.
    
    Features:
    - Data extraction with automatic column tracking
    - Pluggable business rule validation
    - Configurable confidence scoring per-industry
    - Reusable KPI templates
    """
    
    def __init__(self, df, industry_config: Optional[Dict[str, Any]] = None):
        """
        Initialize KPI Engine for an industry/use-case.
        
        Args:
            df: Input DataFrame
            industry_config: Optional dict with keys:
                - missing_data_threshold (default: 10%)
                - score_deduction_for_warning (default: 15)
                - low_confidence_threshold (default: 30)
                - custom_industry_checks (callable for domain-specific validation)
        """
        self.df = df
        self.used_columns = []
        
        # ✅ NEW: Per-industry confidence configuration
        self.confidence_config = industry_config or {}
        self.missing_data_threshold = self.confidence_config.get("missing_data_threshold", 10)
        self.score_deduction_for_warning = self.confidence_config.get("score_deduction_for_warning", 15)
        self.low_confidence_threshold = self.confidence_config.get("low_confidence_threshold", 30)
        self.custom_industry_checks = self.confidence_config.get("custom_industry_checks", None)
        
        # ✅ NEW: Pluggable business rules registry
        self.business_rules: Dict[str, Callable] = {
            "dosage": SemanticValidator.is_valid_dosage,
            "percentage": SemanticValidator.is_valid_percentage,
            "duration": SemanticValidator.is_valid_duration,
            "datetime": SemanticValidator.is_valid_datetime,
            "adverse_event": SemanticValidator.is_valid_adverse_event_count,
            "gmp_compliance": SemanticValidator.is_valid_gmp_compliance,
        }
        
        # ✅ NEW: KPI template registry for reusable patterns
        self.kpi_templates: Dict[str, Callable] = {}
    
    # ==========================================
    # 0. REGISTRY MANAGEMENT (Plugin System)
    # ==========================================
    
    def add_business_rule(self, rule_name: str, validator_func: Callable) -> None:
        """
        Add or override a business rule validator.
        
        Args:
            rule_name: Name of the rule (e.g., "dosage", "batch_size")
            validator_func: Function that takes (series) and returns (is_valid: bool, reason: str)
        """
        self.business_rules[rule_name] = validator_func
    
    def register_kpi_template(self, template_name: str, template_func: Callable) -> None:
        """
        Register a reusable KPI calculation template.
        
        Args:
            template_name: Name of the template
            template_func: Function that takes (engine, **overrides) and returns KPI dict
        """
        self.kpi_templates[template_name] = template_func
    
    # ==========================================
    # 1. DATA EXTRACTION (Talks to kpi_helpers)
    # ==========================================

    def get_column(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first matching column from candidates.
        Automatically tracks the column for confidence scoring.
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, series_data) or (None, None) if not found
        """
        col = first_column(self.df, candidates)
        if col:
            self.used_columns.append(col)
            return col, self.df[col]
        return None, None

    def get_numeric(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first numeric column from candidates.
        Handles string-to-numeric coercion ($, %, commas).
        Automatically tracks the column.
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, numeric_series) or (None, None) if not found/invalid
        """
        col = first_column(self.df, candidates)
        if col:
            series = safe_numeric_series(self.df, col)
            if series is not None:
                self.used_columns.append(col)
                return col, series.dropna()
        return None, None

    def get_datetime(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first datetime column from candidates.
        Handles string-to-datetime coercion and validates against epoch anomalies.
        Automatically tracks the column.
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, datetime_series) or (None, None) if not found/invalid
        """
        col = first_column(self.df, candidates)
        if col:
            series = safe_datetime_series(self.df, col)
            if series is not None:
                self.used_columns.append(col)
                return col, series.dropna()
        return None, None
    
    def reset_column_tracking(self) -> None:
        """
        Clear the used_columns tracker.
        Useful if you want to calculate multiple independent KPI groups.
        """
        self.used_columns = []

    # ==========================================
    # 2. BUSINESS VALIDATION (Talks to validator.py)
    # ==========================================
    
    def validate_business_rule(self, rule_name: str, series: Any) -> Tuple[bool, str]:
        """
        Routes specialized business rule checks to SemanticValidator.
        
        Args:
            rule_name: Name of the rule (e.g., "dosage", "percentage", "duration")
            series: pandas Series to validate
            
        Returns:
            Tuple of (is_valid: bool, reason: str)
            
        Examples:
            is_valid, reason = engine.validate_business_rule("dosage", dosage_series)
            is_valid, reason = engine.validate_business_rule("percentage", pct_series)
        """
        if rule_name not in self.business_rules:
            # Graceful fallback: unknown rules pass validation
            return True, f"Rule '{rule_name}' not registered (using default: Valid)"
        
        return self.business_rules[rule_name](series)

    # ==========================================
    # 3. FORMATTING & GOVERNANCE (Talks to confidence_engine)
    # ==========================================

    def build_kpi(
        self, 
        category: str, 
        name: str, 
        value: str, 
        formula: str, 
        source: str, 
        confidence: Optional[str] = None,
        warnings: str = "None",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build a standardized KPI dictionary with automatic confidence scoring.
        
        Args:
            category: KPI category/group (e.g., "💳 Account Analysis")
            name: KPI name (e.g., "Total Active Accounts")
            value: Formatted value (e.g., "1,234" or "$5,678.90")
            formula: Calculation formula (e.g., "Sum(Amount)")
            source: Source column(s) (e.g., "`account_id`, `amount`")
            confidence: Manual confidence override (High/Medium/Low). If None, auto-calculated.
            warnings: Custom warning message. Auto-warnings from confidence engine are appended.
            **kwargs: Additional fields to include in KPI dict
            
        Returns:
            Standardized KPI dictionary with confidence and warnings
            
        Example:
            kpi = engine.build_kpi(
                category="💳 Account Analysis",
                name="Total Active Accounts",
                value="1,234",
                formula="Count(Distinct Account IDs)",
                source="`account_id`"
            )
        """
        # Auto-calculate confidence if not provided
        if confidence is None:
            confidence, auto_warn = evaluate_kpi_confidence(
                self.df, 
                self.used_columns,
                custom_industry_checks=self.custom_industry_checks
            )
        else:
            auto_warn = "None"
        
        # Merge custom warnings with auto-warnings
        if warnings == "None":
            final_warn = auto_warn
        elif auto_warn == "None":
            final_warn = warnings
        else:
            final_warn = f"{warnings} | {auto_warn}"
        
        return safe_kpi(category, name, value, formula, source, confidence, final_warn, **kwargs)

    def log_missing(
        self, 
        category: str, 
        name: str, 
        reason: str,
        source: str = "Diagnostic"
    ) -> Dict[str, Any]:
        """
        Create a diagnostic entry for missing/excluded KPIs.
        
        Args:
            category: KPI category
            name: KPI name
            reason: Why the KPI is excluded
            source: Source of diagnostic (default: "Diagnostic")
            
        Returns:
            Standardized excluded KPI dictionary with Low confidence
            
        Example:
            kpi = engine.log_missing(
                "💳 Account Analysis", 
                "Active Accounts", 
                "Missing 'account_id' column."
            )
        """
        return excluded_kpi(category, name, source, reason)
    
    # ==========================================
    # 4. TEMPLATE SYSTEM (Reusable Patterns)
    # ==========================================
    
    def build_from_template(self, template_name: str, **overrides) -> Dict[str, Any]:
        """
        Build a KPI using a registered template with custom overrides.
        
        Args:
            template_name: Name of the registered template
            **overrides: Values to override template defaults
            
        Returns:
            Calculated KPI dictionary
            
        Example:
            # Register template once
            def sum_metric_template(engine, col_candidates, name, category):
                col, series = engine.get_numeric(col_candidates)
                if col is None:
                    return engine.log_missing(category, name, "Missing numeric column")
                return engine.build_kpi(
                    category, name, 
                    f"${series.sum():,.2f}", 
                    f"Sum({col})", f"`{col}`"
                )
            
            engine.register_kpi_template("sum_metric", sum_metric_template)
            
            # Use template
            kpi = engine.build_from_template("sum_metric", 
                col_candidates=["amount", "transaction_amount"],
                name="Total Volume",
                category="💳 Account Analysis"
            )
        """
        if template_name not in self.kpi_templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available: {list(self.kpi_templates.keys())}"
            )
        return self.kpi_templates[template_name](self, **overrides)
    
    def list_templates(self) -> List[str]:
        """Return list of registered template names."""
        return list(self.kpi_templates.keys())
    
    def list_business_rules(self) -> List[str]:
        """Return list of registered business rules."""
        return list(self.business_rules.keys())
    
    # ==========================================
    # 5. DIAGNOSTICS & DEBUGGING
    # ==========================================
    
    def get_used_columns(self) -> List[str]:
        """Return list of columns used in current KPI batch."""
        return self.used_columns.copy()
    
    def get_unused_columns(self) -> List[str]:
        """Return list of columns NOT used in current KPI batch."""
        return [col for col in self.df.columns if col not in self.used_columns]
    
    def debug_info(self) -> Dict[str, Any]:
        """
        Return debugging information about the engine state.
        Useful for troubleshooting.
        """
        return {
            "dataframe_shape": self.df.shape,
            "total_columns": len(self.df.columns),
            "used_columns": self.used_columns,
            "unused_columns": self.get_unused_columns(),
            "registered_templates": self.list_templates(),
            "registered_business_rules": self.list_business_rules(),
            "confidence_config": {
                "missing_data_threshold": self.missing_data_threshold,
                "score_deduction_for_warning": self.score_deduction_for_warning,
                "low_confidence_threshold": self.low_confidence_threshold,
            }
        }
