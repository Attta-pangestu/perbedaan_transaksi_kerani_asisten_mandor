#!/usr/bin/env python3
"""
Report Generator untuk Sistem Laporan FFB
Menggenerate laporan PDF berdasarkan template dan data analysis
"""

import os
from datetime import datetime
from typing import Dict, List, Any
import logging
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class ReportGenerator:
    """Generator untuk laporan FFB berbasis template"""

    def __init__(self, output_dir: str = "reports"):
        # Resolve to absolute path - reports is in the same directory as this script's parent
        if not os.path.isabs(output_dir):
            # Get the parent directory of src (which is Reporting_System_Ifes)
            current_file = os.path.abspath(__file__)
            src_dir = os.path.dirname(current_file)
            # reports is in the same level as src, not parent of src
            output_dir = os.path.join(src_dir, "..", output_dir)
            # Resolve .. to get absolute path
            output_dir = os.path.abspath(output_dir)

        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ReportGenerator initialized with output directory: {self.output_dir}")
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_pdf_report(self, template: Dict, analysis_results: List[Dict],
                          parameters: Dict) -> str:
        """Generate PDF report berdasarkan template dan hasil analysis"""
        try:
            # Create filename based on template
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            start_date = parameters.get('START_DATE')
            end_date = parameters.get('END_DATE')

            if hasattr(start_date, 'strftime'):
                period = f"{start_date.strftime('%B_%Y')}"
            else:
                period = f"{start_date}_to_{end_date}"

            filename = template.get('output', {}).get('filename_pattern',
                f"Laporan_{template.get('template_id', 'unknown')}_{period}_{timestamp}.pdf")

            # Replace placeholders
            filename = filename.replace('{PERIOD}', period).replace('{TIMESTAMP}', timestamp)

            filepath = os.path.join(self.output_dir, filename)

            # Get report structure from template
            report_structure = template.get('report_structure', {})

            # Create PDF document
            layout = report_structure.get('layout', {})
            margins = layout.get('margins', {})

            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4) if layout.get('orientation') == 'landscape' else A4,
                leftMargin=margins.get('left', 30),
                rightMargin=margins.get('right', 30),
                topMargin=margins.get('top', 40),
                bottomMargin=margins.get('bottom', 40)
            )

            styles = getSampleStyleSheet()
            story = []

            # Add company header
            self._add_company_header(story, template, styles)

            # Add title
            self._add_title_section(story, template, parameters, styles)

            # Add summary box
            self._add_summary_box(story, analysis_results, styles)

            # Add main table
            self._add_main_table(story, template, analysis_results, styles)

            # Add explanations
            self._add_explanations(story, template, styles)

            # Add footer
            self._add_footer(story, template, styles)

            # Build PDF
            doc.build(story)

            self.logger.info(f"Generated PDF report: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            raise

    def _add_company_header(self, story: List, template: Dict, styles):
        """Add company header with logo and name"""
        company = template.get('report_structure', {}).get('company', {})

        # Add logo if available
        logo_path = company.get('logo_path')
        if logo_path:
            # Try relative path from parent directory
            full_logo_path = os.path.join("..", logo_path)
            if not os.path.exists(full_logo_path):
                # Try current directory
                full_logo_path = logo_path

            if os.path.exists(full_logo_path):
                try:
                    logo = Image(full_logo_path, width=72, height=72)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 10))
                except Exception as e:
                    self.logger.warning(f"Logo loading error: {e}")
            else:
                self.logger.warning(f"Logo file not found: {full_logo_path}")

        # Add company name
        header_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )

        company_header = Paragraph(
            f"<b>{company.get('name', 'PT. REBINMAS JAYA')}</b><br/>{company.get('subtitle', 'SISTEM MONITORING TRANSAKSI FFB')}",
            header_style
        )
        story.append(company_header)
        story.append(Spacer(1, 10))

    def _add_title_section(self, story: List, template: Dict, parameters: Dict, styles):
        """Add title and subtitle"""
        report_structure = template.get('report_structure', {})
        title = report_structure.get('title', 'LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN')
        subtitle_template = report_structure.get('subtitle', 'Periode: ${START_DATE} - ${END_DATE}')

        # Format subtitle
        start_date = parameters.get('START_DATE')
        end_date = parameters.get('END_DATE')

        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%d %B %Y')
        else:
            start_str = str(start_date)

        if hasattr(end_date, 'strftime'):
            end_str = end_date.strftime('%d %B %Y')
        else:
            end_str = str(end_date)

        subtitle = subtitle_template.replace('${START_DATE}', start_str).replace('${END_DATE}', end_str)

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=8,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )

        title_para = Paragraph(title, title_style)
        subtitle_para = Paragraph(subtitle, subtitle_style)

        story.append(title_para)
        story.append(subtitle_para)

    def _add_summary_box(self, story: List, analysis_results: List[Dict], styles):
        """Add summary statistics box"""
        total_estates = len(set(result['estate'] for result in analysis_results))
        total_divisions = len(analysis_results)

        summary_style = ParagraphStyle(
            'SummaryBox',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2D3748'),
            alignment=TA_CENTER,
            spaceAfter=20,
            leftIndent=50,
            rightIndent=50
        )

        summary_text = f"""<b>RINGKASAN ANALISIS:</b> {total_estates} Estate • {total_divisions} Divisi •
        Analisis Transaksi Real-time • Verifikasi Otomatis"""

        summary_box = Paragraph(summary_text, summary_style)
        story.append(summary_box)
        story.append(Spacer(1, 15))

    def _add_main_table(self, story: List, template: Dict, analysis_results: List[Dict], styles):
        """Add main analysis table"""
        report_structure = template.get('report_structure', {})
        table_columns = report_structure.get('table_columns', [])
        styling = report_structure.get('styling', {})

        # Create table data
        table_data = []

        # Header
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )

        header = []
        for col in table_columns:
            header.append(Paragraph(col['title'], header_style))
        table_data.append(header)

        # Process analysis results (same logic as original)
        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
        cell_style_left = ParagraphStyle('CellStyleLeft', parent=styles['Normal'], fontSize=8, alignment=TA_LEFT)

        grand_kerani = 0
        grand_mandor = 0
        grand_asisten = 0
        grand_kerani_verified = 0

        for result in analysis_results:
            estate = result['estate']
            division = result['division']
            kerani_total = result['kerani_total']
            mandor_total = result['mandor_total']
            asisten_total = result['asisten_total']
            verifikasi_total = result['verifikasi_total']
            verification_rate = result['verification_rate']
            employee_details = result['employee_details']

            # Division summary row
            total_kerani_only = kerani_total
            total_verified_kerani = verifikasi_total
            division_verification_rate = (total_verified_kerani / total_kerani_only * 100) if total_kerani_only > 0 else 0

            table_data.append([
                Paragraph(estate, cell_style),
                Paragraph(division, cell_style),
                Paragraph(f"== {division} TOTAL ==", cell_style),
                Paragraph('SUMMARY', cell_style),
                Paragraph(str(total_kerani_only), cell_style),
                Paragraph(f"{division_verification_rate:.2f}% ({total_verified_kerani})", cell_style),
                Paragraph("", cell_style)
            ])

            # Employee rows
            for emp_id, emp_data in employee_details.items():
                # Kerani rows
                if emp_data['kerani'] > 0:
                    kerani_verification_rate = (emp_data.get('kerani_verified', 0) / emp_data['kerani'] * 100) if emp_data['kerani'] > 0 else 0
                    verified_count = emp_data.get('kerani_verified', 0)
                    differences_count = emp_data.get('kerani_differences', 0)
                    percentage_text = f"{kerani_verification_rate:.2f}% ({verified_count})"

                    difference_percentage = (differences_count / verified_count * 100) if verified_count > 0 else 0
                    keterangan_text = f"{differences_count} perbedaan ({difference_percentage:.1f}%)"

                    table_data.append([
                        Paragraph(estate, cell_style),
                        Paragraph(division, cell_style),
                        Paragraph(emp_data['name'], cell_style_left),
                        Paragraph('KERANI', cell_style),
                        Paragraph(str(emp_data['kerani']), cell_style),
                        Paragraph(percentage_text, cell_style),
                        Paragraph(keterangan_text, cell_style)
                    ])

                # Mandor rows
                if emp_data['mandor'] > 0:
                    mandor_percentage = (emp_data['mandor'] / kerani_total * 100) if kerani_total > 0 else 0
                    table_data.append([
                        Paragraph(estate, cell_style),
                        Paragraph(division, cell_style),
                        Paragraph(emp_data['name'], cell_style_left),
                        Paragraph('MANDOR', cell_style),
                        Paragraph(str(emp_data['mandor']), cell_style),
                        Paragraph(f"{mandor_percentage:.2f}%", cell_style),
                        Paragraph("", cell_style)
                    ])

                # Asisten rows
                if emp_data['asisten'] > 0:
                    asisten_percentage = (emp_data['asisten'] / kerani_total * 100) if kerani_total > 0 else 0
                    table_data.append([
                        Paragraph(estate, cell_style),
                        Paragraph(division, cell_style),
                        Paragraph(emp_data['name'], cell_style_left),
                        Paragraph('ASISTEN', cell_style),
                        Paragraph(str(emp_data['asisten']), cell_style),
                        Paragraph(f"{asisten_percentage:.2f}%", cell_style),
                        Paragraph("", cell_style)
                    ])

            # Separator
            table_data.append([
                Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style),
                Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style)
            ])

            # Add to grand totals
            grand_kerani += kerani_total
            grand_mandor += mandor_total
            grand_asisten += asisten_total
            grand_kerani_verified += verifikasi_total

        # Grand total row
        grand_total_kerani_only = grand_kerani
        grand_total_verified_kerani = grand_kerani_verified
        grand_verification_rate = (grand_total_verified_kerani / grand_total_kerani_only * 100) if grand_total_kerani_only > 0 else 0

        table_data.append([
            Paragraph('=== GRAND TOTAL ===', cell_style),
            Paragraph('', cell_style),
            Paragraph('', cell_style),
            Paragraph('', cell_style),
            Paragraph(str(grand_total_kerani_only), cell_style),
            Paragraph(f"{grand_verification_rate:.2f}% ({grand_total_verified_kerani})", cell_style),
            Paragraph("", cell_style)
        ])

        # Create table with column widths
        col_widths = [col['width'] for col in table_columns]
        table = Table(table_data, repeatRows=1, colWidths=col_widths)

        # Apply styling
        self._apply_table_styling(table, styling, len(table_data))

        story.append(table)
        story.append(Spacer(1, 20))

    def _apply_table_styling(self, table: Table, styling: Dict, row_count: int):
        """Apply styling to table based on template configuration"""
        header_style = styling.get('header', {})
        row_styles = styling.get('row_styles', {})

        style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_style.get('background_color', '#2C5282'))),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), header_style.get('font_name', 'Helvetica-Bold')),
            ('FONTSIZE', (0, 0), (-1, 0), header_style.get('font_size', 10)),
            ('TOPPADDING', (0, 0), (-1, 0), header_style.get('padding', 12)),
            ('BOTTOMPADDING', (0, 0), (-1, 0), header_style.get('padding', 12)),

            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white]),
        ])

        # Apply row-specific styling
        for i in range(1, row_count):  # Skip header row
            # This would need to be implemented based on the actual data
            # For now, keeping the original logic
            pass

        table.setStyle(style)

    def _add_explanations(self, story: List, template: Dict, styles):
        """Add explanation sections"""
        explanations = template.get('report_structure', {}).get('explanations', [])

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
            alignment=TA_LEFT
        )

        for section in explanations:
            title = section.get('title', '')
            items = section.get('items', [])

            if title:
                title_para = Paragraph(title, explanation_title_style)
                story.append(title_para)

            for item_text in items:
                item_para = Paragraph(f"• {item_text}", explanation_style)
                story.append(item_para)

            story.append(Spacer(1, 15))

    def _add_footer(self, story: List, template: Dict, styles):
        """Add footer with generation info"""
        footer_config = template.get('footer', {})
        footer_template = footer_config.get('template',
            '📅 Laporan dibuat pada: {DATETIME} | 🔄 Sistem Analisis Real-time | 🏢 PT. Rebinmas Jaya')

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=footer_config.get('font_size', 8),
            textColor=colors.HexColor(footer_config.get('text_color', '#718096')),
            alignment=TA_CENTER,
            spaceBefore=10
        )

        footer_text = footer_template.format(
            DATETIME=datetime.now().strftime('%d %B %Y, %H:%M:%S')
        )

        footer = Paragraph(footer_text, footer_style)
        story.append(footer)