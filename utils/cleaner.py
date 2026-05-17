import pandas as pd
import sys
import os

# ==========================================
# 1. DATA INGESTION (The part that went missing)
# ==========================================
def load_and_clean(file_path):
    """
    Ingests the raw file (CSV, ZIP, or Excel) and drops 100% empty rows/columns.
    """
    print(f"📥 Attempting to load: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        sys.exit(1)
        
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.zip'):
            df = pd.read_csv(file_path, compression='zip')
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            print("⚠️ Error: Unsupported file format.")
            sys.exit(1)

        # Drop columns/rows that are 100% empty (NaN)
        df.dropna(how='all', axis=1, inplace=True)
        df.dropna(how='all', axis=0, inplace=True)
        
        print(f"🧹 Data loaded and empty rows dropped. Shape: {df.shape}")
        return df

    except Exception as e:
        print(f"❌ Critical failure while loading data: {e}")
        sys.exit(1)

# ==========================================
# 2. UNIVERSAL DATA ENGINEERING (The new math)
# ==========================================
def standardize_column_names(df):
    """Converts all columns to lowercase and replaces spaces with underscores."""
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df

def remove_duplicates(df):
    """Drops exact duplicate rows and returns the cleaned dataframe."""
    initial_shape = df.shape[0]
    df = df.drop_duplicates()
    final_shape = df.shape[0]
    if initial_shape != final_shape:
        print(f"🧹 Dropped {initial_shape - final_shape} duplicate rows.")
    return df

def fill_numeric_missing(df, strategy='median'):
    """Fills missing numeric values universally."""
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            if strategy == 'median':
                df[col] = df[col].fillna(df[col].median())
            elif strategy == 'mean':
                df[col] = df[col].fillna(df[col].mean())
    return df

def fix_datetime_columns(df):
    """Attempts to auto-detect and fix datetime columns."""
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass # If it fails, leave it as is
    return df

def universal_clean(df):
    """The master function to run all universal cleaning steps."""
    print("⚙️ Running universal data engineering layers...")
    df = standardize_column_names(df)
    df = remove_duplicates(df)
    df = fill_numeric_missing(df)
    df = fix_datetime_columns(df)
    return df
