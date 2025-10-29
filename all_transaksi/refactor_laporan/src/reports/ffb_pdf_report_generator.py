#!/usr/bin/env python3
"""
Template-based PDF Report Generator for FFB Scanner Verification Analysis
Exact match with template_exact_match.json specification
"""

from reportlab.lib.pagesizes import A4, landscape
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
        self.template_data = self.load_template()

    def load_template(self):
        """Load template configuration from JSON file"""
        template_path = "analisis_database/template_laporan/verifikasi_transaksi_mandor_kerani_asisten/template_exact_match.json"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)
        else:
            print(f"Template file not found: {template_path}")
            return None

    def setup_custom_styles(self):
        """Setup custom styles based on template specification"""
        # Main title style
        self.title_style = ParagraphStyle(
            'MainTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )

        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER
        )

        # Table header style
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.white,
            spaceAfter=0
        )

        # Normal text style for explanations
        self.normal_style = ParagraphStyle(
            'NormalText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT
        )

        # Bold text style
        self.bold_style = ParagraphStyle(
            'BoldText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
    
    def create_template_report(self, analysis_results, start_date, end_date, output_dir, filename=None):
        """Create PDF report matching exact template specification"""
        if not filename:
            month_name = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B")
            year = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Laporan_Kinerja_Kerani_Mandor_Asisten_{month_name}_{year}_{timestamp}.pdf"

        filepath = os.path.join(output_dir, filename)

        # Landscape format per template
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # Header section
        story.extend(self.create_template_header(start_date, end_date, analysis_results))

        # Main table per template specification
        table_data = self.create_template_table_data(analysis_results)
        story.append(table_data)
        story.append(Spacer(1, 12))

        # Explanations section
        story.extend(self.create_explanations_section())

        # Footer
        story.extend(self.create_footer())

        doc.build(story)
        return filepath

    def create_template_header(self, start_date, end_date, analysis_results):
        """Create header section matching template"""
        story = []

        # Company name
        company_title = Paragraph("PT. REBINMAS JAYA", self.title_style)
        story.append(company_title)
        story.append(Spacer(1, 6))

        # System subtitle
        subtitle = Paragraph("SISTEM MONITORING TRANSAKSI FFB", self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 6))

        # Report title
        report_title = Paragraph("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN", self.title_style)
        story.append(report_title)
        story.append(Spacer(1, 8))

        # Period
        period_text = f"Periode: {start_date} - {end_date}"
        period = Paragraph(period_text, self.normal_style)
        story.append(period)
        story.append(Spacer(1, 6))

        # Summary box
        total_estates = len(set(r.get('estate', '') for r in analysis_results))
        total_divisions = len(set(f"{r.get('estate', '')}-{r.get('division', '')}" for r in analysis_results))
        summary_text = f"<b>RINGKASAN ANALISIS:</b> {total_estates} Estate • {total_divisions} Divisi • Analisis Transaksi Real-time • Verifikasi Otomatis"
        summary = Paragraph(summary_text, self.normal_style)
        story.append(summary)
        story.append(Spacer(1, 12))

        return story

    def create_template_table_data(self, analysis_results):
        """Create main table matching template structure"""
        # Process data according to template logic
        processed_data = self.process_template_data(analysis_results)

        # Define headers matching template
        headers = [
            "ESTATE",
            "DIVISI",
            "KARYAWAN",
            "ROLE",
            "JUMLAH<br/>TRANSAKSI",
            "PERSENTASE<br/>TERVERIFIKASI",
            "KETERANGAN<br/>PERBEDAAN"
        ]

        # Column widths matching template
        column_widths = [90, 90, 140, 70, 80, 110, 120]

        # Build table data
        table_data = [headers]

        for row_data in processed_data:
            table_data.append(row_data)

        # Create table
        table = Table(table_data, colWidths=column_widths, repeatRows=1)

        # Apply table styles
        styles = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),

            # Border
            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            # Alignment for specific columns
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),  # Transaction count and percentage columns
            ('ALIGN', (6, 1), (6, -1), 'LEFT'),    # Differences column
        ]

        # Apply conditional formatting for different roles
        self.apply_role_formatting(table, processed_data, styles)

        table.setStyle(TableStyle(styles))
        return table

    def process_template_data(self, analysis_results):
        """Process analysis results to match template structure"""
        # Group data by estate and division
        grouped_data = {}

        for result in analysis_results:
            estate = result.get('estate', '')
            division = result.get('division', '')

            key = f"{estate}-{division}"
            if key not in grouped_data:
                grouped_data[key] = {
                    'estate': estate,
                    'division': division,
                    'employees': []
                }
            grouped_data[key]['employees'].append(result)

        # Build table data
        table_rows = []
        grand_totals = {'total_kerani': 0, 'verified_kerani': 0}

        for key, group in grouped_data.items():
            # Add division summary
            div_totals = self.calculate_division_totals(group['employees'])
            table_rows.append(self.create_division_summary_row(group, div_totals))

            # Add employee rows
            for emp in group['employees']:
                row = self.create_employee_row(emp)
                if row:
                    table_rows.append(row)

            # Add separator
            table_rows.append(self.create_separator_row())

            # Update grand totals
            grand_totals['total_kerani'] += div_totals.get('total_kerani', 0)
            grand_totals['verified_kerani'] += div_totals.get('verified_kerani', 0)

        # Add grand total row
        table_rows.append(self.create_grand_total_row(grand_totals))

        return table_rows

    def calculate_division_totals(self, employees):
        """Calculate totals for a division"""
        totals = {
            'total_kerani': 0,
            'verified_kerani': 0,
            'differences_count': 0
        }

        for emp in employees:
            if emp.get('role') == 'Kerani':
                totals['total_kerani'] += emp.get('total_transactions', 0)
                totals['verified_kerani'] += emp.get('verified_count', 0)
                totals['differences_count'] += emp.get('differences_count', 0)

        return totals

    def create_division_summary_row(self, group, totals):
        """Create division summary row"""
        div_name = group['division']
        estate_name = group['estate']

        verification_rate = 0
        if totals['total_kerani'] > 0:
            verification_rate = (totals['verified_kerani'] / totals['total_kerani']) * 100

        return [
            estate_name,
            f"== {div_name} TOTAL ==",
            "",  # Empty employee column
            "SUMMARY",
            str(totals['total_kerani']),
            f"{verification_rate:.2f}% ({totals['verified_kerani']})",
            ""
        ]

    def create_employee_row(self, employee):
        """Create individual employee row"""
        role = employee.get('role', '')
        name = employee.get('employee_name', '')
        estate = employee.get('estate', '')
        division = employee.get('division', '')

        total_trans = employee.get('total_transactions', 0)

        if role == 'Kerani':
            verified = employee.get('verified_count', 0)
            verification_rate = (verified / total_trans * 100) if total_trans > 0 else 0
            differences = employee.get('differences_count', 0)
            diff_percentage = (differences / verified * 100) if verified > 0 else 0

            return [
                estate,
                division,
                name,
                "KERANI",
                str(total_trans),
                f"{verification_rate:.2f}% ({verified})",
                f"{differences} perbedaan ({diff_percentage:.1f}%)"
            ]
        elif role in ['Mandor', 'Asisten']:
            contribution = employee.get('contribution_percentage', 0)
            return [
                estate,
                division,
                name,
                role.upper(),
                str(total_trans),
                f"{contribution:.2f}%",
                ""
            ]

        return None

    def create_separator_row(self):
        """Create separator row"""
        return ["", "", "", "", "", "", ""]

    def create_grand_total_row(self, grand_totals):
        """Create grand total row"""
        verification_rate = 0
        if grand_totals['total_kerani'] > 0:
            verification_rate = (grand_totals['verified_kerani'] / grand_totals['total_kerani']) * 100

        return [
            "",
            "=== GRAND TOTAL ===",
            "",
            "",
            str(grand_totals['total_kerani']),
            f"{verification_rate:.2f}% ({grand_totals['verified_kerani']})",
            ""
        ]

    def apply_role_formatting(self, table, processed_data, styles):
        """Apply conditional formatting based on template specifications"""
        for i, row in enumerate(processed_data, 1):  # Skip header row
            if i >= len(processed_data) + 1:
                break

            # Skip separator rows
            if all(cell == "" for cell in row):
                styles.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#EDF2F7')))
                continue

            role = row[3] if len(row) > 3 else ""

            if role == "SUMMARY":
                # Division summary formatting
                styles.extend([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#4299E1')),
                    ('TEXTCOLOR', (0, i), (-1, i), colors.white),
                    ('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'),
                ])
            elif role == "KERANI":
                # Kerani formatting
                styles.extend([
                    ('BACKGROUND', (0, i), (3, i), colors.HexColor('#FFF5F5')),
                    ('BACKGROUND', (6, i), (6, i), colors.HexColor('#FED7D7')),
                    ('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#E53E3E')),
                    ('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#C53030')),
                ])
            elif role == "MANDOR":
                # Mandor formatting
                styles.extend([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4')),
                    ('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#38A169')),
                ])
            elif role == "ASISTEN":
                # Asisten formatting
                styles.extend([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0F9FF')),
                    ('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#3182CE')),
                ])
            elif "GRAND TOTAL" in str(row[1]):
                # Grand total formatting
                styles.extend([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#4299E1')),
                    ('TEXTCOLOR', (0, i), (-1, i), colors.white),
                    ('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'),
                ])

    def create_explanations_section(self):
        """Create explanations section matching template"""
        story = []

        story.append(Spacer(1, 12))

        # Main explanations
        main_exp = [
            "KERANI: % transaksi yang sudah diverifikasi (ada duplikat TRANSNO dengan P1/P5) dari total yang ia buat. Angka dalam kurung menunjukkan jumlah transaksi terverifikasi.",
            "MANDOR/ASISTEN: % transaksi yang ia buat per total Kerani di divisi tersebut (warna hijau).",
            "SUMMARY: % verifikasi keseluruhan divisi (Total Transaksi Kerani Terverifikasi / Total Transaksi Kerani). Angka dalam kurung menunjukkan jumlah transaksi Kerani yang terverifikasi.",
            "GRAND TOTAL: % verifikasi keseluruhan untuk semua estate yang dipilih (Total Semua Transaksi Kerani Terverifikasi / Total Semua Transaksi Kerani). Angka dalam kurung menunjukkan jumlah total transaksi Kerani yang terverifikasi.",
            "Jumlah Transaksi: Untuk SUMMARY dan GRAND TOTAL hanya menghitung transaksi Kerani (tanpa Asisten/Mandor)."
        ]

        for exp in main_exp:
            p = Paragraph(exp, self.normal_style)
            story.append(p)

        story.append(Spacer(1, 8))

        # Differences explanations
        diff_exp = [
            "Metodologi: Untuk setiap transaksi KERANI yang terverifikasi, sistem menghitung jumlah field yang berbeda antara input KERANI dan input MANDOR/ASISTEN.",
            "Field yang dibandingkan: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT.",
            "Format: 'X perbedaan (Y%)' dimana Y% = (X perbedaan / Jumlah transaksi terverifikasi) × 100.",
            "Interpretasi: Semakin banyak perbedaan, semakin besar kemungkinan ada ketidakakuratan dalam input data."
        ]

        for exp in diff_exp:
            p = Paragraph(exp, self.normal_style)
            story.append(p)

        return story

    def create_footer(self):
        """Create footer section"""
        story = []

        story.append(Spacer(1, 12))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Laporan dibuat pada: {timestamp}"
        footer = Paragraph(footer_text, self.normal_style)
        story.append(footer)

        system_text = "Sistem Analisis Real-time | PT. Rebinmas Jaya"
        system = Paragraph(system_text, self.normal_style)
        story.append(system)

        return story
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