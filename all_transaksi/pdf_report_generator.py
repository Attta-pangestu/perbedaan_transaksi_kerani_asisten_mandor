#!/usr/bin/env python3
"""
Professional PDF Report Generator untuk FFB Scanner Analysis
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class FFBReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkred
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10
        )
    
    def create_header_footer(self, canvas, doc):
        """Create header and footer for each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(inch, doc.height + inch - 0.5*inch, 
                         "FFB Scanner Verification Analysis Report")
        canvas.drawRightString(doc.width + inch, doc.height + inch - 0.5*inch,
                              f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredText(doc.width/2 + inch, 0.5*inch, 
                              f"Page {doc.page}")
        
        canvas.restoreState()
    
    def generate_division_summary_report(self, analysis_results, output_path):
        """Generate summary report for all divisions"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("FFB Scanner Verification Analysis", self.title_style)
        story.append(title)
        
        subtitle = Paragraph("Division Summary Report", self.subtitle_style)
        story.append(subtitle)
        
        # Period info
        if analysis_results:
            start_date = analysis_results[0].get('start_date', 'N/A')
            end_date = analysis_results[0].get('end_date', 'N/A')
            period_text = f"Analysis Period: {start_date} to {end_date}"
            period_para = Paragraph(period_text, self.normal_style)
            story.append(period_para)
            story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [
            ['Division', 'Total KERANI', 'Total MANDOR', 'Total ASISTEN', 'Verification Rate']
        ]
        
        for result in analysis_results:
            div_name = result['div_name']
            stats = result['verification_stats']
            
            summary_data.append([
                div_name,
                str(stats['total_kerani_transactions']),
                str(stats['total_mandor_transactions']),
                str(stats['total_asisten_transactions']),
                f"{stats['verification_rate']:.2f}%"
            ])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Key findings
        findings_title = Paragraph("Key Findings", self.section_style)
        story.append(findings_title)
        
        findings = []
        for result in analysis_results:
            div_name = result['div_name']
            stats = result['verification_stats']
            
            findings.append(f"• {div_name}: {stats['verification_rate']:.2f}% verification rate")
            
            # Special note for Air Kundo and Erly
            if div_name == 'Air Kundo' and '4771' in result['employees']:
                erly_pm = result['employees']['4771']['PM']
                findings.append(f"  - Erly (ID: 4771): {erly_pm} PM transactions")
        
        for finding in findings:
            finding_para = Paragraph(finding, self.normal_style)
            story.append(finding_para)
        
        doc.build(story, onFirstPage=self.create_header_footer, 
                 onLaterPages=self.create_header_footer)
        
        return output_path
    
    def generate_division_detail_report(self, division_result, output_path):
        """Generate detailed report for a single division"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        div_name = division_result['div_name']
        employees = division_result['employees']
        stats = division_result['verification_stats']
        
        # Title
        title = Paragraph(f"FFB Scanner Analysis - {div_name}", self.title_style)
        story.append(title)
        
        # Period
        start_date = division_result.get('start_date', 'N/A')
        end_date = division_result.get('end_date', 'N/A')
        period_text = f"Period: {start_date} to {end_date}"
        period_para = Paragraph(period_text, self.normal_style)
        story.append(period_para)
        story.append(Spacer(1, 20))
        
        # Division summary
        summary_title = Paragraph("Division Summary", self.section_style)
        story.append(summary_title)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total KERANI Transactions', str(stats['total_kerani_transactions'])],
            ['Total MANDOR Transactions', str(stats['total_mandor_transactions'])],
            ['Total ASISTEN Transactions', str(stats['total_asisten_transactions'])],
            ['Total Verifications', str(stats['total_verifications'])],
            ['Verification Rate', f"{stats['verification_rate']:.2f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Employee details by role
        self.add_employee_section(story, employees, 'KERANI', 'PM')
        self.add_employee_section(story, employees, 'MANDOR', 'P1')
        self.add_employee_section(story, employees, 'ASISTEN', 'P5')
        
        doc.build(story, onFirstPage=self.create_header_footer, 
                 onLaterPages=self.create_header_footer)
        
        return output_path
    
    def add_employee_section(self, story, employees, role_name, transaction_type):
        """Add employee section for specific role"""
        # Filter employees by role
        role_employees = []
        for emp_id, emp_data in employees.items():
            if emp_data[transaction_type] > 0:
                role_employees.append((emp_id, emp_data))
        
        if not role_employees:
            return
        
        # Section title
        section_title = Paragraph(f"{role_name} Details", self.section_style)
        story.append(section_title)
        
        # Employee table
        table_data = [
            ['Employee Name', 'ID', 'Transactions', 'Contribution %']
        ]
        
        for emp_id, emp_data in role_employees:
            contribution_key = f"{transaction_type.lower()}_contribution"
            contribution = emp_data.get(contribution_key, 0)
            
            table_data.append([
                emp_data['name'],
                emp_id,
                str(emp_data[transaction_type]),
                f"{contribution:.2f}%"
            ])
        
        employee_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
        employee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(employee_table)
        story.append(Spacer(1, 20))
    
    def generate_complete_report(self, analysis_results, output_dir="reports"):
        """Generate complete PDF report package"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate summary report
        summary_path = os.path.join(output_dir, f"FFB_Summary_Report_{timestamp}.pdf")
        self.generate_division_summary_report(analysis_results, summary_path)
        
        # Generate individual division reports
        division_reports = []
        for result in analysis_results:
            div_name = result['div_name'].replace(' ', '_').replace('/', '_')
            detail_path = os.path.join(output_dir, f"FFB_{div_name}_Detail_{timestamp}.pdf")
            self.generate_division_detail_report(result, detail_path)
            division_reports.append(detail_path)
        
        return {
            'summary_report': summary_path,
            'division_reports': division_reports,
            'timestamp': timestamp
        }

def test_pdf_generation():
    """Test PDF generation with sample data"""
    # Sample data for testing
    sample_data = [
        {
            'div_name': 'Air Kundo',
            'div_id': '16',
            'employees': {
                '4771': {'name': 'ERLY ( MARDIAH )', 'PM': 123, 'P1': 0, 'P5': 0, 'pm_contribution': 46.59},
                '183': {'name': 'DJULI DARTA', 'PM': 141, 'P1': 0, 'P5': 0, 'pm_contribution': 53.41},
                'XXX': {'name': 'SUHAYAT', 'PM': 0, 'P1': 14, 'P5': 0, 'p1_contribution': 5.30},
                'YYY': {'name': 'SURANTO', 'PM': 0, 'P1': 0, 'P5': 2, 'p5_contribution': 0.76}
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
    reports = generator.generate_complete_report(sample_data)
    
    print("PDF Reports generated:")
    print(f"Summary: {reports['summary_report']}")
    for report in reports['division_reports']:
        print(f"Detail: {report}")

if __name__ == "__main__":
    test_pdf_generation()
