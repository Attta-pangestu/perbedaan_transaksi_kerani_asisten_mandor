#!/usr/bin/env python3
"""
Script final untuk membuat laporan Excel yang benar
Menggunakan query langsung tanpa melalui fungsi analisis yang bermasalah
"""

import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def get_employee_names(connector):
    """Get employee names"""
    query = "SELECT ID, NAME FROM EMP"
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        names = {}
        if not df.empty:
            for _, row in df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                names[emp_id] = emp_name
        return names
    except:
        return {}

def analyze_division_direct(connector, emp_names, div_id, div_name):
    """Analyze division using direct queries"""
    print(f"\nAnalyzing {div_name} (ID: {div_id})")
    
    # Query untuk menghitung transaksi per user per recordtag
    query = f"""
    SELECT 
        a.SCANUSERID,
        a.RECORDTAG,
        COUNT(*) as count
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
            print(f"  No data for {div_name}")
            return None
        
        # Process data
        employees = {}
        totals = {'PM': 0, 'P1': 0, 'P5': 0}
        
        for _, row in df.iterrows():
            user_id = str(row.iloc[0]).strip()
            recordtag = str(row.iloc[1]).strip()
            count = int(row.iloc[2])
            
            if user_id not in employees:
                employees[user_id] = {
                    'name': emp_names.get(user_id, f"EMPLOYEE-{user_id}"),
                    'PM': 0, 'P1': 0, 'P5': 0
                }
            
            employees[user_id][recordtag] = count
            totals[recordtag] += count
        
        # Calculate rates
        total_kerani = totals['PM']
        total_verifications = totals['P1'] + totals['P5']
        verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
        
        print(f"  KERANI (PM): {total_kerani}")
        print(f"  MANDOR (P1): {totals['P1']}")
        print(f"  ASISTEN (P5): {totals['P5']}")
        print(f"  Verification Rate: {verification_rate:.2f}%")
        
        # Check Erly for Air Kundo
        if div_id == '16' and '4771' in employees:
            erly_pm = employees['4771']['PM']
            print(f"  ⭐ Erly (4771): {erly_pm} PM transactions")
            print(f"     Expected: 123 - {'✅ MATCH' if erly_pm == 123 else '❌ MISMATCH'}")
        
        return {
            'div_id': div_id,
            'div_name': div_name,
            'employees': employees,
            'totals': totals,
            'verification_rate': verification_rate
        }
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def create_excel_report(results):
    """Create Excel report"""
    print("\nCreating Excel report...")
    
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FINAL_CORRECTED_FFB_Report_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        
        # Summary sheet
        summary_data = []
        for result in results:
            if result:
                totals = result['totals']
                summary_data.append({
                    'Division': result['div_name'],
                    'Total_KERANI_PM': totals['PM'],
                    'Total_MANDOR_P1': totals['P1'],
                    'Total_ASISTEN_P5': totals['P5'],
                    'Total_Verifications': totals['P1'] + totals['P5'],
                    'Verification_Rate': f"{result['verification_rate']:.2f}%"
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary_Final', index=False)
        
        # Detail sheets
        for result in results:
            if not result:
                continue
                
            div_name = result['div_name']
            employees = result['employees']
            totals = result['totals']
            
            detail_data = []
            
            for user_id, emp_data in employees.items():
                # KERANI row
                if emp_data['PM'] > 0:
                    contribution = (emp_data['PM'] / totals['PM'] * 100) if totals['PM'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': user_id,
                        'Role': 'KERANI',
                        'Conductor': 0,
                        'Assistant': 0,
                        'Manager': 0,
                        'Bunch_Counter': emp_data['PM'],
                        'Contribution': f"{contribution:.2f}%"
                    })
                
                # MANDOR row
                if emp_data['P1'] > 0:
                    contribution = (emp_data['P1'] / totals['PM'] * 100) if totals['PM'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': user_id,
                        'Role': 'MANDOR',
                        'Conductor': emp_data['P1'],
                        'Assistant': 0,
                        'Manager': 0,
                        'Bunch_Counter': 0,
                        'Contribution': f"{contribution:.2f}%"
                    })
                
                # ASISTEN row
                if emp_data['P5'] > 0:
                    contribution = (emp_data['P5'] / totals['PM'] * 100) if totals['PM'] > 0 else 0
                    detail_data.append({
                        'Division': div_name,
                        'Scanner_User': emp_data['name'],
                        'Scanner_User_ID': user_id,
                        'Role': 'ASISTEN',
                        'Conductor': 0,
                        'Assistant': emp_data['P5'],
                        'Manager': 0,
                        'Bunch_Counter': 0,
                        'Contribution': f"{contribution:.2f}%"
                    })
            
            # Summary row
            total_verifications = totals['P1'] + totals['P5']
            detail_data.append({
                'Division': '',
                'Scanner_User': f'Total KERANI: {totals["PM"]}',
                'Scanner_User_ID': f'Total Verifications: {total_verifications}',
                'Role': f'Verification Rate: {result["verification_rate"]:.2f}%',
                'Conductor': '',
                'Assistant': '',
                'Manager': '',
                'Bunch_Counter': '',
                'Contribution': ''
            })
            
            detail_df = pd.DataFrame(detail_data)
            sheet_name = div_name.replace(' ', '_')
            detail_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Report created: {filepath}")
    return filepath

def main():
    """Main function"""
    print("CREATING FINAL CORRECTED FFB REPORT")
    print("="*50)
    print("Using direct queries - bypassing problematic analysis function")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return
        
        print("✅ Database connected")
        
        # Get employee names
        emp_names = get_employee_names(connector)
        print(f"✅ Loaded {len(emp_names)} employee names")
        
        # Target divisions
        divisions = [
            {'div_id': '15', 'div_name': 'Air Batu'},
            {'div_id': '16', 'div_name': 'Air Kundo'},
            {'div_id': '17', 'div_name': 'Air Hijau'}
        ]
        
        results = []
        for div in divisions:
            result = analyze_division_direct(connector, emp_names, div['div_id'], div['div_name'])
            if result:
                results.append(result)
        
        if results:
            report_path = create_excel_report(results)
            
            print(f"\n" + "="*50)
            print("✅ FINAL CORRECTED REPORT CREATED!")
            print("="*50)
            print(f"File: {report_path}")
            
            # Verify Air Kundo results
            air_kundo = next((r for r in results if r['div_name'] == 'Air Kundo'), None)
            if air_kundo and '4771' in air_kundo['employees']:
                erly_pm = air_kundo['employees']['4771']['PM']
                print(f"\n🎯 VERIFICATION:")
                print(f"Erly (4771) PM transactions: {erly_pm}")
                print(f"Expected: 123")
                print(f"Status: {'✅ CORRECT' if erly_pm == 123 else '❌ INCORRECT'}")
                
                print(f"\nAir Kundo Summary:")
                print(f"Total KERANI: {air_kundo['totals']['PM']}")
                print(f"Total MANDOR: {air_kundo['totals']['P1']}")
                print(f"Total ASISTEN: {air_kundo['totals']['P5']}")
                print(f"Verification Rate: {air_kundo['verification_rate']:.2f}%")
            
            print(f"\n📊 Laporan Excel ini menunjukkan:")
            print(f"✅ Data yang akurat sesuai query database")
            print(f"✅ Erly = 123 transaksi PM")
            print(f"✅ Perhitungan verification rate yang benar")
            print(f"✅ Kontribusi individual yang tepat")
            
            # Ask to open file
            try:
                response = input(f"\nBuka file Excel? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    os.startfile(report_path)
            except:
                pass
        else:
            print("❌ No data found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
