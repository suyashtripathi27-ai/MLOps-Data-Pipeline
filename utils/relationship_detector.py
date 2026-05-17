import pandas as pd

def fill_missing_by_mapping(df, source_col, target_col):
    """
    Universally detects 1-to-1 relationships to fill missing text values.
    Example: If Store 123 is usually "Main St", it fills in missing "Main St" 
    wherever Store 123 appears.
    """
    if source_col not in df.columns or target_col not in df.columns:
        return df
        
    print(f"🔗 Attempting to map relationships between {source_col} and {target_col}...")
    
    # Create a clean dictionary of known, non-null mappings
    valid_mappings = df.dropna(subset=[source_col, target_col])
    mapping_dict = valid_mappings.set_index(source_col)[target_col].to_dict()
    
    # Fill the missing values in the target column using the dictionary
    missing_before = df[target_col].isnull().sum()
    df[target_col] = df[target_col].fillna(df[source_col].map(mapping_dict))
    missing_after = df[target_col].isnull().sum()
    
    if missing_before != missing_after:
        print(f"✅ Successfully mapped and filled {missing_before - missing_after} missing values in {target_col}.")
        
    return df
