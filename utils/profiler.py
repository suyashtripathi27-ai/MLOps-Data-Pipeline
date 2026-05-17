import pandas as pd

def generate_payload(df):
    """
    Calculates statistics, data types, and missing values to feed the AI.
    It formats everything into a clean text block for the prompt.
    """
    print("📊 Generating statistical payload...")
    
    # 1. Basic Shape & Types
    data_shape = f"Total Rows: {df.shape[0]} | Total Columns: {df.shape[1]}"
    data_types = df.dtypes.to_string()
    
    # 2. Math Summary
    data_stats = df.describe(include='all').to_string()
    
    # 3. Missing Value Analysis (Token Efficient!)
    missing_data = df.isnull().sum()
    missing_percent = (df.isnull().sum() / len(df)) * 100
    missing_report = pd.DataFrame({'Missing Rows': missing_data, 'Percentage': missing_percent})
    
    # Only show columns that actually have missing data
    missing_summary = missing_report[missing_report['Missing Rows'] > 0].to_string()
    
    # If there is no missing data, tell the AI it's clean
    if "Empty DataFrame" in missing_summary:
        missing_summary = "No missing data detected. Dataset is 100% clean."

    # 4. Bundle it all together
    return f"""
    [DATASET SHAPE]
    {data_shape}
    
    [MISSING DATA SUMMARY]
    {missing_summary}
    
    [COLUMN DATA TYPES]
    {data_types}
    
    [STATISTICAL SUMMARY]
    {data_stats}
    """
