import pandas as pd

def enrich_fact_table(fact_df, all_dfs):
    """
    Intelligently left-joins dimension tables onto the primary fact table 
    by hunting for matching foreign keys (columns ending in _id or _uuid).
    """
    print("\n🤝 Initializing Relationship Detector...")
    enriched_df = fact_df.copy()
    
    # Step 1: Find potential foreign keys in the fact table
    fk_columns = [col for col in enriched_df.columns if col.endswith(('_id', '_uuid'))]
    
    if not fk_columns:
        print("ℹ️ No obvious foreign keys found in the fact table. Skipping enrichment.")
        return enriched_df
        
    print(f"🔍 Found potential foreign keys in Fact Table: {fk_columns}")
    
    # Step 2: Hunt through the other dimension tables for matches
    for dim_name, dim_df in all_dfs.items():
        # Look for matching columns
        common_keys = list(set(fk_columns).intersection(set(dim_df.columns)))
        
        if common_keys:
            join_key = common_keys[0] # Take the first matching key
            print(f"🔗 Match found! Joining `{dim_name}` onto Fact Table using key: `{join_key}`")
            
            # Step 3: SAFE Left Join
            # We drop columns from the dim table that already exist in the fact table (except the join key)
            # This prevents pandas from creating ugly columns like 'name_x' and 'name_y'
            cols_to_use = dim_df.columns.difference(enriched_df.columns).tolist() + [join_key]
            
            try:
                enriched_df = pd.merge(enriched_df, dim_df[cols_to_use], on=join_key, how='left')
            except Exception as e:
                print(f"⚠️ Failed to join {dim_name}: {e}")
                
    print(f"✨ Enrichment complete. New Fact Table Shape: {enriched_df.shape}\n")
    return enriched_df
