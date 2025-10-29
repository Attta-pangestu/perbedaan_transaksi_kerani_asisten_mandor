#!/usr/bin/env python3
"""
PDF Report Generation Module for FFB Analysis System
Handles professional PDF report creation with enhanced styling and layout.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


class PDFReportGenerator:
    """
    Generates professional PDF reports for FFB analysis results.
    Supports multi-estate reporting with enhanced styling and data visualization.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize PDF report generator.

        Args:
            output_dir: Directory for generated reports
        """
        self.output_dir = output_dir
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"Created output directory: {self.output_dir}")

    def create_multi_estate_report(self, analysis_results: Dict, start_date, end_date) -> str:
        """
        Create comprehensive PDF report for multi-estate analysis.

        Args:
            analysis_results: Results from FFBAnalyzer.analyze_multiple_estates
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            Path to generated PDF file
        """
        if not analysis_results or '_summary' not in analysis_results:
            raise ValueError("Invalid analysis results provided")

        summary = analysis_results['_summary']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        period = f"{start_date.strftime('%B_%Y')}"
        filename = f"Laporan_Kinerja_Multi-Estate_{period}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document with landscape orientation
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        story = []

        # Add company header
        self._add_company_header(story, styles)

        # Add main title
        self._add_main_title(story, styles, start_date, end_date, summary)

        # Add summary statistics
        self._add_summary_box(story, styles, summary)

        # Add detailed analysis tables
        self._add_detailed_tables(story, styles, analysis_results)

        # Add explanations
        self._add_explanations(story, styles)

        # Add footer
        self._add_footer(story, styles)

        # Build PDF
        try:
            doc.build(story)
            print(f"PDF report generated: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise

    def _add_company_header(self, story: List, styles):
        """Add company header with logo to the story."""
        try:
            # Try to find logo in assets folder
            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "assets",
                "logo_rebinmas.jpeg"
            )

            if os.path.exists(logo_path):
                logo = Image(logo_path, width=72, height=72)  # 1 inch = 72 points
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 10))
            else:
                print("Logo not found, skipping logo")
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")

        # Company header
        header_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2E4057'),
            alignment=1,  # Center
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )

        company_header = Paragraph(
            "<b>PT. REBINMAS JAYA</b><br/>SISTEM MONITORING TRANSAKSI FFB",
            header_style
        )
        story.append(company_header)
        story.append(Spacer(1, 10))

    def _add_main_title(self, story: List, styles, start_date, end_date, summary: Dict):
        """Add main title and period information."""
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=8,
            spaceBefore=10,
            alignment=1,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=25,
            alignment=1,
            fontName='Helvetica'
        )

        title = Paragraph("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN - MULTI-ESTATE", title_style)
        subtitle = Paragraph(
            f"Periode: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}",
            subtitle_style
        )

        story.append(title)
        story.append(subtitle)

        # Add summary statistics box
        summary_style = ParagraphStyle(
            'SummaryBox',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2D3748'),
            alignment=1,
            spaceAfter=20,
            leftIndent=50,
            rightIndent=50
        )

        summary_text = f"""<b>RINGKASAN ANALISIS:</b> {summary.get('estates_analyzed', 0)} Estate • {summary.get('total_divisions', 0)} Divisi •
        Analisis Transaksi Real-time • Verifikasi Otomatis"""

        summary_box = Paragraph(summary_text, summary_style)
        story.append(summary_box)
        story.append(Spacer(1, 15))

    def _add_summary_box(self, story: List, styles, summary: Dict):
        """Add summary statistics box."""
        # Grand totals calculation
        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)

        summary_table_data = [
            [
                Paragraph('METRIK', ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold', textColor=colors.white)),
                Paragraph('JUMLAH', ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold', textColor=colors.white)),
                Paragraph('CATATAN', ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold', textColor=colors.white))
            ],
            [
                Paragraph('Total Estate', cell_style),
                Paragraph(str(summary.get('estates_analyzed', 0)), cell_style),
                Paragraph(f"Estate berhasil diproses dari {summary.get('successful_estates', 0)}", cell_style)
            ],
            [
                Paragraph('Total Divisi', cell_style),
                Paragraph(str(summary.get('total_divisions', 0)), cell_style),
                Paragraph('Semua divisi dari estate yang berhasil', cell_style)
            ],
            [
                Paragraph('Total Transaksi Kerani', cell_style),
                Paragraph(str(summary.get('kerani_total', 0)), cell_style),
                Paragraph('Total transaksi yang dibuat oleh Kerani', cell_style)
            ],
            [
                Paragraph('Total Transaksi Terverifikasi', cell_style),
                Paragraph(str(summary.get('verifikasi_total', 0)), cell_style),
                Paragraph('Transaksi dengan duplikasi yang terverifikasi', cell_style)
            ],
            [
                Paragraph('Tingkat Verifikasi', cell_style),
                Paragraph(f"{summary.get('verification_rate', 0):.2f}%", cell_style),
                Paragraph('Persentase keberhasilan verifikasi data', cell_style)
            ]
        ]

        summary_table = Table(summary_table_data, colWidths=[150, 80, 200])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 15))

    def _add_detailed_tables(self, story: List, styles, analysis_results: Dict):
        """Add detailed analysis tables for each estate."""
        # Create enhanced header with white text
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )

        table_data = []
        grand_kerani = 0
        grand_mandor = 0
        grand_asisten = 0
        grand_kerani_verified = 0
        grand_kerani_differences = 0

        # Add table header
        table_data.append([
            Paragraph('ESTATE', header_style),
            Paragraph('DIVISI', header_style),
            Paragraph('KARYAWAN', header_style),
            Paragraph('ROLE', header_style),
            Paragraph('JUMLAH<br/>TRANSAKSI', header_style),
            Paragraph('PERSENTASE<br/>TERVERIFIKASI', header_style),
            Paragraph('KETERANGAN<br/>PERBEDAAN', header_style)
        ])

        # Process each estate
        for estate_name, estate_result in analysis_results.items():
            if estate_name.startswith('_'):  # Skip summary keys
                continue

            if 'divisions' not in estate_result:
                continue

            # Add estate totals
            estate_summary = self._calculate_estate_summary(estate_result['divisions'])
            if estate_summary:
                table_data.append([
                    Paragraph(estate_name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold')),
                    Paragraph('== ESTATE TOTAL ==', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold')),
                    Paragraph('SUMMARY', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold')),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(str(estate_summary['total_kerani']), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(f"{estate_summary['verification_rate']:.2f}%", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1))
                ])

                grand_kerani += estate_summary['total_kerani']
                grand_mandor += estate_summary['total_mandor']
                grand_asisten += estate_summary['total_asisten']
                grand_kerani_verified += estate_summary['total_verified']
                grand_kerani_differences += estate_summary['total_differences']

            # Add employee details
            for division in estate_result['divisions']:
                if 'employee_details' not in division:
                    continue

                employee_details = division['employee_details']

                # Group by role for better organization
                kerani_employees = [(name, data) for name, data in employee_details.items() if data.get('kerani', 0) > 0]
                mandor_employees = [(name, data) for name, data in employee_details.items() if data.get('mandor', 0) > 0]
                asisten_employees = [(name, data) for name, data in employee_details.items() if data.get('asisten', 0) > 0]

                # Add Kerani rows
                for name, data in sorted(kerani_employees, key=lambda x: x[0]):
                    verified_pct = (data.get('kerani_verified', 0) / data['kerani'] * 100) if data['kerani'] > 0 else 0
                    differences_pct = (data.get('kerani_differences', 0) / data.get('kerani_verified', 1) * 100) if data.get('kerani_verified', 0) > 0 else 0

                    table_data.append([
                        Paragraph(estate_name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(division.get('division', ''), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=0)),
                        Paragraph('KERANI', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#E53E3E'), fontName='Helvetica-Bold')),
                        Paragraph(str(data['kerani']), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(f"{verified_pct:.2f}% ({data.get('kerani_verified', 0)})", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#E53E3E'), fontName='Helvetica-Bold')),
                        Paragraph(f"{data.get('kerani_differences', 0)} perbedaan ({differences_pct:.1f}%)", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#C53030'), fontName='Helvetica-Bold'))
                    ])

                # Add Mandor rows
                for name, data in sorted(mandor_employees, key=lambda x: x[0]):
                    mandor_pct = (data['mandor'] / estate_summary['total_kerani'] * 100) if estate_summary['total_kerani'] > 0 else 0

                    table_data.append([
                        Paragraph(estate_name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(division.get('division', ''), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=0)),
                        Paragraph('MANDOR', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#38A169'), fontName='Helvetica-Bold')),
                        Paragraph(str(data['mandor']), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(f"{mandor_pct:.2f}%", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#38A169'), fontName='Helvetica-Bold')),
                        Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1))
                    ])

                # Add Asisten rows
                for name, data in sorted(asisten_employees, key=lambda x: x[0]):
                    asisten_pct = (data['asisten'] / estate_summary['total_kerani'] * 100) if estate_summary['total_kerani'] > 0 else 0

                    table_data.append([
                        Paragraph(estate_name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(division.get('division', ''), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(name, ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=0)),
                        Paragraph('ASISTEN', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#3182CE'), fontName='Helvetica-Bold')),
                        Paragraph(str(data['asisten']), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                        Paragraph(f"{asisten_pct:.2f}%", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#3182CE'), fontName='Helvetica-Bold')),
                        Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1))
                    ])

                # Add separator
                table_data.append([
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1))
                ])

        # Add grand total row
        grand_verification_rate = (grand_kerani_verified / grand_kerani * 100) if grand_kerani > 0 else 0

        table_data.append([
            Paragraph('=== GRAND TOTAL ===', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold')),
            Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
            Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
            Paragraph('', ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
            Paragraph(str(grand_kerani), ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
            Paragraph(f"{grand_verification_rate:.2f}% ({grand_kerani_verified})", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)),
            Paragraph(f"{grand_kerani_differences} perbedaan", ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1))
        ])

        # Create table with proper styling
        table = Table(table_data, repeatRows=1, colWidths=[90, 90, 140, 70, 80, 110, 120])

        # Enhanced table styling
        style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Grid styling - only for body rows
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white])
        ])

        # Enhanced row highlighting
        for i, row in enumerate(table_data):
            if i == 0:  # Skip header row
                continue

            # Check row content for styling
            row_text = str(row[2]) if len(row) > 2 else ""  # Employee column

            # Highlight SUMMARY and GRAND TOTAL rows
            if 'TOTAL' in row_text or 'SUMMARY' in row_text:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#4299E1'))
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
                style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
                style.add('FONTSIZE', (0, i), (-1, i), 9)
                style.add('TOPPADDING', (0, i), (-1, i), 10)
                style.add('BOTTOMPADDING', (0, i), (-1, i), 10)

            # Highlight role-specific rows
            elif len(row) > 3:  # Has role column
                role_text = str(row[3]) if len(row) > 3 else ""

                if 'KERANI' in role_text:
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#E53E3E'))
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')
                    if len(row) > 6:  # Has keterangan column
                        style.add('BACKGROUND', (6, i), (6, i), colors.HexColor('#FED7D7'))
                        style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#C53030'))

                elif 'MANDOR' in role_text:
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4'))
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#38A169'))
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')

                elif 'ASISTEN' in role_text:
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0F9FF'))
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#3182CE'))
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')

        table.setStyle(style)
        story.append(table)
        story.append(Spacer(1, 20))

    def _calculate_estate_summary(self, divisions: List[Dict]) -> Optional[Dict]:
        """Calculate summary statistics for all divisions in an estate."""
        if not divisions:
            return None

        total_kerani = sum(div.get('kerani_total', 0) for div in divisions)
        total_mandor = sum(div.get('mandor_total', 0) for div in divisions)
        total_asisten = sum(div.get('asisten_total', 0) for div in divisions)
        total_verified = sum(div.get('verifikasi_total', 0) for div in divisions)
        total_differences = sum(
            emp_data.get('kerani_differences', 0)
            for div in divisions
            for emp_data in div.get('employee_details', {}).values()
        )

        verification_rate = (total_verified / total_kerani * 100) if total_kerani > 0 else 0

        return {
            'total_kerani': total_kerani,
            'total_mandor': total_mandor,
            'total_asisten': total_asisten,
            'total_verified': total_verified,
            'total_differences': total_differences,
            'verification_rate': verification_rate
        }

    def _add_explanations(self, story: List, styles):
        """Add explanation section to the report."""
        explanation_title_style = ParagraphStyle(
            'ExplanationTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2D3748'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        explanation_style = ParagraphStyle(
            'Explanation',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#4A5568'),
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20,
            bulletIndent=10,
            alignment=0
        )

        # Main explanation section
        explanation_title = Paragraph("PENJELASAN LAPORAN KINERJA", explanation_title_style)
        story.append(explanation_title)

        explanations = [
            "<b>KERANI:</b> % transaksi yang sudah diverifikasi (ada duplikat TRANSNO dengan P1/P5) dari total yang ia buat. Angka dalam kurung menunjukkan jumlah transaksi terverifikasi.",
            "<b>MANDOR/ASISTEN:</b> % transaksi yang ia buat per total Kerani di divisi tersebut.",
            "<b>SUMMARY:</b> % verifikasi keseluruhan divisi (Total Transaksi Kerani Terverifikasi / Total Transaksi Kerani).",
            "<b>GRAND TOTAL:</b> % verifikasi keseluruhan untuk semua estate yang dipilih (Total Semua Transaksi Kerani Terverifikasi / Total Semua Transaksi Kerani).",
            "<b>Jumlah Transaksi:</b> Untuk SUMMARY dan GRAND TOTAL hanya menghitung transaksi Kerani (tanpa Asisten/Mandor)."
        ]

        for explanation_text in explanations:
            explanation_para = Paragraph(f"• {explanation_text}", explanation_style)
            story.append(explanation_para)

        story.append(Spacer(1, 15))

        # Differences explanation
        differences_title = Paragraph("⚠️ KETERANGAN PERBEDAAN INPUT (INDIKATOR KINERJA)", explanation_title_style)
        story.append(differences_title)

        differences_explanations = [
            "<b>Metodologi:</b> Untuk setiap transaksi KERANI yang terverifikasi, sistem menghitung jumlah field yang berbeda antara input KERANI dan input MANDOR/ASISTEN.",
            "<b>Field yang dibandingkan:</b> RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT.",
            "<b>Format:</b> 'X perbedaan (Y%)' dimana Y% = (X perbedaan / Jumlah transaksi terverifikasi) × 100.",
            "<b>Interpretasi:</b> Semakin banyak perbedaan, semakin besar kemungkinan ada ketidakakuratan dalam input data."
        ]

        for diff_text in differences_explanations:
            diff_para = Paragraph(f"• {diff_text}", explanation_style)
            story.append(diff_para)

        story.append(Spacer(1, 20))

    def _add_footer(self, story: List, styles):
        """Add footer with generation information."""
        story.append(Spacer(1, 20))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=1,
            spaceBefore=10
        )

        footer_text = f"""📅 Laporan dibuat pada: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} |
        🔄 Sistem Analisis Real-time | 🏢 PT. Rebinmas Jaya"""

        footer = Paragraph(footer_text, footer_style)
        story.append(footer)


class ReportConfig:
    """
    Configuration for report generation.
    """

    DEFAULT_LOGO_PATH = "assets/logo_rebinmas.jpeg"
    DEFAULT_OUTPUT_DIR = "reports"

    def __init__(self, output_dir: str = None, logo_path: str = None):
        """
        Initialize report configuration.

        Args:
            output_dir: Custom output directory
            logo_path: Custom logo path
        """
        self.output_dir = output_dir or self.DEFAULT_OUTPUT_DIR
        self.logo_path = logo_path or self.DEFAULT_LOGO_PATH