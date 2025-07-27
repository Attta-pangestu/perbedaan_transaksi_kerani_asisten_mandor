import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os
import logging

def generate_pdf_report(analyzed_data, summary_stats, output_dir='reports'):
    """
    Menghasilkan laporan PDF dari data yang telah dianalisis.
    
    Args:
        analyzed_data: DataFrame hasil analisis
        summary_stats: Dictionary berisi statistik ringkasan
        output_dir: Direktori untuk menyimpan laporan
    
    Returns:
        str: Path ke file PDF yang dihasilkan
    """
    try:
        # Persiapkan direktori output
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(output_dir, f"analisis_perbedaan_panen_{timestamp}.pdf")
        
        # Buat dokumen PDF
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=landscape(A4), 
            leftMargin=1*cm, 
            rightMargin=1*cm, 
            topMargin=2*cm, 
            bottomMargin=2*cm
        )
        
        # Elemen-elemen untuk PDF
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=12,
            alignment=1  # Center
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=1  # Center
        )
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=0  # Left
        )
        
        # Header
        header_text = Paragraph("Laporan Analisis Perbedaan Panen", header_style)
        elements.append(header_text)
        elements.append(Spacer(1, 0.5*cm))
        
        # Title
        title = Paragraph("Analisis Perbedaan Panen", title_style)
        elements.append(title)
        
        # Subtitle with date
        subtitle = Paragraph(f"Dibuat pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style)
        elements.append(subtitle)
        
        # Tambahkan statistik ringkasan
        summary_title = Paragraph("Statistik Ringkasan", styles['Heading2'])
        elements.append(summary_title)
        
        summary_text = [
            Paragraph(f"Total Transaksi: {summary_stats['total_transactions']}", styles['Normal']),
            Paragraph(f"Transaksi dengan Perbedaan: {summary_stats['transactions_with_differences']}", styles['Normal']),
            Paragraph(f"Transaksi tanpa Perbedaan: {summary_stats['total_transactions'] - summary_stats['transactions_with_differences']}", styles['Normal']),
            Paragraph(f"Rata-rata Perbedaan Total: {summary_stats['avg_total_diff']:.2f}", styles['Normal']),
            Paragraph(f"Perbedaan Total Maksimum: {summary_stats['max_total_diff']}", styles['Normal']),
            Paragraph(f"Perbedaan Total Minimum: {summary_stats['min_total_diff']}", styles['Normal']),
        ]
        
        for text in summary_text:
            elements.append(text)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # Buat tabel untuk data dengan perbedaan
        diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] != 0].copy()
        
        if not diff_data.empty:
            diff_title = Paragraph("Data dengan Perbedaan", styles['Heading2'])
            elements.append(diff_title)
            
            # Pilih kolom yang akan ditampilkan (hanya kolom dasar dan kolom diff)
            diff_cols = [col for col in diff_data.columns if col.endswith('_DIFF') or 
                         col in ['TRANSNO', 'TRANSDATE', 'FIELDNO', 'RECORDTAG_1', 'RECORDTAG_2', 'NAME_1', 'NAME_2', 'TOTAL_DIFF']]
            
            diff_data_simplified = diff_data[diff_cols].head(50)  # Batasi 50 baris untuk performa
            
            # Konversi DataFrame ke list untuk tabel
            table_data = [diff_cols]  # Header row
            for idx, row in diff_data_simplified.iterrows():
                row_data = []
                for col in diff_cols:
                    val = row[col]
                    if isinstance(val, float):
                        row_data.append(f"{val:.2f}")
                    else:
                        row_data.append(str(val))
                table_data.append(row_data)
            
            # Buat tabel
            col_widths = [1.5*cm] * len(diff_cols)  # Default width
            # Atur lebar kolom khusus
            for i, col in enumerate(diff_cols):
                if col in ['TRANSNO', 'TRANSDATE', 'FIELDNO']:
                    col_widths[i] = 2*cm
                elif col in ['NAME_1', 'NAME_2']:
                    col_widths[i] = 3*cm
                elif col.endswith('_DIFF'):
                    col_widths[i] = 1.2*cm
            
            table = Table(table_data, colWidths=col_widths)
            
            # Style tabel
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),  # Green header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),  # Light grey rows
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            
            # Highlight rows where abs(TOTAL_DIFF) > 5
            for i in range(1, len(table_data)):
                total_diff = float(table_data[i][diff_cols.index('TOTAL_DIFF')])
                if abs(total_diff) > 5:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFCDD2'))  # Light red
                    table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.red)
            
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 0.5*cm))
        
        # Buat tabel untuk data tanpa perbedaan
        no_diff_data = analyzed_data[analyzed_data['TOTAL_DIFF'] == 0].copy()
        
        if not no_diff_data.empty:
            no_diff_title = Paragraph("Data tanpa Perbedaan (Sampel 20 Baris)", styles['Heading2'])
            elements.append(no_diff_title)
            
            # Pilih kolom yang akan ditampilkan
            no_diff_cols = ['TRANSNO', 'TRANSDATE', 'FIELDNO', 'RECORDTAG_1', 'RECORDTAG_2', 'NAME_1', 'NAME_2', 'TOTAL_1', 'TOTAL_2', 'TOTAL_DIFF']
            
            no_diff_data_sample = no_diff_data[no_diff_cols].head(20)  # Batasi 20 baris
            
            # Konversi DataFrame ke list untuk tabel
            table_data = [no_diff_cols]  # Header row
            for idx, row in no_diff_data_sample.iterrows():
                row_data = []
                for col in no_diff_cols:
                    val = row[col]
                    if isinstance(val, float):
                        row_data.append(f"{val:.2f}")
                    else:
                        row_data.append(str(val))
                table_data.append(row_data)
            
            # Buat tabel
            col_widths = [1.5*cm] * len(no_diff_cols)  # Default width
            # Atur lebar kolom khusus
            for i, col in enumerate(no_diff_cols):
                if col in ['TRANSNO', 'TRANSDATE', 'FIELDNO']:
                    col_widths[i] = 2*cm
                elif col in ['NAME_1', 'NAME_2']:
                    col_widths[i] = 3*cm
            
            table = Table(table_data, colWidths=col_widths)
            
            # Style tabel
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),  # Blue header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E3F2FD')),  # Light blue rows
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            
            table.setStyle(table_style)
            elements.append(table)
        
        # Tambahkan footer
        def add_header_footer(canvas, doc):
            canvas.saveState()
            # Header
            canvas.setFont("Helvetica", 8)
            canvas.drawString(1*cm, A4[1] - 1*cm, "Laporan Analisis Perbedaan Panen")
            # Footer with page number
            canvas.setFont("Helvetica", 8)
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 1*cm, 1*cm, f"Halaman {page_num}")
            canvas.restoreState()
        
        # Build PDF
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        
        print(f"Laporan PDF disimpan ke: {pdf_path}")
        return pdf_path
    
    except Exception as e:
        print(f"Error saat membuat laporan PDF: {e}")
        logging.error(f"Error saat membuat laporan PDF: {e}")
        return None
