#!/usr/bin/env python3
"""
Test complete system - Analysis Engine + PDF Reports
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

def test_analysis_engine():
    """Test the correct analysis engine"""
    print("TESTING ANALYSIS ENGINE")
    print("="*40)
    
    try:
        from correct_analysis_engine import analyze_multiple_divisions, get_divisions_list
        from firebird_connector import FirebirdConnector
        
        DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
        
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connected")
        
        # Test Air Kundo analysis
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 29)
        
        divisions = [{'div_id': '16', 'div_name': 'Air Kundo'}]
        
        results = analyze_multiple_divisions(connector, divisions, start_date, end_date)
        
        if results and len(results) > 0:
            result = results[0]
            employees = result['employees']
            
            if '4771' in employees:
                erly_pm = employees['4771']['PM']
                print(f"✅ Erly (4771): {erly_pm} PM transactions")
                
                if erly_pm == 123:
                    print("✅ Analysis engine working correctly!")
                    return True
                else:
                    print(f"❌ Expected 123, got {erly_pm}")
                    return False
            else:
                print("❌ Erly not found in results")
                return False
        else:
            print("❌ No results from analysis")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analysis engine: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation"""
    print("\nTESTING PDF GENERATION")
    print("="*40)
    
    try:
        from pdf_report_generator import FFBReportGenerator
        
        # Sample data
        sample_data = [
            {
                'div_name': 'Air Kundo',
                'div_id': '16',
                'employees': {
                    '4771': {'name': 'ERLY ( MARDIAH )', 'PM': 123, 'P1': 0, 'P5': 0, 'pm_contribution': 46.59},
                    '183': {'name': 'DJULI DARTA', 'PM': 141, 'P1': 0, 'P5': 0, 'pm_contribution': 53.41}
                },
                'verification_stats': {
                    'total_kerani_transactions': 264,
                    'total_mandor_transactions': 14,
                    'total_asisten_transactions': 2,
                    'total_verifications': 16,
                    'verification_rate': 6.06
                },
                'start_date': '2025-04-01',
                'end_date': '2025-04-29'
            }
        ]
        
        generator = FFBReportGenerator()
        reports = generator.generate_complete_report(sample_data, "test_reports")
        
        print(f"✅ PDF Summary: {reports['summary_report']}")
        print(f"✅ PDF Details: {len(reports['division_reports'])} files")
        
        # Check if files exist
        if os.path.exists(reports['summary_report']):
            print("✅ PDF generation working correctly!")
            return True
        else:
            print("❌ PDF files not created")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test complete workflow"""
    print("\nTESTING COMPLETE WORKFLOW")
    print("="*40)
    
    try:
        from correct_analysis_engine import analyze_multiple_divisions
        from pdf_report_generator import FFBReportGenerator
        from firebird_connector import FirebirdConnector
        import pandas as pd
        
        DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
        
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return False
        
        # Analyze Air Kundo
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 29)
        
        divisions = [{'div_id': '16', 'div_name': 'Air Kundo'}]
        
        print("Running analysis...")
        results = analyze_multiple_divisions(connector, divisions, start_date, end_date)
        
        if not results:
            print("❌ No analysis results")
            return False
        
        print("Generating Excel report...")
        # Generate Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"test_reports/Excel_Test_{timestamp}.xlsx"
        
        os.makedirs("test_reports", exist_ok=True)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            summary_data = []
            for result in results:
                stats = result['verification_stats']
                summary_data.append({
                    'Division': result['div_name'],
                    'Total_KERANI': stats['total_kerani_transactions'],
                    'Verification_Rate': f"{stats['verification_rate']:.2f}%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print("Generating PDF reports...")
        # Generate PDF
        generator = FFBReportGenerator()
        pdf_reports = generator.generate_complete_report(results, "test_reports")
        
        # Verify Erly result
        result = results[0]
        if '4771' in result['employees']:
            erly_pm = result['employees']['4771']['PM']
            print(f"✅ Final verification - Erly: {erly_pm} transactions")
            
            if erly_pm == 123:
                print("✅ COMPLETE WORKFLOW SUCCESS!")
                print(f"✅ Excel: {excel_path}")
                print(f"✅ PDF Summary: {pdf_reports['summary_report']}")
                print(f"✅ PDF Details: {len(pdf_reports['division_reports'])} files")
                return True
            else:
                print(f"❌ Erly shows {erly_pm}, expected 123")
                return False
        else:
            print("❌ Erly not found in final results")
            return False
            
    except Exception as e:
        print(f"❌ Error in complete workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("FFB SCANNER SYSTEM COMPLETE TEST")
    print("="*50)
    print("Testing all components:")
    print("1. Analysis Engine (correct logic)")
    print("2. PDF Report Generation")
    print("3. Complete Workflow")
    print("="*50)
    
    # Test 1: Analysis Engine
    analysis_ok = test_analysis_engine()
    
    # Test 2: PDF Generation
    pdf_ok = test_pdf_generation()
    
    # Test 3: Complete Workflow
    workflow_ok = test_complete_workflow()
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Analysis Engine: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
    print(f"PDF Generation: {'✅ PASS' if pdf_ok else '❌ FAIL'}")
    print(f"Complete Workflow: {'✅ PASS' if workflow_ok else '❌ FAIL'}")
    
    if analysis_ok and pdf_ok and workflow_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("System is ready for use.")
        print("\nTo run GUI: python run_simple_gui.py")
        print("GUI will now show Erly = 123 and generate PDF reports")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the errors above.")
    
    return analysis_ok and pdf_ok and workflow_ok

if __name__ == "__main__":
    main()
