#!/usr/bin/env python3
"""
Professional PDF Report Generator for FFB Scanner Verification Analysis
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime
import pandas as pd

class FFBPDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for professional formatting"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=15,
            spaceBefore=15,
            textColor=colors.darkred
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Table header style
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            spaceAfter=0
        )
    
    def create_division_report(self, analysis_results, output_dir, filename=None):
        """Create comprehensive division-level PDF report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"FFB_Division_Analysis_Report_{timestamp}.pdf"
        
        filepath = os.path.join(output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title page
        story.extend(self.create_title_page())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self.create_executive_summary(analysis_results))
        story.append(PageBreak())
        
        # Division overview
        story.extend(self.create_division_overview(analysis_results))
        story.append(PageBreak())
        
        # Detailed division analysis
        for result in analysis_results:
            story.extend(self.create_division_detail(result))
            story.append(PageBreak())
        
        # Employee role analysis
        story.extend(self.create_employee_role_analysis(analysis_results))
        story.append(PageBreak())
        
        # Verification statistics
        story.extend(self.create_verification_statistics(analysis_results))
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def create_title_page(self):
        """Create professional title page"""
        story = []
        
        # Main title
        title = Paragraph("Laporan Analisis Verifikasi FFB Scanner", self.title_style)
        story.append(title)
        story.append(Spacer(1, 2*inch))
        
        # Subtitle
        subtitle = Paragraph("Analisis Komprehensif Divisi dan Kinerja Karyawan", 
                           ParagraphStyle('Subtitle', parent=self.styles['Normal'], fontSize=14, alignment=TA_CENTER))
        story.append(subtitle)
        story.append(Spacer(1, 1*inch))
        
        # Report details
        details = [
            ["Jenis Laporan:", "Analisis Verifikasi FFB Scanner"],
            ["Tanggal Dibuat:", datetime.now().strftime("%d %B %Y")],
            ["Waktu Dibuat:", datetime.now().strftime("%H:%M:%S")],
            ["Periode Analisis:", "1-28 April 2025"],
            ["Database:", "PTRJ_P1A.FDB"],
        ]
        
        details_table = Table(details, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 2*inch))
        
        # Footer
        footer = Paragraph("Laporan ini dibuat secara otomatis oleh sistem analisis FFB Scanner.", 
                          ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
        story.append(footer)
        
        return story
    
    def create_executive_summary(self, analysis_results):
        """Create executive summary section"""
        story = []
        
        # Section header
        story.append(Paragraph("Ringkasan Eksekutif", self.section_style))
        
        # Calculate totals
        total_divisions = len(analysis_results)
        total_kerani = sum(result['totals']['kerani'] for result in analysis_results)
        total_mandor = sum(result['totals']['mandor'] for result in analysis_results)
        total_asisten = sum(result['totals']['asisten'] for result in analysis_results)
        total_verifications = sum(result['totals']['verifications'] for result in analysis_results)
        overall_verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
        
        # Summary text
        summary_text = f"""
        Laporan ini menyajikan analisis komprehensif aktivitas verifikasi FFB Scanner di {total_divisions} divisi 
        untuk periode 1-28 April 2025. Analisis ini memeriksa kinerja tiga peran karyawan utama: 
        KERANI (Penghitung Tandan), MANDOR (Konduktor), dan ASISTEN (Asisten).
        
        <b>Temuan Utama:</b>
        • Total transaksi KERANI: {total_kerani:,}
        • Total verifikasi MANDOR: {total_mandor:,}
        • Total verifikasi ASISTEN: {total_asisten:,}
        • Tingkat verifikasi keseluruhan: {overall_verification_rate:.2f}%
        • Total divisi yang dianalisis: {total_divisions}
        """
        
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [['Metrik', 'Jumlah', 'Persentase']]
        summary_data.append(['Total Transaksi KERANI', f"{total_kerani:,}", '100.00%'])
        summary_data.append(['Total Verifikasi MANDOR', f"{total_mandor:,}", f"{(total_mandor/total_kerani*100):.2f}%" if total_kerani > 0 else '0.00%'])
        summary_data.append(['Total Verifikasi ASISTEN', f"{total_asisten:,}", f"{(total_asisten/total_kerani*100):.2f}%" if total_kerani > 0 else '0.00%'])
        summary_data.append(['Total Verifikasi', f"{total_verifications:,}", f"{overall_verification_rate:.2f}%"])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(summary_table)
        
        return story
    
    def create_division_overview(self, analysis_results):
        """Create division overview section"""
        story = []
        
        story.append(Paragraph("Ringkasan Divisi", self.section_style))
        
        # Division summary table
        div_data = [['Divisi', 'KERANI', 'MANDOR', 'ASISTEN', 'Total Verifikasi', 'Tingkat Verifikasi']]
        
        for result in analysis_results:
            totals = result['totals']
            div_data.append([
                result['div_name'],
                f"{totals['kerani']:,}",
                f"{totals['mandor']:,}",
                f"{totals['asisten']:,}",
                f"{totals['verifications']:,}",
                f"{totals['verification_rate']:.2f}%"
            ])
        
        div_table = Table(div_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch, 1.5*inch])
        div_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(div_table)
        
        return story
    
    def create_division_detail(self, result):
        """Create detailed analysis for a specific division"""
        story = []
        
        div_name = result['div_name']
        totals = result['totals']
        employees = result['employees']
        
        # Division header
        story.append(Paragraph(f"Division: {div_name}", self.section_style))
        
        # Division summary
        summary_text = f"""
        <b>Division Summary:</b>
        • Total KERANI transactions: {totals['kerani']:,}
        • Total MANDOR verifications: {totals['mandor']:,}
        • Total ASISTEN verifications: {totals['asisten']:,}
        • Verification rate: {totals['verification_rate']:.2f}%
        • Number of employees: {len(employees)}
        """
        
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Employee breakdown by role
        story.append(Paragraph("Employee Breakdown by Role", self.subsection_style))
        
        # KERANI employees
        kerani_employees = [(emp_id, emp_data) for emp_id, emp_data in employees.items() if emp_data['pm_count'] > 0]
        if kerani_employees:
            story.append(Paragraph("KERANI (Bunch Counter) Employees:", self.normal_style))
            kerani_data = [['Employee ID', 'Employee Name', 'Transactions', 'Contribution %']]
            
            for emp_id, emp_data in kerani_employees:
                contribution = (emp_data['pm_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                kerani_data.append([
                    emp_id,
                    emp_data['name'],
                    f"{emp_data['pm_count']:,}",
                    f"{contribution:.2f}%"
                ])
            
            kerani_table = Table(kerani_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            kerani_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(kerani_table)
            story.append(Spacer(1, 15))
        
        # MANDOR employees
        mandor_employees = [(emp_id, emp_data) for emp_id, emp_data in employees.items() if emp_data['p1_count'] > 0]
        if mandor_employees:
            story.append(Paragraph("MANDOR (Conductor) Employees:", self.normal_style))
            mandor_data = [['Employee ID', 'Employee Name', 'Verifications', 'Contribution %']]
            
            for emp_id, emp_data in mandor_employees:
                contribution = (emp_data['p1_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                mandor_data.append([
                    emp_id,
                    emp_data['name'],
                    f"{emp_data['p1_count']:,}",
                    f"{contribution:.2f}%"
                ])
            
            mandor_table = Table(mandor_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            mandor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(mandor_table)
            story.append(Spacer(1, 15))
        
        # ASISTEN employees
        asisten_employees = [(emp_id, emp_data) for emp_id, emp_data in employees.items() if emp_data['p5_count'] > 0]
        if asisten_employees:
            story.append(Paragraph("ASISTEN (Assistant) Employees:", self.normal_style))
            asisten_data = [['Employee ID', 'Employee Name', 'Verifications', 'Contribution %']]
            
            for emp_id, emp_data in asisten_employees:
                contribution = (emp_data['p5_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                asisten_data.append([
                    emp_id,
                    emp_data['name'],
                    f"{emp_data['p5_count']:,}",
                    f"{contribution:.2f}%"
                ])
            
            asisten_table = Table(asisten_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            asisten_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(asisten_table)
        
        return story
    
    def create_employee_role_analysis(self, analysis_results):
        """Create employee role analysis section"""
        story = []
        
        story.append(Paragraph("Employee Role Analysis", self.section_style))
        
        # Collect all employees by role
        all_kerani = []
        all_mandor = []
        all_asisten = []
        
        for result in analysis_results:
            div_name = result['div_name']
            employees = result['employees']
            
            for emp_id, emp_data in employees.items():
                if emp_data['pm_count'] > 0:
                    all_kerani.append({
                        'division': div_name,
                        'emp_id': emp_id,
                        'name': emp_data['name'],
                        'transactions': emp_data['pm_count']
                    })
                
                if emp_data['p1_count'] > 0:
                    all_mandor.append({
                        'division': div_name,
                        'emp_id': emp_id,
                        'name': emp_data['name'],
                        'verifications': emp_data['p1_count']
                    })
                
                if emp_data['p5_count'] > 0:
                    all_asisten.append({
                        'division': div_name,
                        'emp_id': emp_id,
                        'name': emp_data['name'],
                        'verifications': emp_data['p5_count']
                    })
        
        # Top KERANI performers
        if all_kerani:
            story.append(Paragraph("Top KERANI (Bunch Counter) Performers", self.subsection_style))
            all_kerani.sort(key=lambda x: x['transactions'], reverse=True)
            
            kerani_data = [['Rank', 'Division', 'Employee ID', 'Employee Name', 'Transactions']]
            for i, emp in enumerate(all_kerani[:10], 1):  # Top 10
                kerani_data.append([
                    str(i),
                    emp['division'],
                    emp['emp_id'],
                    emp['name'],
                    f"{emp['transactions']:,}"
                ])
            
            kerani_table = Table(kerani_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 2*inch, 1*inch])
            kerani_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(kerani_table)
            story.append(Spacer(1, 20))
        
        # Top MANDOR performers
        if all_mandor:
            story.append(Paragraph("Top MANDOR (Conductor) Performers", self.subsection_style))
            all_mandor.sort(key=lambda x: x['verifications'], reverse=True)
            
            mandor_data = [['Rank', 'Division', 'Employee ID', 'Employee Name', 'Verifications']]
            for i, emp in enumerate(all_mandor[:10], 1):  # Top 10
                mandor_data.append([
                    str(i),
                    emp['division'],
                    emp['emp_id'],
                    emp['name'],
                    f"{emp['verifications']:,}"
                ])
            
            mandor_table = Table(mandor_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 2*inch, 1*inch])
            mandor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(mandor_table)
            story.append(Spacer(1, 20))
        
        # Top ASISTEN performers
        if all_asisten:
            story.append(Paragraph("Top ASISTEN (Assistant) Performers", self.subsection_style))
            all_asisten.sort(key=lambda x: x['verifications'], reverse=True)
            
            asisten_data = [['Rank', 'Division', 'Employee ID', 'Employee Name', 'Verifications']]
            for i, emp in enumerate(all_asisten[:10], 1):  # Top 10
                asisten_data.append([
                    str(i),
                    emp['division'],
                    emp['emp_id'],
                    emp['name'],
                    f"{emp['verifications']:,}"
                ])
            
            asisten_table = Table(asisten_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 2*inch, 1*inch])
            asisten_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(asisten_table)
        
        return story
    
    def create_verification_statistics(self, analysis_results):
        """Create verification statistics section"""
        story = []
        
        story.append(Paragraph("Verification Statistics", self.section_style))
        
        # Calculate statistics
        total_kerani = sum(result['totals']['kerani'] for result in analysis_results)
        total_mandor = sum(result['totals']['mandor'] for result in analysis_results)
        total_asisten = sum(result['totals']['asisten'] for result in analysis_results)
        total_verifications = sum(result['totals']['verifications'] for result in analysis_results)
        
        # Verification rates by division
        story.append(Paragraph("Verification Rates by Division", self.subsection_style))
        
        rates_data = [['Division', 'KERANI', 'MANDOR', 'ASISTEN', 'Total Verifications', 'Verification Rate']]
        for result in analysis_results:
            totals = result['totals']
            rates_data.append([
                result['div_name'],
                f"{totals['kerani']:,}",
                f"{totals['mandor']:,}",
                f"{totals['asisten']:,}",
                f"{totals['verifications']:,}",
                f"{totals['verification_rate']:.2f}%"
            ])
        
        rates_table = Table(rates_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch, 1.5*inch])
        rates_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(rates_table)
        story.append(Spacer(1, 20))
        
        # Summary statistics
        story.append(Paragraph("Overall Statistics", self.subsection_style))
        
        overall_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
        mandor_rate = (total_mandor / total_kerani * 100) if total_kerani > 0 else 0
        asisten_rate = (total_asisten / total_kerani * 100) if total_kerani > 0 else 0
        
        stats_text = f"""
        <b>Overall Performance Summary:</b>
        • Total KERANI transactions: {total_kerani:,}
        • Total MANDOR verifications: {total_mandor:,} ({mandor_rate:.2f}% of KERANI transactions)
        • Total ASISTEN verifications: {total_asisten:,} ({asisten_rate:.2f}% of KERANI transactions)
        • Total verifications: {total_verifications:,} ({overall_rate:.2f}% of KERANI transactions)
        • Average verification rate across divisions: {sum(r['totals']['verification_rate'] for r in analysis_results) / len(analysis_results):.2f}%
        """
        
        story.append(Paragraph(stats_text, self.normal_style))
        
        return story

def generate_ffb_pdf_report(analysis_results, output_dir, filename=None):
    """Main function to generate FFB PDF report"""
    generator = FFBPDFReportGenerator()
    return generator.create_division_report(analysis_results, output_dir, filename)

if __name__ == "__main__":
    # Test the PDF generator
    print("FFB PDF Report Generator")
    print("This module provides professional PDF report generation for FFB Scanner Verification Analysis") 