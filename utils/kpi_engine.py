from utils.kpi_helpers import (
    first_column, safe_numeric_series, safe_datetime_series, 
    safe_kpi, excluded_kpi
)
from utils.confidence_engine import evaluate_kpi_confidence
from utils.validator import SemanticValidator

class KPIEngine:
    """
    Central Corporate Dispatcher.
    Industry files ONLY talk to this class. This class talks to the rest of the utils folder.
    """
    def __init__(self, df):
        self.df = df
        self.used_columns = [] 

    # --- 1. DATA EXTRACTION (Talks to kpi_helpers) ---

    def get_column(self, candidates):
        col = first_column(self.df, candidates)
        if col:
            self.used_columns.append(col)
            return col, self.df[col]
        return None, None

    def get_numeric(self, candidates):
        col = first_column(self.df, candidates)
        if col:
            series = safe_numeric_series(self.df, col)
            if series is not None:
                self.used_columns.append(col)
                return col, series.dropna()
        return None, None

    def get_datetime(self, candidates):
        col = first_column(self.df, candidates)
        if col:
            series = safe_datetime_series(self.df, col)
            if series is not None:
                self.used_columns.append(col)
                return col, series.dropna()
        return None, None

    # --- 2. BUSINESS VALIDATION (Talks to validator.py) ---
    
    def validate_business_rule(self, rule_name, series):
        """
        Routes specialized checks to SemanticValidator.
        Example: engine.validate_business_rule("dosage", dosage_series)
        """
        if rule_name == "dosage":
            return SemanticValidator.is_valid_dosage(series)
        elif rule_name == "percentage":
            return SemanticValidator.is_valid_percentage(series)
        # Add more mappings as you invent them!
        return True, "Valid"

    # --- 3. FORMATTING & GOVERNANCE (Talks to confidence_engine) ---

    def build_kpi(self, category, name, value, formula, source, warnings="None", **kwargs):
        """Builds KPI and talks to confidence_engine automatically."""
        confidence, auto_warn = evaluate_kpi_confidence(self.df, self.used_columns)
        final_warn = auto_warn if warnings == "None" else f"{warnings} | {auto_warn}"
        
        return safe_kpi(category, name, value, formula, source, confidence, final_warn, **kwargs)

    def log_missing(self, category, name, reason):
        return excluded_kpi(category, name, "Diagnostic", reason)
