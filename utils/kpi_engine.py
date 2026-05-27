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
    - KPI Deduplication and Governance Aggregation
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
        """Add or override a business rule validator."""
        self.business_rules[rule_name] = validator_func
        self._log_trace("rule_registered", {"rule_name": rule_name})
    
    def register_kpi_template(self, template_name: str, template_func: Callable) -> None:
        """Register a reusable KPI calculation template."""
        self.kpi_templates[template_name] = template_func
        self._log_trace("template_registered", {"template_name": template_name})
    
    # ==========================================
    # 1. DATA EXTRACTION (Talks to kpi_helpers)
    # ==========================================

    def get_column(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        """Find and return the first matching column from candidates."""
        col = first_column(self.df, candidates)
        if col:
            self.used_columns.add(col)  
            self._log_trace("column_mapped", {
                "col": col,
                "candidates": candidates,
                "type": str(self.df[col].dtype)
            })
            return col, self.df[col]
        
        self._log_
