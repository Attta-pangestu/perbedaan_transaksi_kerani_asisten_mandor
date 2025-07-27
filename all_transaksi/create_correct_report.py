#!/usr/bin/env python3
"""
Script untuk membuat laporan Excel yang benar
Menggunakan query yang sama persis seperti yang diberikan user
"""

import pandas as pd
import os
from datetime import datetime
from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def get_employee_name_mapping(connector):
    """Get employee name mapping"""
    query = "SELECT ID, NAME FROM EMP"
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        mapping = {}
        if not df.empty:
            for _, row in df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                mapping[emp_id] = emp_name
        
        return mapping
    except:
        return {}

def analyze_division_correct(connector, emp_mapping, div_id, div_name):
    """Analyze division dengan query yang benar"""
    print(f"\nAnalyzing {div_name} (ID: {div_id})")
    
    # Query untuk semua transaksi di divisi (TANPA filter status)
    query = f"""
    SELECT 
        a.SCANUSERID,
        a.RECORDTAG,
        COUNT(*) as transaction_count
    FROM 
        FFBSCANNERDATA04 a
    JOIN 
        OCFIELD b ON a.FIELDID = b.ID
    WHERE 
        b.DIVID = '{div_id}'
        AND a.TRANSDATE >= '2025-04-01' 
        AND a.TRANSDATE < '2025-04-29'
    GROUP BY a.SCANUSERID, a.RECORDTAG
    ORDER BY a.SCANUSERID, a.RECORDTAG
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print(f"  No data found for {div_name}")
            return None
        
        # Process results
        employees = {}
        total_kerani = 0
        total_mandor = 0
        total_asisten = 0
        
        for _, row in df.iterrows():
            scanuserid = str(row.iloc[0]).strip()
            recordtag = str(row.iloc[1]).strip()
            count = int(row.iloc[2])
            
            emp_name = emp_mapping.get(scanuserid, f"EMPLOYEE-{scanuserid}")
            
            if scanuserid not in employees:
                employees[scanuserid] = {
                    'name': emp_name,
                    'pm_count': 0,  # KERANI
                    'p1_count': 0,  # MANDOR
                    'p5_count': 0   # ASISTEN
                }
            
            if recordtag == 'PM':
                employees[scanuserid]['pm_count'] = count
                total_kerani += count
            elif recordtag == 'P1':
                employees[scanuserid]['p1_count'] = count
                total_mandor += count
            elif recordtag == 'P5':
                employees[scanuserid]['p5_count'] = count
                total_asisten += count
        
        total_verifications = total_mandor + total_asisten
        verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
        
        print(f"  Total KERANI (PM): {total_kerani}")
        print(f"  Total MANDOR (P1): {total_mandor}")
        print(f"  Total ASISTEN (P5): {total_asisten}")
        print(f"  Verification Rate: {verification_rate:.2f}%")
        
        # Special check for Erly
        if div_id == '16':  # Air Kundo
            erly_data = employees.get('4771')
            if erly_data:
                print(f"  ⭐ Erly (4771): {erly_data['pm_count']} PM transactions")
                print(f"     Expected: 123 - {'✓ MATCH' if erly_data['pm_count'] == 123 else '✗ MISMATCH'}")
        
        return {
            'div_id': div_id,
            'div_name': div_name,
            'employees': employees,
            'totals': {
                'kerani': total_kerani,
                'mandor': total_mandor,
                'asisten': total_asisten,
                'verifications': total_verifications,
                'verification_rate': verification_rate
            }
        }
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def create_correct_excel_report(division_results, output_dir="reports"):
    """Create correct Excel report"""
    print("\nCreating corrected Excel report...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"corrected_ffb_report_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        
        # Summary sheet
        summary_data = []
        for result in division_results:
            if result:
                totals = result['totals']
                summary_data.append({
                    'Division': result['div_name'],
                    'Total_KERANI_PM': totals['kerani'],
                    'Total_MANDOR_P1': totals['mandor'],
                    'Total_ASISTEN_P5': totals['asisten'],
                    'Total_Verifications': totals['verifications'],
                    'Verification_Rate': f"{totals['verification_rate']:.2f}%"
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detail sheets per division
        for result in division_results:
            if not result:
                continue
                
            div_name = result['div_name']
            employees = result['employees']
            totals = result['totals']
            
            detail_data = []
            
            # Add employee data
            for emp_id, emp_data in employees.items():
                # KERANI row
                if emp_data['pm_count'] > 0:
                    contribution = (emp_data['pm_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'KERANI',
                        'Conductor': 0,
                        'Assistant': 0,
                        'Manager': 0,
                        'Bunch_Counter': emp_data['pm_count'],
                        'Contribution_Pct': f"{contribution:.2f}%"
                    })
                
                # MANDOR row
                if emp_data['p1_count'] > 0:
                    contribution = (emp_data['p1_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'MANDOR',
                        'Conductor': emp_data['p1_count'],
                        'Assistant': 0,
                        'Manager': 0,
                        'Bunch_Counter': 0,
                        'Contribution_Pct': f"{contribution:.2f}%"
                    })
                
                # ASISTEN row
                if emp_data['p5_count'] > 0:
                    contribution = (emp_data['p5_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': emp_id,
                        'Role': 'ASISTEN',
                        'Conductor': 0,
                        'Assistant': emp_data['p5_count'],
                        'Manager': 0,
                        'Bunch_Counter': 0,
                        'Contribution_Pct': f"{contribution:.2f}%"
                    })
            
            # Add summary rows
            detail_data.append({
                'Division': '',
                'Scanner_User': f'Total KERANI: {totals["kerani"]}',
                'Scanner_User_ID': f'Total Verifications: {totals["verifications"]}',
                'Role': f'Verification Rate: {totals["verification_rate"]:.2f}%',
                'Conductor': '',
                'Assistant': '',
                'Manager': '',
                'Bunch_Counter': '',
                'Contribution_Pct': ''
            })
            
            detail_df = pd.DataFrame(detail_data)
            sheet_name = div_name.replace('/', '_').replace('\\', '_')[:31]
            detail_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Report saved: {filepath}")
    return filepath

def main():
    """Main function"""
    print("CREATING CORRECTED FFB REPORT")
    print("="*50)
    print("Using exact query logic without status filter")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("Database connection failed!")
            return
        
        print("Database connected successfully")
        
        # Get employee mapping
        emp_mapping = get_employee_name_mapping(connector)
        print(f"Loaded {len(emp_mapping)} employee mappings")
        
        # Target divisions
        divisions = [
            {'div_id': '15', 'div_name': 'Air Batu'},
            {'div_id': '16', 'div_name': 'Air Kundo'},
            {'div_id': '17', 'div_name': 'Air Hijau'}
        ]
        
        division_results = []
        
        for div in divisions:
            result = analyze_division_correct(connector, emp_mapping, div['div_id'], div['div_name'])
            if result:
                division_results.append(result)
        
        if division_results:
            report_path = create_correct_excel_report(division_results)
            print(f"\n✓ Corrected report created: {report_path}")
            
            # Verify Erly result
            for result in division_results:
                if result['div_name'] == 'Air Kundo':
                    erly_data = result['employees'].get('4771')
                    if erly_data:
                        print(f"\n🎯 VERIFICATION:")
                        print(f"Erly (4771) PM transactions: {erly_data['pm_count']}")
                        print(f"Expected: 123")
                        print(f"Status: {'✅ CORRECT' if erly_data['pm_count'] == 123 else '❌ INCORRECT'}")
        else:
            print("No data found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
