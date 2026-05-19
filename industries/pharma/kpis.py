"""
Pharma KPI Generators - Clinical Trial, Manufacturing & Supply Chain Metrics
"""
import pandas as pd
from datetime import datetime

def calc_drug_development_kpis(df):
    """Calculate drug development pipeline KPIs."""
    kpis = []
    
    if 'phase' in df.columns and 'enrollment_status' in df.columns:
        phase_distribution = df['phase'].value_counts()
        active_trials = len(df[df['enrollment_status'] == 'Active'])
        completion_rate = (len(df[df['enrollment_status'] == 'Completed']) / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append({
            'category': 'Clinical Trials',
            'name': 'Active Trial Count',
            'value': active_trials,
            'formula': 'COUNT(enrollment_status == "Active")',
            'source': 'enrollment_status column',
            'confidence': '95%',
            'warnings': 'None' if active_trials > 0 else 'No active trials found'
        })
        
        kpis.append({
            'category': 'Clinical Trials',
            'name': 'Trial Completion Rate',
            'value': f'{completion_rate:.2f}%',
            'formula': 'COUNT(Completed) / TOTAL * 100',
            'source': 'enrollment_status column',
            'confidence': '90%',
            'warnings': 'None' if completion_rate > 50 else 'Low completion rate - investigate delays'
        })
    
    return kpis

def calc_manufacturing_compliance_kpis(df):
    """Calculate GMP (Good Manufacturing Practice) compliance KPIs."""
    kpis = []
    
    if 'gmp_inspection_date' in df.columns and 'defects_found' in df.columns:
        batches_compliant = len(df[df['defects_found'] == 0])
        compliance_percentage = (batches_compliant / len(df) * 100) if len(df) > 0 else 0
        avg_defects = df['defects_found'].mean() if 'defects_found' in df.columns else 0
        
        kpis.append({
            'category': 'Manufacturing',
            'name': 'GMP Compliance Rate',
            'value': f'{compliance_percentage:.2f}%',
            'formula': 'COUNT(defects_found == 0) / TOTAL * 100',
            'source': 'defects_found column',
            'confidence': '98%',
            'warnings': 'None' if compliance_percentage > 95 else '⚠️ Below 95% compliance threshold'
        })
        
        kpis.append({
            'category': 'Manufacturing',
            'name': 'Average Defects per Batch',
            'value': f'{avg_defects:.2f}',
            'formula': 'AVG(defects_found)',
            'source': 'defects_found column',
            'confidence': '92%',
            'warnings': 'None' if avg_defects < 2 else 'High defect rate detected'
        })
    
    return kpis

def calc_supply_chain_kpis(df):
    """Calculate pharmaceutical supply chain KPIs."""
    kpis = []
    
    if 'stock_level' in df.columns and 'reorder_point' in df.columns:
        stockouts = len(df[df['stock_level'] == 0])
        low_stock_items = len(df[df['stock_level'] < df['reorder_point']])
        total_items = len(df)
        
        kpis.append({
            'category': 'Supply Chain',
            'name': 'Inventory Availability',
            'value': f'{((total_items - stockouts) / total_items * 100):.2f}%',
            'formula': '(TOTAL - COUNT(stock == 0)) / TOTAL * 100',
            'source': 'stock_level column',
            'confidence': '96%',
            'warnings': f'{stockouts} items currently out of stock' if stockouts > 0 else 'None'
        })
        
        kpis.append({
            'category': 'Supply Chain',
            'name': 'Below Reorder Point Items',
            'value': low_stock_items,
            'formula': 'COUNT(stock_level < reorder_point)',
            'source': 'stock_level and reorder_point columns',
            'confidence': '97%',
            'warnings': 'None' if low_stock_items < 5 else f'⚠️ {low_stock_items} items need reordering'
        })
    
    return kpis

def calc_regulatory_compliance_kpis(df):
    """Calculate FDA/regulatory compliance KPIs."""
    kpis = []
    
    if 'regulatory_status' in df.columns:
        approved = len(df[df['regulatory_status'] == 'Approved'])
        pending = len(df[df['regulatory_status'] == 'Pending'])
        rejected = len(df[df['regulatory_status'] == 'Rejected'])
        
        kpis.append({
            'category': 'Regulatory',
            'name': 'FDA Approved Products',
            'value': approved,
            'formula': 'COUNT(regulatory_status == "Approved")',
            'source': 'regulatory_status column',
            'confidence': '99%',
            'warnings': 'None'
        })
        
        kpis.append({
            'category': 'Regulatory',
            'name': 'Pending Approvals',
            'value': pending,
            'formula': 'COUNT(regulatory_status == "Pending")',
            'source': 'regulatory_status column',
            'confidence': '99%',
            'warnings': f'Track {pending} applications in progress' if pending > 0 else 'None'
        })
    
    return kpis

def generate_pharma_kpis(df):
    """Main aggregator for all pharma KPIs."""
    all_kpis = []
    all_kpis.extend(calc_drug_development_kpis(df))
    all_kpis.extend(calc_manufacturing_compliance_kpis(df))
    all_kpis.extend(calc_supply_chain_kpis(df))
    all_kpis.extend(calc_regulatory_compliance_kpis(df))
    return all_kpis
