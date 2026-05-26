from utils.kpi_helpers import (
    first_column, safe_numeric_series, safe_datetime_series, 
    safe_kpi, excluded_kpi
)
from utils.confidence_engine import evaluate_kpi_confidence
from utils.validator import SemanticValidator
from typing import Tuple, Optional, Set, List, Any, Callable, Dict
from datetime import datetime

class KPIEngine:
    """
    Central Corporate Dispatcher.
    Industry files ONLY talk to this class. This class talks to the rest of the utils folder.
    
    Features:
    - Data extraction with automatic column tracking (no duplicates via set)
    - Pluggable business rule validation
    - Configurable confidence scoring per-industry
    - Reusable KPI templates (for HIGHLY repeated patterns only)
    - Execution tracing for enterprise observability
    """
    
    def __init__(self, df, industry_config: Optional[Dict[str, Any]] = None):
        """
        Initialize KPI Engine for an industry/use-case.
        
        Args:
            df: Input DataFrame
            industry_config: Optional dict with keys:
                - missing_data_threshold (default: 10%) - % missing data before warning
                - score_deduction_for_warning (default: 15) - points deducted per warning
                - low_confidence_threshold (default: 30) - score above this = Low confidence
                - custom_industry_checks (callable for domain-specific validation)
        """
        self.df = df
        self.used_columns: Set[str] = set()
        
        # Per-industry confidence configuration
        self.confidence_config = industry_config or {}
        self.missing_data_threshold = self.confidence_config.get("missing_data_threshold", 10)
        self.score_deduction_for_warning = self.confidence_config.get("score_deduction_for_warning", 15)
        self.low_confidence_threshold = self.confidence_config.get("low_confidence_threshold", 30)
        self.custom_industry_checks = self.confidence_config.get("custom_industry_checks", None)
        
        # Pluggable business rules registry
        self.business_rules: Dict[str, Callable] = {
            "dosage": SemanticValidator.is_valid_dosage,
            "percentage": SemanticValidator.is_valid_percentage,
            "duration": SemanticValidator.is_valid_duration,
            "datetime": SemanticValidator.is_valid_datetime,
            "adverse_event": SemanticValidator.is_valid_adverse_event_count,
            "gmp_compliance": SemanticValidator.is_valid_gmp_compliance,
        }
        
        # KPI template registry (ONLY for highly repeated patterns)
        self.kpi_templates: Dict[str, Callable] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self._trace_enabled = False
    
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
        self._log_trace("rule_registered", {"rule_name": rule_name})
    
    def register_kpi_template(self, template_name: str, template_func: Callable) -> None:
        """
        Register a reusable KPI calculation template.
        
        ⚠️ WARNING: Only use for HIGHLY REPEATED patterns.
        Do NOT create 50 tiny templates - that's over-engineering.
        Good candidates: sum_metric, avg_metric, count_metric, growth_rate
        Bad candidates: one-off calculations specific to a single KPI
        
        Args:
            template_name: Name of the template
            template_func: Function that takes (engine, **overrides) and returns KPI dict
        """
        self.kpi_templates[template_name] = template_func
        self._log_trace("template_registered", {"template_name": template_name})
    
    # ==========================================
    # 1. DATA EXTRACTION (Talks to kpi_helpers)
    # ==========================================

    def get_column(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first matching column from candidates.
        Automatically tracks the column for confidence scoring (no duplicates).
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, series_data) or (None, None) if not found
        """
        col = first_column(self.df, candidates)
        if col:
            self.used_columns.add(col)  # ✅ ISSUE 1 FIX: set prevents duplicates
            self._log_trace("column_mapped", {
                "col": col,
                "candidates": candidates,
                "type": str(self.df[col].dtype)
            })
            return col, self.df[col]
        
        self._log_trace("column_not_found", {"candidates": candidates})
        return None, None

    def get_numeric(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first numeric column from candidates.
        Handles string-to-numeric coercion ($, %, commas).
        Automatically tracks the column (no duplicates).
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, numeric_series) or (None, None) if not found/invalid
        """
        col = first_column(self.df, candidates)
        if col:
            series = safe_numeric_series(self.df, col)
            if series is not None:
                self.used_columns.add(col)  
                non_null_count = len(series)
                total_count = len(self.df)
                coercion_failure_rate = ((total_count - non_null_count) / total_count * 100) if total_count > 0 else 0
                
                self._log_trace("numeric_coercion_applied", {
                    "col": col,
                    "candidates": candidates,
                    "non_null_rows": non_null_count,
                    "coercion_failure_rate": f"{coercion_failure_rate:.1f}%"
                })
                return col, series.dropna()
            else:
                self._log_trace("numeric_coercion_failed", {
                    "col": col,
                    "reason": "All values failed numeric conversion"
                })
        
        self._log_trace("numeric_column_not_found", {"candidates": candidates})
        return None, None

    def get_datetime(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """
        Find and return the first datetime column from candidates.
        Handles string-to-datetime coercion and validates against epoch anomalies.
        Automatically tracks the column (no duplicates).
        
        Args:
            candidates: List of column name variations to search
            
        Returns:
            Tuple of (column_name, datetime_series) or (None, None) if not found/invalid
        """
        col = first_column(self.df, candidates)
        if col:
            series = safe_datetime_series(self.df, col)  
            if series is not None:
                self.used_columns.add(col)  
                self._log_trace("datetime_coercion_applied", {
                    "col": col,
                    "candidates": candidates,
                    "min_date": str(series.min()),
                    "max_date": str(series.max())
                })
                return col, series.dropna()
            else:
                self._log_trace("datetime_coercion_failed", {
                    "col": col,
                    "reason": "Date parsing failed or epoch anomaly detected"
                })
        
        self._log_trace("datetime_column_not_found", {"candidates": candidates})
        return None, None
    
    def reset_column_tracking(self) -> None:
        """
        Clear the used_columns tracker.
        Useful if you want to calculate multiple independent KPI groups.
        """
        self.used_columns.clear()
        self._log_trace("column_tracking_reset", {})

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
            msg = f"Rule '{rule_name}' not registered (using default: Valid)"
            self._log_trace("business_rule_not_found", {"rule_name": rule_name})
            return True, msg
        
        is_valid, reason = self.business_rules[rule_name](series)
        self._log_trace("business_rule_validated", {
            "rule_name": rule_name,
            "is_valid": is_valid,
            "reason": reason
        })
        return is_valid, reason

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
        # Auto-calculate confidence if not provided
        if confidence is None:
            confidence, auto_warn = evaluate_kpi_confidence(
                self.df, 
                list(self.used_columns),  # Convert set to list for confidence_engine
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
        
        self._log_trace("kpi_built", {
            "category": category,
            "name": name,
            "confidence": confidence,
            "warnings": final_warn,
            "columns_used": list(self.used_columns)
        })
        
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
        self._log_trace("kpi_excluded", {
            "category": category,
            "name": name,
            "reason": reason
        })
        return excluded_kpi(category, name, source, reason)
    
    # ==========================================
    # 4. TEMPLATE SYSTEM (Reusable Patterns)
    # ==========================================
    
    def build_from_template(self, template_name: str, **overrides) -> Dict[str, Any]:

        if template_name not in self.kpi_templates:
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available: {list(self.kpi_templates.keys())}"
            )
        
        self._log_trace("template_used", {
            "template_name": template_name,
            "overrides": overrides
        })
        
        return self.kpi_templates[template_name](self, **overrides)
    
    def list_templates(self) -> List[str]:
        """Return list of registered template names."""
        return list(self.kpi_templates.keys())
    
    def list_business_rules(self) -> List[str]:
        """Return list of registered business rules."""
        return list(self.business_rules.keys())
    
    # ==========================================
    # 5. EXECUTION TRACING (Enterprise Observability)
    # ==========================================
    
    def enable_tracing(self, enabled: bool = True) -> None:
        self._trace_enabled = enabled
        self._log_trace("tracing_toggled", {"enabled": enabled})
    
    def _log_trace(self, event_type: str, details: Dict[str, Any]) -> None:
        """Internal method to log execution events."""
        if self._trace_enabled:
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "details": details
            })
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        return self.execution_log.copy()
    
    def clear_execution_log(self) -> None:
        """Clear the execution trace log."""
        self.execution_log.clear()
    
    def print_execution_log(self) -> None:
        """Pretty-print the execution trace log for debugging."""
        if not self.execution_log:
            print("📋 Execution log is empty. Enable tracing with engine.enable_tracing()")
            return
        
        print("\n" + "="*80)
        print("📋 EXECUTION TRACE LOG")
        print("="*80)
        for i, event in enumerate(self.execution_log, 1):
            print(f"\n[{i}] {event['event_type']} @ {event['timestamp']}")
            for key, value in event['details'].items():
                print(f"    {key}: {value}")
        print("\n" + "="*80 + "\n")
    
    # ==========================================
    # 6. DIAGNOSTICS & DEBUGGING
    # ==========================================
    
    def get_used_columns(self) -> List[str]:
        """Return list of columns used in current KPI batch (sorted)."""
        return sorted(list(self.used_columns))
    
    def get_unused_columns(self) -> List[str]:
        """Return list of columns NOT used in current KPI batch (sorted)."""
        unused = [col for col in self.df.columns if col not in self.used_columns]
        return sorted(unused)
    
    def debug_info(self) -> Dict[str, Any]:
        return {
            "dataframe_shape": self.df.shape,
            "total_columns": len(self.df.columns),
            "used_columns": self.get_used_columns(),
            "unused_columns": self.get_unused_columns(),
            "registered_templates": self.list_templates(),
            "registered_business_rules": self.list_business_rules(),
            "confidence_config": {
                "missing_data_threshold": self.missing_data_threshold,
                "score_deduction_for_warning": self.score_deduction_for_warning,
                "low_confidence_threshold": self.low_confidence_threshold,
            },
            "tracing_enabled": self._trace_enabled,
            "execution_log_size": len(self.execution_log)
        }
