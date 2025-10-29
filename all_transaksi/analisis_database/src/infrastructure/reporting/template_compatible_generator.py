"""
Template-based PDF Report Generator for FFB Analysis System
Matches exact format from gui_multi_estate_ffb_analysis.py entrypoint
"""

import os
import sys
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics

# Add parent directory to path to import original template-based generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
try:
    from ffb_pdf_report_generator import FFBPDFReportGenerator
except ImportError:
    print("Warning: Could not import original FFBPDFReportGenerator, using fallback")
    FFBPDFReportGenerator = None


class TemplateCompatiblePDFGenerator:
    """
    Template-compatible PDF generator that matches exact format from gui_multi_estate_ffb_analysis.py
    """

    def __init__(self):
        """Initialize template-compatible PDF generator"""
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles matching gui_multi_estate_ffb_analysis.py"""
        # Company Header style - matching original
        self.company_header_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2E4057'),
            alignment=1,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )

        # Title style - matching original
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=8,
            spaceBefore=10,
            alignment=1,
            fontName='Helvetica-Bold'
        )

        # Subtitle style - matching original
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=25,
            alignment=1,
            fontName='Helvetica'
        )

        # Summary style - matching original
        self.summary_style = ParagraphStyle(
            'SummaryBox',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2D3748'),
            alignment=1,
            spaceAfter=20,
            leftIndent=50,
            rightIndent=50
        )

        # Cell styles - matching original
        self.cell_style = ParagraphStyle('CellStyle', parent=self.styles['Normal'], fontSize=8, alignment=1)
        self.cell_style_left = ParagraphStyle('CellStyleLeft', parent=self.styles['Normal'], fontSize=8, alignment=0)

        # Explanation styles - matching original
        self.explanation_title_style = ParagraphStyle(
            'ExplanationTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2D3748'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        self.explanation_style = ParagraphStyle(
            'Explanation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#4A5568'),
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20,
            bulletIndent=10,
            alignment=0
        )

        # Footer style - matching original
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=1,
            spaceBefore=10
        )

    def create_template_compatible_report(self, analysis_result: AnalysisResult,
                                         output_path: str) -> str:
        """
        Create PDF report matching exact format from gui_multi_estate_ffb_analysis.py

        :param analysis_result: Analysis result data
        :param output_path: Output file path
        :return: Path to generated PDF file
        """
        try:
            # Convert AnalysisResult to the format expected by original system
            all_results = self.convert_to_original_format(analysis_result)

            # Create PDF using exact same logic as original
            return self.create_pdf_report_original(all_results, analysis_result, output_path)

        except Exception as e:
            print(f"Error creating template-compatible report: {e}")
            raise

    def convert_to_original_format(self, analysis_result: AnalysisResult) -> List[Dict[str, Any]]:
        """
        Convert AnalysisResult to format expected by original gui_multi_estate_ffb_analysis.py
        """
        all_results = []

        for division in analysis_result.get_division_summaries():
            # Create result dictionary matching original format
            result = {
                'estate': analysis_result.estate_name,
                'division': division.division_name,
                'kerani_total': 0,
                'mandor_total': 0,
                'asisten_total': 0,
                'verifikasi_total': 0,
                'verification_rate': 0,
                'employee_details': {}
            }

            # Process employees
            for employee in division.get_employee_metrics():
                emp_id = str(employee.employee_id)
                role = employee.role

                # Map roles to original format
                if role in ['Kerani', 'PM']:
                    result['employee_details'][emp_id] = {
                        'name': employee.employee_name,
                        'kerani': employee.total_transactions,
                        'kerani_verified': getattr(employee, 'verified_transactions', 0),
                        'kerani_differences': getattr(employee, 'differences_count', 0),
                        'mandor': 0,
                        'asisten': 0
                    }
                    result['kerani_total'] += employee.total_transactions
                    result['verifikasi_total'] += getattr(employee, 'verified_transactions', 0)

                elif role in ['Mandor', 'P5']:
                    if emp_id not in result['employee_details']:
                        result['employee_details'][emp_id] = {
                            'name': employee.employee_name,
                            'kerani': 0,
                            'kerani_verified': 0,
                            'kerani_differences': 0,
                            'mandor': employee.total_transactions,
                            'asisten': 0
                        }
                    else:
                        result['employee_details'][emp_id]['mandor'] = employee.total_transactions
                    result['mandor_total'] += employee.total_transactions

                elif role in ['Asisten', 'P1']:
                    if emp_id not in result['employee_details']:
                        result['employee_details'][emp_id] = {
                            'name': employee.employee_name,
                            'kerani': 0,
                            'kerani_verified': 0,
                            'kerani_differences': 0,
                            'mandor': 0,
                            'asisten': employee.total_transactions
                        }
                    else:
                        result['employee_details'][emp_id]['asisten'] = employee.total_transactions
                    result['asisten_total'] += employee.total_transactions

            # Calculate verification rate
            if result['kerani_total'] > 0:
                result['verification_rate'] = (result['verifikasi_total'] / result['kerani_total']) * 100

            all_results.append(result)

        return all_results

    def create_pdf_report_original(self, all_results: List[Dict[str, Any]],
                                  analysis_result: AnalysisResult,
                                  filepath: str) -> str:
        """
        Create PDF report using exact same logic as gui_multi_estate_ffb_analysis.py
        """
        start_date = analysis_result.start_date
        end_date = analysis_result.end_date

        # Create PDF document with LANDSCAPE orientation and custom margins
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )
        story = []

        # Company Header with Logo - matching original
        try:
            logo_path = r"D:\Gawean Rebinmas\Monitoring Database\Laporan_Ifess_beda_transno\all_transaksi\assets\logo_rebinmas.jpeg"
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=72, height=72)  # 1 inch = 72 points
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 10))
        except Exception as e:
            print(f"Logo loading error: {e}")

        company_header = Paragraph(
            "<b>PT. REBINMAS JAYA</b><br/>SISTEM MONITORING TRANSAKSI FFB",
            self.company_header_style
        )
        story.append(company_header)
        story.append(Spacer(1, 10))

        # Main Title with Enhanced Styling - matching original
        title = Paragraph("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN", self.title_style)
        subtitle = Paragraph(f"Periode: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}", self.subtitle_style)

        story.append(title)
        story.append(subtitle)

        # Add summary statistics box - matching original
        total_estates = 1  # Single estate per analysis
        total_divisions = len(all_results)

        summary_text = f"""<b>RINGKASAN ANALISIS:</b> {total_estates} Estate • {total_divisions} Divisi •
        Analisis Transaksi Real-time • Verifikasi Otomatis"""

        summary_box = Paragraph(summary_text, self.summary_style)
        story.append(summary_box)
        story.append(Spacer(1, 15))

        # Create table data with enhanced columns - matching original logic
        table_data = []

        # Enhanced Header with White Text - matching original
        header_style = ParagraphStyle('HeaderStyle', parent=self.styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold', textColor=colors.white)
        header = [
            Paragraph('ESTATE', header_style),
            Paragraph('DIVISI', header_style),
            Paragraph('KARYAWAN', header_style),
            Paragraph('ROLE', header_style),
            Paragraph('JUMLAH<br/>TRANSAKSI', header_style),
            Paragraph('PERSENTASE<br/>TERVERIFIKASI', header_style),
            Paragraph('KETERANGAN<br/>PERBEDAAN', header_style)
        ]
        table_data.append(header)

        # Grand totals - matching original accumulation
        grand_kerani = 0
        grand_mandor = 0
        grand_asisten = 0
        grand_kerani_verified = 0

        # Process each result - matching original logic exactly
        for result in all_results:
            estate = result['estate']
            division = result['division']
            kerani_total = result['kerani_total']
            mandor_total = result['mandor_total']
            asisten_total = result['asisten_total']
            verifikasi_total = result['verifikasi_total']
            verification_rate = result['verification_rate']
            employee_details = result['employee_details']

            # Add division summary row - matching original
            total_kerani_only = kerani_total
            total_verified_kerani = verifikasi_total
            division_verification_rate = (total_verified_kerani / total_kerani_only * 100) if total_kerani_only > 0 else 0

            table_data.append([
                Paragraph(estate, self.cell_style),
                Paragraph(division, self.cell_style),
                Paragraph(f"== {division} TOTAL ==", self.cell_style),
                Paragraph('SUMMARY', self.cell_style),
                Paragraph(str(total_kerani_only), self.cell_style),
                Paragraph(f"{division_verification_rate:.2f}% ({total_verified_kerani})", self.cell_style),
                Paragraph("", self.cell_style)
            ])

            # Collect employee rows by role type - matching original
            kerani_rows = []
            mandor_rows = []
            asisten_rows = []

            for emp_id, emp_data in employee_details.items():
                # KERANI row - matching original logic
                if emp_data['kerani'] > 0:
                    kerani_verification_rate = (emp_data.get('kerani_verified', 0) / emp_data['kerani'] * 100) if emp_data['kerani'] > 0 else 0
                    verified_count = emp_data.get('kerani_verified', 0)
                    differences_count = emp_data.get('kerani_differences', 0)
                    percentage_text = f"{kerani_verification_rate:.2f}% ({verified_count})"
                    difference_percentage = (differences_count / verified_count * 100) if verified_count > 0 else 0
                    keterangan_text = f"{differences_count} perbedaan ({difference_percentage:.1f}%)"

                    kerani_rows.append([
                        Paragraph(estate, self.cell_style),
                        Paragraph(division, self.cell_style),
                        Paragraph(emp_data['name'], self.cell_style_left),
                        Paragraph('KERANI', self.cell_style),
                        Paragraph(str(emp_data['kerani']), self.cell_style),
                        Paragraph(percentage_text, self.cell_style),
                        Paragraph(keterangan_text, self.cell_style)
                    ])

                # MANDOR row - matching original logic
                if emp_data['mandor'] > 0:
                    mandor_percentage = (emp_data['mandor'] / kerani_total * 100) if kerani_total > 0 else 0
                    mandor_rows.append([
                        Paragraph(estate, self.cell_style),
                        Paragraph(division, self.cell_style),
                        Paragraph(emp_data['name'], self.cell_style_left),
                        Paragraph('MANDOR', self.cell_style),
                        Paragraph(str(emp_data['mandor']), self.cell_style),
                        Paragraph(f"{mandor_percentage:.2f}%", self.cell_style),
                        Paragraph("", self.cell_style)
                    ])

                # ASISTEN row - matching original logic
                if emp_data['asisten'] > 0:
                    asisten_percentage = (emp_data['asisten'] / kerani_total * 100) if kerani_total > 0 else 0
                    asisten_rows.append([
                        Paragraph(estate, self.cell_style),
                        Paragraph(division, self.cell_style),
                        Paragraph(emp_data['name'], self.cell_style_left),
                        Paragraph('ASISTEN', self.cell_style),
                        Paragraph(str(emp_data['asisten']), self.cell_style),
                        Paragraph(f"{asisten_percentage:.2f}%", self.cell_style),
                        Paragraph("", self.cell_style)
                    ])

            # Add rows in proper order: KERANI first, then MANDOR, then ASISTEN - matching original
            for row in kerani_rows:
                table_data.append(row)
            for row in mandor_rows:
                table_data.append(row)
            for row in asisten_rows:
                table_data.append(row)

            # Add separator - matching original
            table_data.append([
                Paragraph('', self.cell_style), Paragraph('', self.cell_style), Paragraph('', self.cell_style),
                Paragraph('', self.cell_style), Paragraph('', self.cell_style), Paragraph('', self.cell_style), Paragraph('', self.cell_style)
            ])

            # Add to grand totals - matching original
            grand_kerani += kerani_total
            grand_mandor += mandor_total
            grand_asisten += asisten_total
            grand_kerani_verified += verifikasi_total

        # Add grand total row - matching original
        grand_total_kerani_only = grand_kerani
        grand_total_verified_kerani = grand_kerani_verified
        grand_verification_rate = (grand_total_verified_kerani / grand_total_kerani_only * 100) if grand_total_kerani_only > 0 else 0

        table_data.append([
            Paragraph('=== GRAND TOTAL ===', self.cell_style),
            Paragraph('', self.cell_style),
            Paragraph('', self.cell_style),
            Paragraph('', self.cell_style),
            Paragraph(str(grand_total_kerani_only), self.cell_style),
            Paragraph(f"{grand_verification_rate:.2f}% ({grand_total_verified_kerani})", self.cell_style),
            Paragraph("", self.cell_style)
        ])

        # Create table with custom column widths - matching original
        col_widths = [90, 90, 140, 70, 80, 110, 120]
        table = Table(table_data, repeatRows=1, colWidths=col_widths)

        # Enhanced Modern Table Styling - matching original exactly
        style = TableStyle([
            # Header styling - clean header without boxes
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body styling with alternating colors
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Grid styling - ONLY for body rows (excluding header)
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),

            # Alternating row colors for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white]),
        ])

        # Enhanced row highlighting with modern color schemes - matching original exactly
        for i, row in enumerate(table_data):
            if i == 0:
                continue

            # Highlight SUMMARY and GRAND TOTAL rows with premium styling
            if 'TOTAL' in str(row[2]) or 'GRAND TOTAL' in str(row[0]):
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#4299E1'))
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
                style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
                style.add('FONTSIZE', (0, i), (-1, i), 9)
                style.add('TOPPADDING', (0, i), (-1, i), 10)
                style.add('BOTTOMPADDING', (0, i), (-1, i), 10)

            # Enhanced KERANI row styling
            elif len(row) > 3 and hasattr(row[3], 'text') and 'KERANI' in str(row[3].text):
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))
                style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#E53E3E'))
                style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')

                if len(row) > 6 and row[6]:
                    style.add('BACKGROUND', (6, i), (6, i), colors.HexColor('#FED7D7'))
                    style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#C53030'))
                    style.add('FONTNAME', (6, i), (6, i), 'Helvetica-Bold')

            # Enhanced MANDOR row styling
            elif len(row) > 3 and hasattr(row[3], 'text') and 'MANDOR' in str(row[3].text):
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4'))
                style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#38A169'))
                style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')

            # Enhanced ASISTEN row styling
            elif len(row) > 3 and hasattr(row[3], 'text') and 'ASISTEN' in str(row[3].text):
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0F9FF'))
                style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#3182CE'))
                style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')

            # Empty separator rows
            elif all(not str(cell).strip() for cell in row):
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#EDF2F7'))
                style.add('TOPPADDING', (0, i), (-1, i), 3)
                style.add('BOTTOMPADDING', (0, i), (-1, i), 3)

        table.setStyle(style)
        story.append(table)

        story.append(Spacer(1, 20))

        # Enhanced explanation section with modern styling - matching original
        explanation_title = Paragraph("PENJELASAN LAPORAN KINERJA", self.explanation_title_style)
        story.append(explanation_title)

        explanations = [
            "<b>KERANI:</b> % transaksi yang sudah diverifikasi (ada duplikat TRANSNO dengan P1/P5) dari total yang ia buat. Angka dalam kurung menunjukkan jumlah transaksi terverifikasi.",
            "<b>MANDOR/ASISTEN:</b> % transaksi yang ia buat per total Kerani di divisi tersebut (warna hijau).",
            "<b>SUMMARY:</b> % verifikasi keseluruhan divisi (Total Transaksi Kerani Terverifikasi / Total Transaksi Kerani). Angka dalam kurung menunjukkan jumlah transaksi Kerani yang terverifikasi.",
            "<b>GRAND TOTAL:</b> % verifikasi keseluruhan untuk semua estate yang dipilih (Total Semua Transaksi Kerani Terverifikasi / Total Semua Transaksi Kerani). Angka dalam kurung menunjukkan jumlah total transaksi Kerani yang terverifikasi.",
            "<b>Jumlah Transaksi:</b> Untuk SUMMARY dan GRAND TOTAL hanya menghitung transaksi Kerani (tanpa Asisten/Mandor)."
        ]

        for explanation_text in explanations:
            explanation_para = Paragraph(f"• {explanation_text}", self.explanation_style)
            story.append(explanation_para)

        story.append(Spacer(1, 15))

        # Enhanced differences explanation - matching original
        differences_title = Paragraph("⚠️ KETERANGAN PERBEDAAN INPUT (INDIKATOR KINERJA)", self.explanation_title_style)
        story.append(differences_title)

        differences_explanations = [
            "<b>Metodologi:</b> Untuk setiap transaksi KERANI yang terverifikasi, sistem menghitung jumlah field yang berbeda antara input KERANI dan input MANDOR/ASISTEN.",
            "<b>Field yang dibandingkan:</b> RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT.",
            "<b>Format:</b> 'X perbedaan (Y%)' dimana Y% = (X perbedaan / Jumlah transaksi terverifikasi) × 100.",
            "<b>Interpretasi:</b> Semakin banyak perbedaan, semakin besar kemungkinan ada ketidakakuratan dalam input data."
        ]

        for diff_text in differences_explanations:
            diff_para = Paragraph(f"• {diff_text}", self.explanation_style)
            story.append(diff_para)

        # Add footer with generation info - matching original
        story.append(Spacer(1, 20))

        footer_text = f"""📅 Laporan dibuat pada: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} |
        🔄 Sistem Analisis Real-time | 🏢 PT. Rebinmas Jaya"""

        footer = Paragraph(footer_text, self.footer_style)
        story.append(footer)

        # Build PDF
        doc.build(story)

        return filepath