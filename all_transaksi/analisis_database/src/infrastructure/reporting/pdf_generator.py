"""
PDF Report Generator
Professional PDF report generation for FFB Analysis System
"""

import os
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


class PDFReportGenerator:
    """
    Professional PDF report generator for FFB analysis results
    """

    def __init__(self):
        """Initialize PDF report generator"""
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

        # Small text style
        self.small_style = ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3
        )

    def create_comprehensive_report(self, analysis_result: AnalysisResult,
                                   output_path: str, include_charts: bool = True,
                                   include_details: bool = True) -> str:
        """
        Create comprehensive PDF report

        :param analysis_result: Analysis result data
        :param output_path: Output file path
        :param include_charts: Whether to include charts
        :param include_details: Whether to include detailed breakdowns
        :return: Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # Title page
        story.extend(self._create_title_page(analysis_result))
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(analysis_result))
        story.append(PageBreak())

        # Grand totals overview
        story.extend(self._create_grand_totals_section(analysis_result))
        story.append(PageBreak())

        # Estate breakdown
        story.extend(self._create_estate_breakdown_section(analysis_result))
        story.append(PageBreak())

        # Top performers
        story.extend(self._create_top_performers_section(analysis_result))
        story.append(PageBreak())

        # Quality issues
        if analysis_result.grand_differences > 0:
            story.extend(self._create_quality_issues_section(analysis_result))
            story.append(PageBreak())

        # Detailed division breakdown
        if include_details:
            for division_summary in analysis_result.get_division_summaries():
                story.extend(self._create_detailed_division_section(division_summary))
                story.append(PageBreak())

        # Methodology and explanations
        story.extend(self._create_methodology_section())
        story.append(PageBreak())

        # Appendices
        story.extend(self._create_appendices_section(analysis_result))

        # Build PDF
        doc.build(story)

        return output_path

    def create_summary_report(self, analysis_result: AnalysisResult,
                             output_path: str) -> str:
        """
        Create summary PDF report

        :param analysis_result: Analysis result data
        :param output_path: Output file path
        :return: Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # Title
        story.extend(self._create_title_page(analysis_result, summary=True))

        # Executive summary
        story.extend(self._create_executive_summary(analysis_result))

        # Grand totals table
        story.extend(self._create_grand_totals_table(analysis_result))

        # Top performers table
        story.extend(self._create_top_performers_table(analysis_result, limit=5))

        # Quality issues (if any)
        if analysis_result.grand_differences > 0:
            story.extend(self._create_quality_issues_table(analysis_result, limit=5))

        # Footer
        story.extend(self._create_footer())

        # Build PDF
        doc.build(story)

        return output_path

    def create_employee_performance_report(self, analysis_result: AnalysisResult,
                                          output_path: str) -> str:
        """
        Create employee performance focused report

        :param analysis_result: Analysis result data
        :param output_path: Output file path
        :return: Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # Title page
        story.extend(self._create_title_page(analysis_result, title="LAPORAN KINERJA KARYAWAN"))

        # Employee performance overview
        story.extend(self._create_employee_performance_overview(analysis_result))

        # Performance by role
        story.extend(self._create_performance_by_role_section(analysis_result))

        # Detailed employee breakdown
        story.extend(self._create_detailed_employee_section(analysis_result))

        # Performance recommendations
        story.extend(self._create_performance_recommendations_section(analysis_result))

        # Build PDF
        doc.build(story)

        return output_path

    def create_quality_assurance_report(self, analysis_result: AnalysisResult,
                                       output_path: str) -> str:
        """
        Create quality assurance focused report

        :param analysis_result: Analysis result data
        :param output_path: Output file path
        :return: Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # Title page
        story.extend(self._create_title_page(analysis_result, title="LAPORAN QUALITY ASSURANCE"))

        # Quality summary
        story.extend(self._create_quality_summary_section(analysis_result))

        # Detailed quality analysis
        story.extend(self._create_detailed_quality_analysis(analysis_result))

        # Problematic employees
        story.extend(self._create_problematic_employees_section(analysis_result))

        # Quality recommendations
        story.extend(self._create_quality_recommendations_section(analysis_result))

        # Build PDF
        doc.build(story)

        return output_path

    def _create_title_page(self, analysis_result: AnalysisResult,
                          summary: bool = False, title: Optional[str] = None) -> List:
        """Create title page elements"""
        elements = []

        # Add logo if available
        logo_path = self._get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=72, height=72)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 20))
            except Exception:
                pass

        # Company header
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )

        company_header = Paragraph(
            "<b>PT. REBINMAS JAYA</b><br/>SISTEM MONITORING TRANSAKSI FFB",
            company_style
        )
        elements.append(company_header)
        elements.append(Spacer(1, 20))

        # Main title
        if title:
            main_title = title
        else:
            main_title = "LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN" if not summary else "RINGKASAN LAPORAN KINERJA"

        title_para = Paragraph(main_title, self.title_style)
        elements.append(title_para)

        # Period
        period_style = ParagraphStyle(
            'PeriodStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4A5568'),
            alignment=TA_CENTER,
            spaceAfter=25
        )

        period_para = Paragraph(
            f"Periode: {analysis_result.start_date.strftime('%d %B %Y')} - {analysis_result.end_date.strftime('%d %B %Y')}",
            period_style
        )
        elements.append(period_para)

        # Analysis summary box
        summary_box = self._create_analysis_summary_box(analysis_result)
        elements.append(summary_box)
        elements.append(Spacer(1, 30))

        # Generation info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.small_style,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096')
        )

        info_para = Paragraph(
            f"Dibuat pada: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}<br/>"
            f"Versi Analisis: {analysis_result.analysis_version}",
            info_style
        )
        elements.append(info_para)

        return elements

    def _create_analysis_summary_box(self, analysis_result: AnalysisResult) -> Table:
        """Create analysis summary box"""
        summary_data = [
            ['<b>RINGKASAN ANALISIS</b>', ''],
            ['Estate Dianalisis', f"{len(analysis_result.analyzed_estates)} Estate"],
            ['Divisi Aktif', f"{analysis_result.total_divisions} Divisi"],
            ['Total Transaksi Kerani', f"{analysis_result.grand_kerani:,}"],
            ['Transaksi Terverifikasi', f"{analysis_result.grand_kerani_verified:,}"],
            ['Tingkat Verifikasi', f"{analysis_result.grand_verification_rate:.2f}%"],
            ['Total Perbedaan', f"{analysis_result.grand_differences:,}"],
            ['Durasi Analisis', f"{analysis_result.analysis_duration_seconds:.1f} detik"]
        ]

        summary_table = Table(summary_data, colWidths=[200, 150])
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        summary_table.setStyle(summary_style)

        return summary_table

    def _create_executive_summary(self, analysis_result: AnalysisResult) -> List:
        """Create executive summary section"""
        elements = []

        # Section title
        elements.append(Paragraph("EKSEKUTIF SUMMARY", self.section_style))

        # Key metrics
        metrics_data = [
            ['<b>METRIK UTAMA</b>', '<b>NILAI</b>', '<b>KETERANGAN</b>'],
            ['Total Estate', f"{len(analysis_result.analyzed_estates)}", 'Jumlah estate yang dianalisis'],
            ['Total Divisi', f"{analysis_result.total_divisions}", 'Jumlah divisi aktif'],
            ['Total Transaksi Kerani', f"{analysis_result.grand_kerani:,}", 'Semua transaksi yang dimasuk kerani'],
            ["Tingkat Verifikasi", f"{analysis_result.grand_verification_rate:.2f}%", f"{analysis_result.grand_kerani_verified:,} transaksi terverifikasi"],
            ['Total Perbedaan', f"{analysis_result.grand_differences:,}", 'Transaksi dengan perbedaan input data'],
            ['Tingkat Perbedaan', f"{analysis_result.grand_difference_rate:.2f}%", 'Persentase transaksi dengan perbedaan']
        ]

        metrics_table = Table(metrics_data, colWidths=[150, 100, 250])
        metrics_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        metrics_table.setStyle(metrics_style)
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))

        # Performance highlights
        top_performers = analysis_result.get_top_performers(3)
        if top_performers:
            elements.append(Paragraph("<b>PERFORMA TERBAIK</b>", self.subsection_style))

            performer_data = [['<b>Peringkat</b>', '<b>Nama Karyawan</b>', '<b>Tingkat Verifikasi</b>', '<b>Total Transaksi</b>']]
            for i, emp in enumerate(top_performers, 1):
                performer_data.append([
                    str(i),
                    emp.employee_name,
                    f"{emp.verification_rate:.1f}%",
                    f"{emp.kerani_transactions}"
                ])

            performer_table = Table(performer_data, colWidths=[60, 200, 100, 100])
            performer_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38A169')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0FFF4')),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ])
            performer_table.setStyle(performer_style)
            elements.append(performer_table)
            elements.append(Spacer(1, 15))

        # Quality concerns
        if analysis_result.grand_differences > 0:
            problematic = analysis_result.get_problematic_employees(3)
            if problematic:
                elements.append(Paragraph("<b>PERHATINAN QUALITY</b>", self.subsection_style))

                problem_data = [['<b>Nama Karyawan</b>', '<b>Total Perbedaan</b>', '<b>Tingkat Perbedaan</b>', '<b>Total Transaksi</b>']]
                for emp in problematic:
                    problem_data.append([
                        emp.employee_name,
                        f"{emp.kerani_differences}",
                        f"{emp.difference_rate:.1f}%",
                        f"{emp.kerani_transactions}"
                    ])

                problem_table = Table(problem_data, colWidths=[200, 100, 100, 100])
                problem_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53E3E')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF5F5')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ])
                problem_table.setStyle(problem_style)
                elements.append(problem_table)

        return elements

    def _create_grand_totals_section(self, analysis_result: AnalysisResult) -> List:
        """Create grand totals section"""
        elements = []

        elements.append(Paragraph("GRAND TOTALS SEMUA ESTATE", self.section_style))

        # Create comprehensive grand totals table
        totals_data = [
            ['<b>KATEGORI</b>', '<b>JUMLAH</b>', '<b>PERSENTASE</b>', '<b>KETERANGAN</b>'],
            ['Total Estate', f"{len(analysis_result.analyzed_estates)}", '-', 'Jumlah estate yang dianalisis'],
            ['Total Divisi', f"{analysis_result.total_divisions}", '-', 'Total divisi aktif'],
            ['Transaksi Kerani', f"{analysis_result.grand_kerani:,}", '100.0%', 'Semua transaksi input kerani'],
            ['Transaksi Terverifikasi', f"{analysis_result.grand_kerani_verified:,}", f"{analysis_result.grand_verification_rate:.2f}%", 'Transaksi yang sudah diverifikasi'],
            ['Transaksi Mandor', f"{analysis_result.grand_mandor:,}", '-', 'Transaksi verifikasi oleh mandor'],
            ['Transaksi Asisten', f"{analysis_result.grand_asisten:,}", '-', 'Transaksi verifikasi oleh asisten'],
            ['Total Perbedaan', f"{analysis_result.grand_differences:,}", f"{analysis_result.grand_difference_rate:.2f}%", 'Transaksi dengan perbedaan input data']
        ]

        totals_table = Table(totals_data, colWidths=[180, 120, 100, 200])
        totals_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])

        # Highlight important rows
        totals_style.add('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#EBF8FF'))  # Kerani
        totals_style.add('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F0FFF4'))  # Verified
        totals_style.add('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#FFF5F5'))  # Differences

        totals_table.setStyle(totals_style)
        elements.append(totals_table)

        return elements

    def _get_logo_path(self) -> str:
        """Get logo file path"""
        # Try multiple possible logo locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'logo_rebinmas.jpeg'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'assets', 'logo_rebinmas.jpeg'),
            r"D:\Gawean Rebinmas\Monitoring Database\Laporan_Ifess_beda_transno\all_transaksi\assets\logo_rebinmas.jpeg"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _create_footer(self) -> List:
        """Create footer elements"""
        elements = []

        footer_style = ParagraphStyle(
            'Footer',
            parent=self.small_style,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096'),
            spaceBefore=20
        )

        footer_text = f"""<br/><br/>
        <b>PT. REBINMAS JAYA</b><br/>
        Sistem Monitoring Transaksi FFB Multi-Estate<br/>
        Laporan dibuat: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}<br/>
        Generated by FFB Analysis System v1.0"""

        footer_para = Paragraph(footer_text, footer_style)
        elements.append(footer_para)

        return elements

    # Additional helper methods would continue here...
    # Due to length constraints, I'll include the key methods and note that additional methods follow similar patterns

    def _create_estate_breakdown_section(self, analysis_result: AnalysisResult) -> List:
        """Create estate breakdown section"""
        elements = []

        elements.append(Paragraph("BREAKDOWN PER ESTATE", self.section_style))

        # Group by estate
        estate_summaries = analysis_result.get_estate_summaries()

        for estate_name, divisions in estate_summaries.items():
            elements.append(Paragraph(f"<b>Estate: {estate_name}</b>", self.subsection_style))

            # Estate summary table
            estate_data = [['<b>Divisi</b>', '<b>Kerani</b>', '<b>Terverifikasi</b>', '<b>% Verifikasi</b>', '<b>Perbedaan</b>']]

            estate_kerani = sum(d.kerani_total for d in divisions)
            estate_verified = sum(d.verification_total for d in divisions)
            estate_differences = sum(d.difference_count for d in divisions)
            estate_rate = (estate_verified / estate_kerani * 100) if estate_kerani > 0 else 0

            estate_data.append([
                f"<b>{estate_name} TOTAL</b>",
                f"{estate_kerani:,}",
                f"{estate_verified:,}",
                f"{estate_rate:.2f}%",
                f"{estate_differences:,}"
            ])

            # Add individual divisions
            for division in divisions:
                estate_data.append([
                    division.division_name,
                    f"{division.kerani_total:,}",
                    f"{division.verification_total:,}",
                    f"{division.verification_rate:.2f}%",
                    f"{division.difference_count:,}"
                ])

            estate_table = Table(estate_data, colWidths=[150, 80, 80, 80, 80])
            estate_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5568')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ])

            # Highlight estate total row
            estate_style.add('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#EBF8FF'))
            estate_style.add('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold')

            estate_table.setStyle(estate_style)
            elements.append(estate_table)
            elements.append(Spacer(1, 15))

        return elements

    def _create_top_performers_section(self, analysis_result: AnalysisResult) -> List:
        """Create top performers section"""
        elements = []

        elements.append(Paragraph("TOP PERFORMERS", self.section_style))

        # Top Kerani by verification rate
        top_kerani = analysis_result.get_top_performers(10)
        if top_kerani:
            elements.append(Paragraph("<b>Kerani Terbaik (Berdasarkan Tingkat Verifikasi)</b>", self.subsection_style))

            kerani_data = [['<b>Peringkat</b>', '<b>Nama</b>', '<b>Estate</b>', '<b>Divisi</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>% Verifikasi</b>', '<b>Perbedaan</b>']]

            for i, emp in enumerate(top_kerani, 1):
                kerani_data.append([
                    str(i),
                    emp.employee_name,
                    emp.estate,
                    emp.division,
                    f"{emp.kerani_transactions}",
                    f"{emp.kerani_verified}",
                    f"{emp.verification_rate:.1f}%",
                    f"{emp.kerani_differences}"
                ])

            kerani_table = Table(kerani_data, colWidths=[40, 150, 80, 80, 60, 60, 60, 60])
            kerani_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38A169')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ])

            # Top 3 performers get special highlighting
            for i in range(min(3, len(top_kerani))):
                kerani_style.add('BACKGROUND', (0, i+1), (-1, i+1), colors.HexColor('#F0FFF4'))

            kerani_table.setStyle(kerani_style)
            elements.append(kerani_table)

        return elements

    def _create_quality_issues_section(self, analysis_result: AnalysisResult) -> List:
        """Create quality issues section"""
        elements = []

        elements.append(Paragraph("ANALISIS QUALITY DATA", self.section_style))

        # Get problematic employees
        problematic = analysis_result.get_problematic_employees(20)
        if problematic:
            elements.append(Paragraph(f"<b>Karyawan dengan Perbedaan Data ({len(problematic)} karyawan)</b>", self.subsection_style))

            problem_data = [['<b>Nama</b>', '<b>Estate</b>', '<b>Divisi</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>Perbedaan</b>', '<b>% Perbedaan</b>']]

            for emp in problematic:
                problem_data.append([
                    emp.employee_name,
                    emp.estate,
                    emp.division,
                    f"{emp.kerani_transactions}",
                    f"{emp.kerani_verified}",
                    f"{emp.kerani_differences}",
                    f"{emp.difference_rate:.1f}%"
                ])

            problem_table = Table(problem_data, colWidths=[150, 80, 80, 60, 60, 60, 60])
            problem_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53E3E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ])

            # Highlight high difference rates (>10%)
            for i, emp in enumerate(problematic, 1):
                if emp.difference_rate > 10:
                    problem_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))

            problem_table.setStyle(problem_style)
            elements.append(problem_table)

        return elements

    def _create_methodology_section(self) -> List:
        """Create methodology section"""
        elements = []

        elements.append(Paragraph("METODOLOGI ANALISIS", self.section_style))

        methodology_text = """
        <b>1. Pengumpulan Data</b><br/>
        Data transaksi diambil dari tabel bulanan FFBSCANNERDATA[MM] untuk setiap estate.
        Periode analisis mencakup semua transaksi dalam rentang tanggal yang ditentukan.

        <b>2. Verifikasi Transaksi</b><br/>
        Transaksi dianggap terverifikasi jika ada duplikasi TRANSNO dengan RECORDTAG berbeda:
        • PM (Kerani) + P1 (Asisten) atau P5 (Mandor) = Transaksi Terverifikasi
        • Prioritas: P1 (Asisten) > P5 (Mandor) jika keduanya ada

        <b>3. Filter Khusus (Mei 2025)</b><br/>
        Untuk transaksi pada bulan Mei 2025, diterapkan filter TRANSSTATUS = 704
        untuk transaksi Mandor/Asisten dalam perhitungan verifikasi.

        <b>4. Analisis Perbedaan</b><br/>
        Dihitung perbedaan pada 7 field utama: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH,
        LONGSTALKBCH, RATDMGBCH, dan LOOSEFRUIT. Setiap transaksi dihitung sebagai 1
        perbedaan jika ada field yang berbeda antara input Kerani dan verifikator.

        <b>5. Metrik Kinerja</b><br/>
        • Kerani: % verifikasi = (Terverifikasi / Total Dibuat) × 100<br/>
        • Mandor/Asisten: % kontribusi = (Total / Total Kerani) × 100<br/>
        • Quality Rate: % perbedaan = (Perbedaan / Terverifikasi) × 100
        """

        methodology_para = Paragraph(methodology_text, self.normal_style)
        elements.append(methodology_para)

        return elements

    def _create_appendices_section(self, analysis_result: AnalysisResult) -> List:
        """Create appendices section"""
        elements = []

        elements.append(Paragraph("LAMPIRAN", self.section_style))

        # Appendix A: Estate Information
        elements.append(Paragraph("<b>Lampiran A: Informasi Estate</b>", self.subsection_style))

        estate_info = analysis_result.get_analysis_summary()
        estates_text = f"""
        <b>Estate yang Dianalisis:</b><br/>
        {', '.join(estate_info['estates']['analyzed'])}<br/><br/>
        <b>Jumlah Estate Valid:</b> {estate_info['estates']['active_count']} dari {estate_info['estates']['total_count']}<br/>
        <b>Jumlah Divisi Aktif:</b> {estate_info['divisions']['active_count']}<br/>
        <b>Total Transaksi:</b> {estate_info['grand_totals']['kerani']:,}<br/>
        <b>Tingkat Verifikasi Keseluruhan:</b> {estate_info['grand_totals']['verification_rate']:.2f}%
        """

        estates_para = Paragraph(estates_text, self.normal_style)
        elements.append(estates_para)
        elements.append(Spacer(1, 15))

        # Appendix B: Technical Information
        elements.append(Paragraph("<b>Lampiran B: Informasi Teknis</b>", self.subsection_style))

        tech_text = f"""
        <b>Versi Analisis:</b> {analysis_result.analysis_version}<br/>
        <b>Filter Status 704:</b> {'Aktif' if analysis_result.use_status_704_filter else 'Tidak Aktif'}<br/>
        <b>Durasi Analisis:</b> {analysis_result.analysis_duration_seconds:.1f} detik<br/>
        <b>Tanggal Analisis:</b> {analysis_result.analysis_date.strftime('%d %B %Y')}<br/>
        <b>Periode Data:</b> {analysis_result.start_date.strftime('%d %B %Y')} - {analysis_result.end_date.strftime('%d %B %Y')}<br/>
        <b>Total Hari:</b> {(analysis_result.end_date - analysis_result.start_date).days + 1} hari
        """

        tech_para = Paragraph(tech_text, self.normal_style)
        elements.append(tech_para)

        # Add footer
        elements.extend(self._create_footer())

        return elements

    # Additional detailed methods would be implemented here...
    # Due to length constraints, I'm including the main structure and key methods

    def _create_detailed_division_section(self, division_summary: DivisionSummary) -> List:
        """Create detailed division section"""
        elements = []

        elements.append(Paragraph(f"DETAIL DIVISI: {division_summary.division_name}", self.section_style))

        # Division summary
        summary_data = [
            ['<b>Estate</b>', division_summary.estate_name],
            ['<b>Divisi ID</b>', division_summary.division_id],
            ['<b>Total Kerani</b>', f"{division_summary.kerani_total:,}"],
            ['<b>Transaksi Terverifikasi</b>', f"{division_summary.verification_total:,}"],
            ['<b>Tingkat Verifikasi</b>', f"{division_summary.verification_rate:.2f}%"],
            ['<b>Total Perbedaan</b>', f"{division_summary.difference_count:,}"],
            ['<b>Tingkat Perbedaan</b>', f"{division_summary.difference_rate:.2f}%"]
        ]

        summary_table = Table(summary_data, colWidths=[120, 200])
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (1, 0), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        summary_table.setStyle(summary_style)
        elements.append(summary_table)
        elements.append(Spacer(1, 15))

        # Employee breakdown
        elements.append(Paragraph("<b>Detail Karyawan</b>", self.subsection_style))

        employee_data = [['<b>Nama</b>', '<b>Role</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>% Verifikasi</b>', '<b>Perbedaan</b>', '<b>% Perbedaan</b>']]

        # Get all employees and sort by verification rate
        all_employees = division_summary.get_employee_metrics()
        all_employees.sort(key=lambda x: x.verification_rate, reverse=True)

        for emp in all_employees:
            role = 'Kerani' if emp.kerani_transactions > 0 else ('Mandor' if emp.mandor_transactions > 0 else 'Asisten')
            employee_data.append([
                emp.employee_name,
                role,
                f"{emp.kerani_transactions or emp.mandor_transactions or emp.asisten_transactions}",
                f"{emp.kerani_verified}",
                f"{emp.verification_rate:.1f}%" if emp.kerani_transactions > 0 else "-",
                f"{emp.kerani_differences}",
                f"{emp.difference_rate:.1f}%" if emp.kerani_differences > 0 else "-"
            ])

        employee_table = Table(employee_data, colWidths=[150, 60, 60, 60, 60, 60, 60])
        employee_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

        # Highlight Kerani rows
        for i, emp in enumerate(all_employees, 1):
            if emp.kerani_transactions > 0:
                if emp.verification_rate >= 90:
                    employee_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4'))  # Excellent
                elif emp.kerani_differences > 0:
                    employee_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))  # Issues

        employee_table.setStyle(employee_style)
        elements.append(employee_table)

        return elements

    def _create_grand_totals_table(self, analysis_result: AnalysisResult) -> List:
        """Create grand totals summary table"""
        elements = []

        # Grand totals data
        totals_data = [
            ['<b>METRIK</b>', '<b>JUMLAH</b>', '<b>PERSENTASE</b>'],
            ['Total Kerani', f"{analysis_result.grand_kerani:,}", '-'],
            ['Transaksi Terverifikasi', f"{analysis_result.grand_kerani_verified:,}", f"{analysis_result.grand_verification_rate:.2f}%"],
            ['Transaksi Mandor', f"{analysis_result.grand_mandor:,}", '-'],
            ['Transaksi Asisten', f"{analysis_result.grand_asisten:,}", '-'],
            ['Total Perbedaan', f"{analysis_result.grand_differences:,}", f"{analysis_result.grand_difference_rate:.2f}%"],
        ]

        # Create table
        totals_table = Table(totals_data, colWidths=[150, 100, 80])

        # Style the table
        totals_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Data rows
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),

            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            # Highlight important rows
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#E6FFFA')),  # Kerani
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#F0FFF4')),  # Verified
            ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#FFF5F5')),  # Differences
        ])

        totals_table.setStyle(totals_style)
        elements.append(totals_table)
        elements.append(Spacer(1, 12))

        return elements

    def _create_top_performers_table(self, analysis_result: AnalysisResult, limit: int = 10) -> List:
        """Create top performers table"""
        elements = []

        # Get top performers (highest verification rates)
        all_employees = analysis_result.employee_metrics
        kerani_employees = [emp for emp in all_employees if emp.kerani_transactions > 0]
        top_performers = sorted(kerani_employees, key=lambda x: x.verification_rate, reverse=True)[:limit]

        if not top_performers:
            return elements

        elements.append(Paragraph(f"<b>Top {limit} Performers (Kerani)</b>", self.subsection_style))

        # Table data
        performers_data = [
            ['<b>Peringkat</b>', '<b>Nama</b>', '<b>Divisi</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>Rate</b>'],
        ]

        for i, emp in enumerate(top_performers, 1):
            performers_data.append([
                str(i),
                emp.employee_name,
                emp.division,
                str(emp.kerani_transactions),
                str(emp.kerani_verified),
                f"{emp.verification_rate:.1f}%"
            ])

        # Create table
        performers_table = Table(performers_data, colWidths=[50, 120, 80, 60, 70, 60])

        # Style table
        performers_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),

            # Data
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 5), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),

            # Highlight top performers
            ('BACKGROUND', (0, 1), (0, 3), colors.HexColor('#F0FFF4')),  # Top 3
        ])

        performers_table.setStyle(performers_style)
        elements.append(performers_table)
        elements.append(Spacer(1, 12))

        return elements

    def _create_quality_issues_table(self, analysis_result: AnalysisResult, limit: int = 10) -> List:
        """Create quality issues table"""
        elements = []

        # Get employees with quality issues (differences)
        all_employees = analysis_result.employee_metrics
        problematic_employees = [emp for emp in all_employees if emp.kerani_differences > 0]
        problematic_employees = sorted(problematic_employees, key=lambda x: x.kerani_differences, reverse=True)[:limit]

        if not problematic_employees:
            elements.append(Paragraph("<b>Tidak Ada Masalah Kualitas</b>", self.normal_style))
            elements.append(Paragraph("Semua transaksi kerani sudah konsisten.", self.normal_style))
            elements.append(Spacer(1, 12))
            return elements

        elements.append(Paragraph(f"<b>Top {limit} Masalah Kualitas</b>", self.subsection_style))

        # Table data
        issues_data = [
            ['<b>Nama</b>', '<b>Divisi</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>Perbedaan</b>', '<b>Rate</b>'],
        ]

        for emp in problematic_employees:
            issues_data.append([
                emp.employee_name,
                emp.division,
                str(emp.kerani_transactions),
                str(emp.kerani_verified),
                str(emp.kerani_differences),
                f"{emp.difference_rate:.1f}%"
            ])

        # Create table
        issues_table = Table(issues_data, colWidths=[120, 80, 60, 70, 60, 60])

        # Style table
        issues_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53E3E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),

            # Data
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 5), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),

            # Highlight problematic rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF5F5')),
        ])

        issues_table.setStyle(issues_style)
        elements.append(issues_table)
        elements.append(Spacer(1, 12))

        return elements

    def _create_employee_performance_overview(self, analysis_result: AnalysisResult) -> List:
        """Create employee performance overview section"""
        elements = []

        elements.append(Paragraph("<b>OVERVIEW KINERJA KARYAWAN</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Performance statistics
        all_employees = analysis_result.employee_metrics
        kerani_employees = [emp for emp in all_employees if emp.kerani_transactions > 0]

        if kerani_employees:
            # Calculate statistics
            avg_verification = sum(emp.verification_rate for emp in kerani_employees) / len(kerani_employees)
            total_transactions = sum(emp.kerani_transactions for emp in kerani_employees)
            total_verified = sum(emp.kerani_verified for emp in kerani_employees)
            total_differences = sum(emp.kerani_differences for emp in kerani_employees)

            # Summary table
            overview_data = [
                ['<b>METRIK</b>', '<b>NILAI</b>'],
                ['Total Karyawan Kerani', f"{len(kerani_employees)}"],
                ['Total Transaksi', f"{total_transactions:,}"],
                ['Transaksi Terverifikasi', f"{total_verified:,}"],
                ['Rata-rata Verifikasi', f"{avg_verification:.2f}%"],
                ['Total Perbedaan', f"{total_differences:,}"],
            ]

            overview_table = Table(overview_data, colWidths=[200, 100])
            overview_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ])

            overview_table.setStyle(overview_style)
            elements.append(overview_table)
        else:
            elements.append(Paragraph("Tidak ada data karyawan kerani untuk periode ini.", self.normal_style))

        elements.append(Spacer(1, 12))
        return elements

    def _create_performance_by_role_section(self, analysis_result: AnalysisResult) -> List:
        """Create performance breakdown by role section"""
        elements = []

        elements.append(Paragraph("<b>KINERJA BERDASARKAN PERAN</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Group employees by role
        all_employees = analysis_result.employee_metrics
        kerani_emp = [emp for emp in all_employees if emp.kerani_transactions > 0]
        mandor_emp = [emp for emp in all_employees if emp.mandor_transactions > 0]
        asisten_emp = [emp for emp in all_employees if emp.asisten_transactions > 0]

        # Role breakdown table
        role_data = [
            ['<b>Peran</b>', '<b>Jumlah Karyawan</b>', '<b>Total Transaksi</b>', '<b>Rata-rata Performance</b>'],
            ['Kerani', f"{len(kerani_emp)}", f"{sum(emp.kerani_transactions for emp in kerani_emp):,}", f"{sum(emp.verification_rate for emp in kerani_emp)/len(kerani_emp):.1f}%" if kerani_emp else "0%"],
            ['Mandor', f"{len(mandor_emp)}", f"{sum(emp.mandor_transactions for emp in mandor_emp):,}", "-"],
            ['Asisten', f"{len(asisten_emp)}", f"{sum(emp.asisten_transactions for emp in asisten_emp):,}", "-"],
        ]

        role_table = Table(role_data, colWidths=[80, 80, 100, 120])
        role_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])

        role_table.setStyle(role_style)
        elements.append(role_table)
        elements.append(Spacer(1, 12))

        return elements

    def _create_performance_recommendations_section(self, analysis_result: AnalysisResult) -> List:
        """Create performance recommendations section"""
        elements = []

        elements.append(Paragraph("<b>REKOMENDASI KINERJA</b>", self.section_style))
        elements.append(Spacer(1, 12))

        all_employees = analysis_result.employee_metrics
        kerani_employees = [emp for emp in all_employees if emp.kerani_transactions > 0]

        if not kerani_employees:
            elements.append(Paragraph("Tidak ada data untuk rekomendasi.", self.normal_style))
            return elements

        recommendations = []

        # Performance-based recommendations
        low_performers = [emp for emp in kerani_employees if emp.verification_rate < 50]
        if low_performers:
            recommendations.append(
                f"<b>Perlu Perhatian Khusus:</b> {len(low_performers)} karyawan dengan tingkat verifikasi di bawah 50%. "
                "Disarankan untuk melakukan pelatihan tambahan dan supervisi yang lebih intensif."
            )

        # Quality-based recommendations
        problematic_employees = [emp for emp in kerani_employees if emp.kerani_differences > 0]
        if problematic_employees:
            recommendations.append(
                f"<b>Peningkatan Kualitas Data:</b> {len(problematic_employees)} karyawan menunjukkan perbedaan data. "
                "Perlu review proses input data dan standarisasi format."
            )

        # High performers
        high_performers = [emp for emp in kerani_employees if emp.verification_rate >= 95]
        if high_performers:
            recommendations.append(
                f"<b>Pengakuan Kinerja:</b> {len(high_performers)} karyawan mencapai tingkat verifikasi 95%+. "
                "Pertimbangkan untuk memberikan penghargaan atau sebagai mentor untuk karyawan lain."
            )

        # General recommendations
        avg_verification = sum(emp.verification_rate for emp in kerani_employees) / len(kerani_employees)
        if avg_verification < 70:
            recommendations.append(
                "<b>Program Peningkatan Keseluruhan:</b> Tingkat verifikasi rata-rata di bawah 70%. "
                "Disarankan untuk melakukan evaluasi sistem dan pelatihan menyeluruh."
            )

        if not recommendations:
            recommendations.append(
                "<b>Kinerja Baik:</b> Semua metrik kinerja dalam rentang yang dapat diterima. "
                "Lanjutkan monitoring dan maintenance proses yang ada."
            )

        # Add recommendations to elements
        for i, rec in enumerate(recommendations, 1):
            rec_para = Paragraph(f"{i}. {rec}", self.normal_style)
            elements.append(rec_para)
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 12))
        return elements

    def _create_quality_summary_section(self, analysis_result: AnalysisResult) -> List:
        """Create quality summary section"""
        elements = []

        elements.append(Paragraph("<b>RINGKASAN KUALITAS DATA</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Quality metrics
        total_differences = analysis_result.grand_differences
        total_verified = analysis_result.grand_kerani_verified
        quality_rate = ((total_verified - total_differences) / total_verified * 100) if total_verified > 0 else 100

        quality_data = [
            ['<b>METRIK KUALITAS</b>', '<b>NILAI</b>'],
            ['Total Transaksi Terverifikasi', f"{total_verified:,}"],
            ['Total Perbedaan', f"{total_differences:,}"],
            ['Tingkat Kualitas Data', f"{quality_rate:.2f}%"],
        ]

        quality_table = Table(quality_data, colWidths=[200, 100])
        quality_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38A169')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])

        quality_table.setStyle(quality_style)
        elements.append(quality_table)
        elements.append(Spacer(1, 12))

        return elements

    def _create_detailed_quality_analysis(self, analysis_result: AnalysisResult) -> List:
        """Create detailed quality analysis section"""
        elements = []

        elements.append(Paragraph("<b>ANALISIS KUALITAS DETAIL</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Get employees with quality issues
        all_employees = analysis_result.employee_metrics
        problematic_employees = [emp for emp in all_employees if emp.kerani_differences > 0]

        if problematic_employees:
            # Sort by number of differences
            problematic_employees.sort(key=lambda x: x.kerani_differences, reverse=True)

            # Create detailed table
            detail_data = [
                ['<b>Nama</b>', '<b>Divisi</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>Perbedaan</b>', '<b>Rate</b>'],
            ]

            for emp in problematic_employees:
                detail_data.append([
                    emp.employee_name,
                    emp.division,
                    str(emp.kerani_transactions),
                    str(emp.kerani_verified),
                    str(emp.kerani_differences),
                    f"{emp.difference_rate:.1f}%"
                ])

            detail_table = Table(detail_data, colWidths=[120, 80, 60, 70, 60, 60])
            detail_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53E3E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 5), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF5F5')),
            ])

            detail_table.setStyle(detail_style)
            elements.append(detail_table)
        else:
            elements.append(Paragraph("<b>TIDAK ADA MASALAH KUALITAS</b>", self.normal_style))
            elements.append(Paragraph("Semua transaksi kerani konsisten dan tidak ada perbedaan.", self.normal_style))

        elements.append(Spacer(1, 12))
        return elements

    def _create_problematic_employees_section(self, analysis_result: AnalysisResult) -> List:
        """Create problematic employees section"""
        elements = []

        elements.append(Paragraph("<b>KARYAWAN YANG MEMERLUKAN PERHATIAN</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Get problematic employees
        all_employees = analysis_result.employee_metrics
        problematic_employees = [emp for emp in all_employees if emp.kerani_differences > 0 or emp.verification_rate < 50]

        if problematic_employees:
            # Sort by severity (differences first, then low verification)
            problematic_employees.sort(key=lambda x: (x.kerani_differences * 10 + (50 - x.verification_rate)), reverse=True)

            # Create table
            prob_data = [
                ['<b>Nama</b>', '<b>Divisi</b>', '<b>Masalah</b>', '<b>Detail</b>', '<b>Aksi Rekomendasi</b>'],
            ]

            for emp in problematic_employees:
                issues = []
                details = []
                actions = []

                if emp.kerani_differences > 0:
                    issues.append("Kualitas Data")
                    details.append(f"{emp.kerani_differences} perbedaan")
                    actions.append("Training input data")
                if emp.verification_rate < 50:
                    issues.append("Verifikasi Rendah")
                    details.append(f"{emp.verification_rate:.1f}%")
                    actions.append("Supervisi tambahan")

                prob_data.append([
                    emp.employee_name,
                    emp.division,
                    ", ".join(issues),
                    ", ".join(details),
                    ", ".join(actions)
                ])

            prob_table = Table(prob_data, colWidths=[120, 80, 80, 80, 100])
            prob_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DD6B20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 4), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFDF7')),
            ])

            prob_table.setStyle(prob_style)
            elements.append(prob_table)
        else:
            elements.append(Paragraph("<b>SEMUA KARYAWAN BERKINERJA BAIK</b>", self.normal_style))
            elements.append(Paragraph("Tidak ada karyawan yang memerlukan perhatian khusus untuk periode ini.", self.normal_style))

        elements.append(Spacer(1, 12))
        return elements

    def _create_quality_recommendations_section(self, analysis_result: AnalysisResult) -> List:
        """Create quality recommendations section"""
        elements = []

        elements.append(Paragraph("<b>REKOMENDASI PENINGKATAN KUALITAS</b>", self.section_style))
        elements.append(Spacer(1, 12))

        recommendations = []

        total_differences = analysis_result.grand_differences
        total_verified = analysis_result.grand_kerani_verified

        if total_differences > 0:
            diff_rate = (total_differences / total_verified * 100) if total_verified > 0 else 0

            if diff_rate > 10:
                recommendations.append(
                    "<b>Prioritas Tinggi:</b> Tingkat perbedaan data tinggi (>10%). "
                    "Segera lakukan evaluasi proses input data dan standarisasi format."
                )
            elif diff_rate > 5:
                recommendations.append(
                    "<b>Perlu Perhatian:</b> Tingkat perbedaan data menengah (5-10%). "
                    "Perlu program pelatihan dan monitoring yang lebih ketat."
                )
            else:
                recommendations.append(
                    "<b>Tingkat Baik:</b> Tingkat perbedaan data rendah (<5%). "
                    "Lanjutkan proses monitoring yang ada."
                )

            recommendations.extend([
                "<b>Aksi Rekomendasi:</b>",
                "1. Standardisasi format input data untuk semua karyawan",
                "2. Implementasi checklist verifikasi sebelum input",
                "3. Pelatihan reguler untuk aplikasi FFB Scanner",
                "4. Sistem review otomatis untuk deteksi perbedaan",
                "5. Feedback loop untuk karyawan dengan performa rendah"
            ])

        else:
            recommendations.append(
                "<b>Kualitas Data Sempurna:</b> Tidak ada perbedaan data yang terdeteksi. "
                "Pertahankan proses quality control yang sudah berjalan dengan baik."
            )

        # Add recommendations to elements
        for rec in recommendations:
            rec_para = Paragraph(rec, self.normal_style)
            elements.append(rec_para)
            elements.append(Spacer(1, 6))

        return elements

    def _create_detailed_employee_section(self, analysis_result: AnalysisResult) -> List:
        """Create detailed employee section"""
        elements = []

        elements.append(Paragraph("<b>DETAIL KINERJA KARYAWAN</b>", self.section_style))
        elements.append(Spacer(1, 12))

        # Get all employees with transactions
        all_employees = analysis_result.employee_metrics
        active_employees = [emp for emp in all_employees if emp.total_transactions > 0]

        if active_employees:
            # Sort by name
            active_employees.sort(key=lambda x: x.employee_name)

            # Create detailed table
            emp_data = [
                ['<b>Nama</b>', '<b>Divisi</b>', '<b>Peran</b>', '<b>Total</b>', '<b>Terverifikasi</b>', '<b>Rate</b>', '<b>Keterangan</b>'],
            ]

            for emp in active_employees:
                remarks = ""
                if emp.role == 'Kerani':
                    if emp.kerani_differences > 0:
                        remarks = f"{emp.kerani_differences} perbedaan"
                    elif emp.verification_rate >= 95:
                        remarks = "Sangat Baik"
                    elif emp.verification_rate >= 80:
                        remarks = "Baik"
                    elif emp.verification_rate >= 60:
                        remarks = "Cukup"
                    else:
                        remarks = "Perlu Perbaikan"

                emp_data.append([
                    emp.employee_name,
                    emp.division,
                    emp.role,
                    str(emp.total_transactions),
                    str(emp.verified_count) if emp.role == 'Kerani' else '-',
                    f"{emp.verification_rate:.1f}%" if emp.role == 'Kerani' else '-',
                    remarks
                ])

            emp_table = Table(emp_data, colWidths=[120, 80, 60, 50, 60, 60, 80])
            emp_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299E1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 1), (0, 5), 'LEFT'),
                ('ALIGN', (1, 1), (5, -1), 'CENTER'),
                ('ALIGN', (6, 1), (6, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ])

            # Color code based on performance
            for i, emp in enumerate(active_employees, 1):
                if emp.role == 'Kerani':
                    if emp.verification_rate >= 95:
                        emp_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4'))
                    elif emp.verification_rate < 60 or emp.kerani_differences > 0:
                        emp_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))

            emp_table.setStyle(emp_style)
            elements.append(emp_table)
        else:
            elements.append(Paragraph("Tidak ada data karyawan untuk periode ini.", self.normal_style))

        elements.append(Spacer(1, 12))
        return elements

    def _create_footer(self) -> List:
        """Create footer elements"""
        elements = []

        elements.append(Spacer(1, 20))

        timestamp = datetime.now().strftime("%d %B %Y %H:%M:%S")
        footer_text = f"<b>Laporan dibuat pada:</b> {timestamp}<br/>"
        footer_text += "<i>Sistem Analisis FFB Scanner - PT. Rebinmas Jaya</i>"

        footer_para = Paragraph(footer_text, self.small_style)
        elements.append(footer_para)

        return elements