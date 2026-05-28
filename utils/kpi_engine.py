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
    """
    
    def __init__(self, df, industry_config: Optional[Dict[str, Any]] = None):
        self.df = df
        self.used_columns: Set[str] = set()
        
        self.confidence_config = industry_config or {}
        self.missing_data_threshold = self.confidence_config.get("missing_data_threshold", 10)
        self.score_deduction_for_warning = self.confidence_config.get("score_deduction_for_warning", 15)
        self.low_confidence_threshold = self.confidence_config.get("low_confidence_threshold", 30)
        self.custom_industry_checks = self.confidence_config.get("custom_industry_checks", None)
        
        self.business_rules: Dict[str, Callable] = {
            "dosage": SemanticValidator.is_valid_dosage,
            "percentage": SemanticValidator.is_valid_percentage,
            "duration": SemanticValidator.is_valid_duration,
            "datetime": SemanticValidator.is_valid_datetime,
            "adverse_event": SemanticValidator.is_valid_adverse_event_count,
            "gmp_compliance": SemanticValidator.is_valid_gmp_compliance,
        }
        
        self.kpi_templates: Dict[str, Callable] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self._trace_enabled = False
    
    def add_business_rule(self, rule_name: str, validator_func: Callable) -> None:
        self.business_rules[rule_name] = validator_func
        self._log_trace("rule_registered", {"rule_name": rule_name})
    
    def register_kpi_template(self, template_name: str, template_func: Callable) -> None:
        self.kpi_templates[template_name] = template_func
        self._log_trace("template_registered", {"template_name": template_name})
    
    def get_column(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        col = first_column(self.df, candidates)
        if col:
            self.used_columns.add(col)  
            self._log_trace("column_mapped", {
                "col": col, "candidates": candidates, "type": str(self.df[col].dtype)
            })
            return col, self.df[col]
        self._log_trace("column_not_found", {"candidates": candidates})
        return None, None

    def get_numeric(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        col = first_column(self.df, candidates)
        if col:
            series = safe_numeric_series(self.df, col)
            if series is not None:
                self.used_columns.add(col)  
                non_null_count = len(series)
                total_count = len(self.df)
                coercion_failure_rate = ((total_count - non_null_count) / total_count * 100) if total_count > 0 else 0
                self._log_trace("numeric_coercion_applied", {
                    "col": col, "candidates": candidates,
                    "non_null_rows": non_null_count, "coercion_failure_rate": f"{coercion_failure_rate:.1f}%"
                })
                return col, series.dropna()
            else:
                self._log_trace("numeric_coercion_failed", {
                    "col": col, "reason": "All values failed numeric conversion"
                })
        self._log_trace("numeric_column_not_found", {"candidates": candidates})
        return None, None

    def get_datetime(self, candidates: List[str]) -> Tuple[Optional[str], Optional[Any]]:
        col = first_column(self.df, candidates)
        if col:
            series = safe_datetime_series(self.df, col)  
            if series is not None:
                self.used_columns.add(col)  
                self._log_trace("datetime_coercion_applied", {
                    "col": col, "candidates": candidates,
                    "min_date": str(series.min()), "max_date": str(series.max())
                })
                return col, series.dropna()
            else:
                self._log_trace("datetime_coercion_failed", {
                    "col": col, "reason": "Date parsing failed or epoch anomaly detected"
                })
        self._log_trace("datetime_column_not_found", {"candidates": candidates})
        return None, None
    
    def reset_column_tracking(self) -> None:
        self.used_columns.clear()
        self._log_trace("column_tracking_reset", {})

    def validate_business_rule(self, rule_name: str, series: Any) -> Tuple[bool, str]:
        if rule_name not in self.business_rules:
            msg = f"Rule '{rule_name}' not registered (using default: Valid)"
            self._log_trace("business_rule_not_found", {"rule_name": rule_name})
            return True, msg
        is_valid, reason = self.business_rules[rule_name](series)
        self._log_trace("business_rule_validated", {
            "rule_name": rule_name, "is_valid": is_valid, "reason": reason
        })
        return is_valid, reason

    def build_kpi(self, category: str, name: str, value: str, formula: str, source: str, confidence: Optional[str] = None, warnings: str = "None", **kwargs) -> Dict[str, Any]:
        if confidence is None:
            confidence, auto_warn = evaluate_kpi_confidence(self.df, list(self.used_columns), custom_industry_checks=self.custom_industry_checks)
        else:
            auto_warn = "None"
        
        if warnings == "None":
            final_warn = auto_warn
        elif auto_warn == "None":
            final_warn = warnings
        else:
            final_warn = f"{warnings} | {auto_warn}"
        
        self._log_trace("kpi_built", {
            "category": category, "name": name, "confidence": confidence,
            "warnings": final_warn, "columns_used": list(self.used_columns)
        })
        
        # Hard-tag as operational to guarantee pipeline routing
        kpi_dict = safe_kpi(category, name, value, formula, source, confidence, final_warn, **kwargs)
        kpi_dict["signal_type"] = "operational"
        return kpi_dict

    def log_missing(self, category: str, name: str, reason: str, source: str = "Diagnostic") -> Dict[str, Any]:
        self._log_trace("kpi_excluded", {"category": category, "name": name, "reason": reason})
        
        # Hard-tag as governance to guarantee pipeline routing
        kpi_dict = excluded_kpi(category, name, source, reason)
        kpi_dict["signal_type"] = "governance"
        return kpi_dict
    
    def build_from_template(self, template_name: str, **overrides) -> Dict[str, Any]:
        if template_name not in self.kpi_templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.kpi_templates.keys())}")
        self._log_trace("template_used", {"template_name": template_name, "overrides": overrides})
        return self.kpi_templates[template_name](self, **overrides)
    
    def list_templates(self) -> List[str]: return list(self.kpi_templates.keys())
    def list_business_rules(self) -> List[str]: return list(self.business_rules.keys())
    
    def enable_tracing(self, enabled: bool = True) -> None:
        self._trace_enabled = enabled
        self._log_trace("tracing_toggled", {"enabled": enabled})
    
    def _log_trace(self, event_type: str, details: Dict[str, Any]) -> None:
        if self._trace_enabled:
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type, "details": details
            })
    
    def get_execution_log(self) -> List[Dict[str, Any]]: return self.execution_log.copy()
    def clear_execution_log(self) -> None: self.execution_log.clear()
    
    def print_execution_log(self) -> None:
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
    
    def get_used_columns(self) -> List[str]: return sorted(list(self.used_columns))
    def get_unused_columns(self) -> List[str]:
        return sorted([col for col in self.df.columns if col not in self.used_columns])
    
    def debug_info(self) -> Dict[str, Any]:
        return {
            "dataframe_shape": self.df.shape, "total_columns": len(self.df.columns),
            "used_columns": self.get_used_columns(), "unused_columns": self.get_unused_columns(),
            "registered_templates": self.list_templates(), "registered_business_rules": self.list_business_rules(),
            "confidence_config": self.confidence_config, "tracing_enabled": self._trace_enabled,
            "execution_log_size": len(self.execution_log)
        }

    @staticmethod
    def deduplicate_diagnostics(kpi_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_kpis = []
        excluded_tracker = {}

        for kpi in kpi_list:
            if kpi.get("value") == "EXCLUDED":
                reason = kpi.get("warnings", "Missing data elements.")
                category = kpi.get("category", "Unknown")
                if reason not in excluded_tracker:
                    excluded_tracker[reason] = {"categories": set([category]), "count": 1}
                else:
                    excluded_tracker[reason]["categories"].add(category)
                    excluded_tracker[reason]["count"] += 1
            else:
                valid_kpis.append(kpi)

        for reason, data in excluded_tracker.items():
            affected_cats = ", ".join(sorted(list(data["categories"])))
            valid_kpis.append({
                "category": "🛠️ System Diagnostics",
                "name": f"Excluded Metrics ({data['count']} Items)",
                "value": "EXCLUDED",
                "formula": "N/A",
                "source": "Governance Engine",
                "confidence": "Low",
                "warnings": f"Affected Areas: [{affected_cats}] | Reason: {reason}",
                "signal_type": "governance"  # 👈 Ensure consolidated missing data goes to governance!
            })

        return valid_kpis
