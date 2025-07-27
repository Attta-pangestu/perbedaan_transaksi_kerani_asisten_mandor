import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus.flowables import Flowable

# Configure logging
logging.basicConfig(
    filename='report_generation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a rotated text class
class RotatedText(Flowable):
    def __init__(self, text, font_name='Helvetica-Bold', font_size=8, rotation=90):
        Flowable.__init__(self)
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.rotation = rotation

    def draw(self):
        canvas = self.canv
        canvas.saveState()

        # Translate and rotate
        canvas.translate(self.width/2, self.height/2)
        canvas.rotate(self.rotation)

        # Set font
        canvas.setFont(self.font_name, self.font_size)

        # Draw text centered
        canvas.drawCentredString(0, 0, self.text)

        canvas.restoreState()

    def wrap(self, availWidth, availHeight):
        # Size is switched due to rotation
        self.width = self.font_size * 1.2  # Estimate width based on font size
        self.height = len(self.text) * self.font_size * 0.6  # Estimate height based on text length
        return self.width, self.height

def create_comparison_scatter(data, output_dir):
    """
    Create scatter plots comparing PM vs P1/P5 values.

    Args:
        data: DataFrame with PM and P1/P5 data
        output_dir: Directory to save the chart

    Returns:
        str: Path to the saved chart image
    """
    try:
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))

        # Columns to analyze
        bunch_columns = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT', 'TOTAL']

        # Select the top 4 columns with the most differences for detailed plots
        diff_counts = {}
        for col in bunch_columns:
            diff_col = f'{col}_DIFF'
            if diff_col in data.columns:
                diff_counts[col] = (data[diff_col] != 0).sum()

        # Sort columns by difference count and take top 4
        top_columns = sorted(diff_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        top_column_names = [item[0] for item in top_columns]

        # If we have less than 4 columns with differences, add TOTAL
        if len(top_column_names) < 4 and 'TOTAL' not in top_column_names:
            top_column_names.append('TOTAL')

        # Fill remaining slots with other columns if needed
        remaining_slots = 4 - len(top_column_names)
        if remaining_slots > 0:
            for col in bunch_columns:
                if col not in top_column_names:
                    top_column_names.append(col)
                    remaining_slots -= 1
                    if remaining_slots == 0:
                        break

        # Create scatter plots for each selected column
        for i, col in enumerate(top_column_names[:4]):
            row, col_idx = divmod(i, 2)
            ax = axs[row, col_idx]

            col1 = f'{col}_1'
            col2 = f'{col}_2'
            diff_col = f'{col}_DIFF'

            if col1 in data.columns and col2 in data.columns:
                # Separate data with and without differences
                has_diff = data[diff_col] != 0 if diff_col in data.columns else pd.Series(False, index=data.index)
                no_diff = ~has_diff

                # Plot points without differences
                if no_diff.any():
                    ax.scatter(data.loc[no_diff, col1], data.loc[no_diff, col2],
                              color='blue', alpha=0.5, label='Tanpa Selisih')

                # Plot points with differences
                if has_diff.any():
                    ax.scatter(data.loc[has_diff, col1], data.loc[has_diff, col2],
                              color='red', alpha=0.7, label='Dengan Selisih')

                # Add diagonal line (perfect match)
                min_val = min(data[col1].min(), data[col2].min())
                max_val = max(data[col1].max(), data[col2].max())
                ax.plot([min_val, max_val], [min_val, max_val], 'g--', label='Nilai Sama')

                # Add labels and title
                ax.set_xlabel(f'Nilai Kerani (PM)')
                ax.set_ylabel(f'Nilai Mandor/Asisten (P1/P5)')
                ax.set_title(f'Perbandingan {col}')
                ax.grid(alpha=0.3)
                ax.legend(fontsize=8)

                # Add annotations for points with large differences
                for idx in data[has_diff].index:
                    if abs(data.loc[idx, diff_col]) > 5:
                        ax.annotate(f'Selisih: {data.loc[idx, diff_col]:.1f}',
                                   (data.loc[idx, col1], data.loc[idx, col2]),
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=7, color='darkred')

        # Adjust layout
        plt.tight_layout()

        # Save the chart
        os.makedirs(output_dir, exist_ok=True)
        scatter_path = os.path.join(output_dir, 'comparison_scatter.png')
        plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
        plt.close()

        return scatter_path

    except Exception as e:
        logging.error(f"Error creating comparison scatter plot: {e}")
        return None

def create_column_diff_chart(data, output_dir):
    """
    Create a chart showing differences by column.

    Args:
        data: DataFrame with difference columns
        output_dir: Directory to save the chart

    Returns:
        str: Path to the saved chart image
    """
    try:
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Columns to analyze
        bunch_columns = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
        diff_columns = [f'{col}_DIFF' for col in bunch_columns]

        # Calculate average absolute difference for each column
        avg_abs_diffs = [data[col].abs().mean() for col in diff_columns if col in data.columns]
        col_labels = [col.replace('_DIFF', '') for col in diff_columns if col in data.columns]

        # First chart: Average absolute difference by column
        bars = ax1.bar(col_labels, avg_abs_diffs, color='#2196F3', alpha=0.7)
        ax1.set_xlabel('Kolom')
        ax1.set_ylabel('Rata-rata Selisih Absolut')
        ax1.set_title('Rata-rata Selisih Absolut per Kolom')
        ax1.grid(axis='y', alpha=0.3)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)

        # Second chart: Count of transactions with differences by column
        counts = [(data[col] != 0).sum() for col in diff_columns if col in data.columns]
        bars = ax2.bar(col_labels, counts, color='#FF9800', alpha=0.7)
        ax2.set_xlabel('Kolom')
        ax2.set_ylabel('Jumlah Transaksi dengan Selisih')
        ax2.set_title('Jumlah Transaksi dengan Selisih per Kolom')
        ax2.grid(axis='y', alpha=0.3)
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)

        # Adjust layout
        plt.tight_layout()

        # Save the chart
        os.makedirs(output_dir, exist_ok=True)
        chart_path = os.path.join(output_dir, 'column_diff_chart.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        return chart_path

    except Exception as e:
        logging.error(f"Error creating column difference chart: {e}")
        return None

def create_histogram(data, output_dir):
    """
    Create a histogram of TOTAL_DIFF distribution.

    Args:
        data: DataFrame with TOTAL_DIFF column
        output_dir: Directory to save the histogram

    Returns:
        str: Path to the saved histogram image
    """
    try:
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # First histogram: Regular distribution
        bins = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
        ax1.hist(data['TOTAL_DIFF'], bins=bins, color='#4CAF50', edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Selisih Total')
        ax1.set_ylabel('Frekuensi')
        ax1.set_title('Distribusi Selisih Total')
        ax1.grid(axis='y', alpha=0.75)

        # Second histogram: Absolute difference distribution
        abs_bins = [0, 1, 2, 3, 4, 5, 10, 15, 20]
        ax2.hist(data['TOTAL_DIFF'].abs(), bins=abs_bins, color='#FF5722', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Selisih Absolut')
        ax2.set_ylabel('Frekuensi')
        ax2.set_title('Distribusi Selisih Absolut')
        ax2.grid(axis='y', alpha=0.75)

        # Add a vertical line at threshold value 5
        ax2.axvline(x=5, color='red', linestyle='--', linewidth=2, label='Batas Selisih Signifikan (5)')
        ax2.legend()

        # Adjust layout
        plt.tight_layout()

        # Save the histogram
        os.makedirs(output_dir, exist_ok=True)
        histogram_path = os.path.join(output_dir, 'histogram.png')
        plt.savefig(histogram_path, dpi=300, bbox_inches='tight')
        plt.close()

        logging.info(f"Histogram saved to {histogram_path}")
        return histogram_path

    except Exception as e:
        logging.error(f"Error creating histogram: {e}")
        return None

def create_diff_histogram(data, output_dir, kerani_name=None):
    """
    Create a histogram specifically for transactions with differences.

    Args:
        data: DataFrame with difference data (should already be filtered to have differences)
        output_dir: Directory to save the histogram
        kerani_name: Optional kerani name if creating histogram for specific kerani

    Returns:
        str: Path to the saved histogram image
    """
    try:
        # Filter for rows with differences
        diff_data = data[data['TOTAL_DIFF'] != 0].copy() if 'TOTAL_DIFF' in data.columns else data.copy()

        if diff_data.empty:
            logging.warning(f"No difference data available for histogram {kerani_name if kerani_name else 'all'}")
            return None

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Figure title
        title_prefix = f"Kerani: {kerani_name}" if kerani_name else "Semua Kerani"
        fig.suptitle(f"Analisis Selisih untuk {title_prefix}", fontsize=14)

        # First plot: Distribution by difference magnitude
        bins = [-20, -15, -10, -5, -1, 1, 5, 10, 15, 20]
        n, bins, patches = ax1.hist(diff_data['TOTAL_DIFF'], bins=bins,
                                    color='#2196F3', edgecolor='black', alpha=0.7)

        # Color bins differently based on range
        for i in range(len(patches)):
            if i < 3:  # Bins for negative differences < -5
                patches[i].set_facecolor('#E57373')  # Light red
            elif i >= (len(patches)-3):  # Bins for positive differences > 5
                patches[i].set_facecolor('#E57373')  # Light red
            else:
                patches[i].set_facecolor('#81C784')  # Light green

        ax1.set_xlabel('Selisih Total')
        ax1.set_ylabel('Jumlah Transaksi')
        ax1.set_title('Distribusi Selisih')

        # Add annotations for bin counts
        for i in range(len(n)):
            if n[i] > 0:
                ax1.text((bins[i]+bins[i+1])/2, n[i]+0.1, int(n[i]),
                        ha='center', va='bottom', fontsize=9)

        ax1.grid(axis='y', alpha=0.3)

        # Second plot: Pie chart of significant vs minor differences
        sig_diff = len(diff_data[diff_data['TOTAL_DIFF'].abs() > 5])
        minor_diff = len(diff_data) - sig_diff

        labels = ['Selisih Signifikan (>5)', 'Selisih Kecil (≤5)']
        sizes = [sig_diff, minor_diff]
        colors = ['#E57373', '#81C784']
        explode = (0.1, 0)  # Explode the 1st slice (significant differences)

        ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax2.set_title('Proporsi Selisih Signifikan vs Kecil')

        # Add total count annotation
        ax2.text(0, -1.2, f'Total Transaksi dengan Selisih: {len(diff_data)}',
                ha='center', va='center', fontsize=10, fontweight='bold')

        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the title

        # Save the histogram
        os.makedirs(output_dir, exist_ok=True)
        if kerani_name:
            filename = f'diff_histogram_{kerani_name.replace(" ", "_").lower()}.png'
        else:
            filename = 'diff_histogram_all.png'
        diff_histogram_path = os.path.join(output_dir, filename)
        plt.savefig(diff_histogram_path, dpi=300, bbox_inches='tight')
        plt.close()

        logging.info(f"Difference histogram saved to {diff_histogram_path}")
        return diff_histogram_path

    except Exception as e:
        logging.error(f"Error creating difference histogram: {e}")
        print(f"Error creating difference histogram: {e}")
        return None

def create_kerani_scatter(data, kerani_name, output_dir):
    """
    Create scatter plot for a specific kerani comparing their values against Mandor/Asisten.

    Args:
        data: DataFrame with transaction data
        kerani_name: Name of the kerani to analyze
        output_dir: Directory to save the plot

    Returns:
        str: Path to the saved plot image
    """
    try:
        # Filter data for the specific kerani
        kerani_data = data[data['NAME_1'] == kerani_name].copy()

        if kerani_data.empty:
            logging.warning(f"No data available for kerani: {kerani_name}")
            return None

        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Analisis Transaksi Kerani: {kerani_name}', fontsize=16)

        # Columns to analyze
        bunch_columns = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
                        'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT', 'TOTAL']

        # Select the TOTAL column and the top 3 columns with the most differences for this kerani
        diff_counts = {}
        for col in bunch_columns:
            if col != 'TOTAL':  # Skip TOTAL for now
                diff_col = f'{col}_DIFF'
                if diff_col in kerani_data.columns:
                    diff_counts[col] = (kerani_data[diff_col] != 0).sum()

        # Sort columns by difference count
        top_columns = sorted(diff_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_column_names = [item[0] for item in top_columns]

        # Always include TOTAL as the 4th column
        selected_columns = top_column_names + ['TOTAL']

        # Create scatter plots for each selected column
        for i, col in enumerate(selected_columns):
            row, col_idx = divmod(i, 2)
            ax = axs[row, col_idx]

            col1 = f'{col}_1'  # Kerani value
            col2 = f'{col}_2'  # Mandor/Asisten value
            diff_col = f'{col}_DIFF'

            if col1 in kerani_data.columns and col2 in kerani_data.columns:
                # Separate data with and without differences
                has_diff = kerani_data[diff_col] != 0 if diff_col in kerani_data.columns else pd.Series(False, index=kerani_data.index)
                sig_diff = kerani_data[diff_col].abs() > 5 if diff_col in kerani_data.columns else pd.Series(False, index=kerani_data.index)
                minor_diff = has_diff & ~sig_diff
                no_diff = ~has_diff

                # Plot points without differences
                if no_diff.any():
                    ax.scatter(kerani_data.loc[no_diff, col1], kerani_data.loc[no_diff, col2],
                              color='blue', alpha=0.5, label='Tanpa Selisih')

                # Plot points with minor differences
                if minor_diff.any():
                    ax.scatter(kerani_data.loc[minor_diff, col1], kerani_data.loc[minor_diff, col2],
                              color='green', alpha=0.6, label='Selisih ≤5')

                # Plot points with significant differences
                if sig_diff.any():
                    ax.scatter(kerani_data.loc[sig_diff, col1], kerani_data.loc[sig_diff, col2],
                              color='red', alpha=0.7, label='Selisih >5')

                # Add diagonal line (perfect match)
                min_val = min(kerani_data[col1].min(), kerani_data[col2].min())
                max_val = max(kerani_data[col1].max(), kerani_data[col2].max())
                padding = (max_val - min_val) * 0.05  # 5% padding
                ax.plot([min_val-padding, max_val+padding], [min_val-padding, max_val+padding],
                       'k--', alpha=0.6, label='Nilai Sama')

                # Add labels and title
                ax.set_xlabel(f'Nilai Kerani (PM) - {col}')
                ax.set_ylabel(f'Nilai Mandor/Asisten (P1/P5) - {col}')
                ax.set_title(f'Perbandingan {col}')
                ax.grid(alpha=0.3)
                ax.legend(fontsize=8)

                # Set equal axis limits for better comparison
                max_limit = max(max_val+padding, 1)  # At least 1 to avoid empty plots
                ax.set_xlim(0, max_limit)
                ax.set_ylim(0, max_limit)

                # Add annotations for points with large differences
                for idx in kerani_data[sig_diff].index:
                    ax.annotate(f'{kerani_data.loc[idx, diff_col]:.1f}',
                               (kerani_data.loc[idx, col1], kerani_data.loc[idx, col2]),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=7, color='darkred')

        # Add summary statistics as text in a box
        total_trans = len(kerani_data)
        sig_diff_count = (kerani_data['TOTAL_DIFF'].abs() > 5).sum() if 'TOTAL_DIFF' in kerani_data.columns else 0
        minor_diff_count = ((kerani_data['TOTAL_DIFF'] != 0) & (kerani_data['TOTAL_DIFF'].abs() <= 5)).sum() if 'TOTAL_DIFF' in kerani_data.columns else 0
        avg_diff = kerani_data['TOTAL_DIFF'].abs().mean() if 'TOTAL_DIFF' in kerani_data.columns else 0

        summary_text = (
            f"Total Transaksi: {total_trans}\n"
            f"Transaksi dengan Selisih >5: {sig_diff_count} ({sig_diff_count/total_trans*100:.1f}%)\n"
            f"Transaksi dengan Selisih ≤5: {minor_diff_count} ({minor_diff_count/total_trans*100:.1f}%)\n"
            f"Rata-rata Selisih Absolut: {avg_diff:.2f}"
        )

        plt.figtext(0.5, 0.01, summary_text, ha="center", fontsize=10,
                   bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

        # Adjust layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.97])  # Make room for summary text

        # Save the plot
        os.makedirs(output_dir, exist_ok=True)
        plot_path = os.path.join(output_dir, f'kerani_{kerani_name.replace(" ", "_")}_scatter.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()

        logging.info(f"Kerani scatter plot saved to {plot_path}")
        return plot_path

    except Exception as e:
        logging.error(f"Error creating kerani scatter plot for {kerani_name}: {e}")
        print(f"Error creating kerani scatter plot for {kerani_name}: {e}")
        return None

def create_summary_info_box(data, styles):
    """
    Create a more compact summary information box with overall statistics

    Args:
        data: DataFrame with transaction data
        styles: ReportLab stylesheet

    Returns:
        Table object for the summary box
    """
    # Prepare data for summary
    total_trans = len(data)
    diff_data = data[data['TOTAL_DIFF'] != 0] if 'TOTAL_DIFF' in data.columns else pd.DataFrame()
    diff_trans = len(diff_data)
    sig_diff_trans = len(data[data['TOTAL_DIFF'].abs() > 5]) if 'TOTAL_DIFF' in data.columns else 0

    avg_diff = data['TOTAL_DIFF'].mean() if 'TOTAL_DIFF' in data.columns else 0
    max_diff = data['TOTAL_DIFF'].max() if 'TOTAL_DIFF' in data.columns else 0
    min_diff = data['TOTAL_DIFF'].min() if 'TOTAL_DIFF' in data.columns else 0

    pct_diff = (diff_trans / total_trans * 100) if total_trans > 0 else 0
    pct_sig_diff = (sig_diff_trans / total_trans * 100) if total_trans > 0 else 0

    # Create a more compact table for summary data
    summary_data = [
        ['Summary Analysis', ''],  # Removed bold formatting
        ['Total Transactions:', f'{total_trans:,}'],
        ['Transactions with Differences:', f'{diff_trans:,} ({pct_diff:.1f}%)'],
        ['Transactions with |Difference| > 5:', f'{sig_diff_trans:,} ({pct_sig_diff:.1f}%)'],
        ['Average Total Difference:', f'{avg_diff:.2f}'],
        ['Maximum Total Difference:', f'{max_diff:.2f}']
        # Removed Minimum Total Difference to save space
    ]

    # Create table with appropriate widths - match kerani table width (8+4+4+4+4=24cm)
    summary_table = Table(summary_data, colWidths=[16*cm, 8*cm])

    # Style the table with larger fonts and more padding
    summary_style = TableStyle([
        # Header style
        ('SPAN', (0, 0), (1, 0)),  # Span the header across both columns
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),  # Larger font
        ('BOTTOMPADDING', (0, 0), (1, 0), 4),  # More padding
        ('TOPPADDING', (0, 0), (1, 0), 4),     # More padding

        # Grid and borders
        ('BOX', (0, 0), (1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (1, 0), 1, colors.black),
        ('LINEAFTER', (0, 1), (0, -1), 0.5, colors.gray),

        # Row styling with larger fonts
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (1, -1), 9),  # Larger font
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),

        # More comfortable spacing
        ('BOTTOMPADDING', (0, 1), (1, -1), 2),  # More padding
        ('TOPPADDING', (0, 1), (1, -1), 2),     # More padding

        # Background color
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#F5F5F5')),
    ])

    # Apply alternating row colors
    for i in range(2, len(summary_data), 2):
        summary_style.add('BACKGROUND', (0, i), (1, i), colors.HexColor('#FFFFFF'))

    summary_table.setStyle(summary_style)
    return summary_table

def create_total_scatter_plot(data, output_dir, title_prefix=""):
    """
    Create scatter plot for TOTAL comparison across all kerani

    Args:
        data: DataFrame with transaction data
        output_dir: Directory to save the plot
        title_prefix: Optional prefix for the plot title

    Returns:
        str: Path to the saved plot image
    """
    try:
        # Create figure with smaller size to avoid exceeding pixel limits
        plt.figure(figsize=(10, 8), dpi=80)

        # Check if needed columns exist
        if 'TOTAL_1' not in data.columns or 'TOTAL_2' not in data.columns:
            logging.warning("Required columns for scatter plot are missing")
            return None

        # Separate data with different levels of differences
        has_diff = data['TOTAL_DIFF'] != 0 if 'TOTAL_DIFF' in data.columns else pd.Series(False, index=data.index)
        sig_diff = data['TOTAL_DIFF'].abs() > 5 if 'TOTAL_DIFF' in data.columns else pd.Series(False, index=data.index)
        minor_diff = has_diff & ~sig_diff
        no_diff = ~has_diff

        # Plot points without differences - larger markers
        if no_diff.any():
            plt.scatter(data.loc[no_diff, 'TOTAL_1'], data.loc[no_diff, 'TOTAL_2'],
                       color='blue', alpha=0.6, label='Tanpa Selisih', s=80)

        # Plot points with minor differences - larger markers
        if minor_diff.any():
            plt.scatter(data.loc[minor_diff, 'TOTAL_1'], data.loc[minor_diff, 'TOTAL_2'],
                       color='green', alpha=0.7, label='Selisih ≤5', s=100)

        # Plot points with significant differences - larger markers
        if sig_diff.any():
            plt.scatter(data.loc[sig_diff, 'TOTAL_1'], data.loc[sig_diff, 'TOTAL_2'],
                       color='red', alpha=0.8, label='Selisih >5', s=120, edgecolors='darkred', linewidths=1.5)

        # Add diagonal line (perfect match)
        min_val = min(data['TOTAL_1'].min(), data['TOTAL_2'].min())
        max_val = max(data['TOTAL_1'].max(), data['TOTAL_2'].max())
        padding = (max_val - min_val) * 0.05  # 5% padding
        plt.plot([min_val-padding, max_val+padding], [min_val-padding, max_val+padding],
                'k--', alpha=0.6, label='Nilai Sama')

        # Add labels and grid with improved styling (removed title to avoid duplication)
        plt.xlabel('Nilai Total Kerani (PM)', fontsize=16, fontweight='bold')
        plt.ylabel('Nilai Total Mandor/Asisten (P1/P5)', fontsize=16, fontweight='bold')
        # Removed title to avoid duplication with the PDF heading
        plt.grid(alpha=0.3, linestyle='--')
        plt.legend(fontsize=14, loc='upper left', framealpha=0.9, edgecolor='gray')

        # Improve tick labels - larger font and better spacing
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        # Add more tick marks for better scale readability
        from matplotlib.ticker import MaxNLocator
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))
        plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=10))

        # Add annotations for points with large differences with improved styling - larger font
        for idx in data[sig_diff].index:
            plt.annotate(f'{data.loc[idx, "TOTAL_DIFF"]:.1f}',
                       (data.loc[idx, 'TOTAL_1'], data.loc[idx, 'TOTAL_2']),
                       xytext=(7, 7), textcoords='offset points',
                       fontsize=14, color='darkred', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='darkred', alpha=0.7))

        # Equal aspect ratio for better visualization with improved scaling
        plt.axis('equal')

        # Adjust axis limits to focus on the data range with padding
        x_min, x_max = plt.xlim()
        y_min, y_max = plt.ylim()

        # Calculate range and add padding
        x_range = x_max - x_min
        y_range = y_max - y_min

        # Add 10% padding on each side
        plt.xlim(x_min - 0.1 * x_range, x_max + 0.1 * x_range)
        plt.ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

        # Add minor differences annotations - larger font
        for idx in data[minor_diff].index:
            plt.annotate(f'{data.loc[idx, "TOTAL_DIFF"]:.1f}',
                       (data.loc[idx, 'TOTAL_1'], data.loc[idx, 'TOTAL_2']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=12, color='darkgreen',
                       bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='darkgreen', alpha=0.5))

        # Adjust layout
        plt.tight_layout()

        # Save the plot with higher quality
        os.makedirs(output_dir, exist_ok=True)
        if title_prefix:
            plot_path = os.path.join(output_dir, f'total_scatter_{title_prefix.replace(" ", "_").lower()}.png')
        else:
            plot_path = os.path.join(output_dir, 'total_scatter_all.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight', format='png',
                  facecolor='white', edgecolor='none', transparent=False,
                  pad_inches=0.1, metadata={'Creator': 'Ifess Analysis Tool'})
        plt.close()

        logging.info(f"Total scatter plot saved to {plot_path}")
        return plot_path

    except Exception as e:
        logging.error(f"Error creating total scatter plot: {e}")
        print(f"Error creating total scatter plot: {e}")
        return None

def generate_advanced_pdf_report(analyzed_data, summary_stats, output_dir='reports', header_mode='rotated', database_name='', bulan='', tahun='', show_all_diff=True):
    """
    Generate a PDF report with detailed analysis of the comparison data.

    Parameters:
    - analyzed_data: DataFrame containing the comparison data with differences
    - summary_stats: Dictionary containing summary statistics
    - output_dir: Directory to save the output PDF
    - header_mode: Mode for column headers ('rotated', 'compact', or 'normal')
    - database_name: Nama database
    - bulan: Periode bulan
    - tahun: Periode tahun
    - show_all_diff: Tampilkan semua transaksi dengan selisih (jika False, hanya 10 teratas)

    Returns:
    - Path to the generated PDF file
    """
    try:
        # Filter for records with differences
        diff_data = analyzed_data.copy()
        has_diff = False

        # Check if there are any difference columns
        diff_cols = [col for col in analyzed_data.columns if col.endswith('_DIFF')]

        if diff_cols:
            # Create a mask for records with any non-zero difference
            diff_mask = analyzed_data[diff_cols].abs().sum(axis=1) > 0
            diff_data = analyzed_data[diff_mask].copy()
            has_diff = len(diff_data) > 0

        if not has_diff:
            logging.info("No differences found in the data for PDF report.")
            # Still keep the original data for other sections of the report
            diff_data = analyzed_data.copy()

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # PDF filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"comparison_report_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        # Create PDF document in landscape orientation with smaller top margin
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A4),
            leftMargin=1*cm,
            rightMargin=1*cm,
            topMargin=1*cm,  # Reduced top margin
            bottomMargin=1.5*cm
        )

        # Create styles for document
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        normal_style.fontSize = 9
        normal_style.leading = 12

        # Create a custom header style for the tables
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=normal_style,
            fontName='Helvetica-Bold',
            fontSize=8,      # Ukuran font yang lebih besar untuk keterbacaan
            alignment=1,     # Center
            wordWrap='CJK',  # Improved word wrapping
            leading=10,      # Spasi antar baris yang lebih besar
            leftIndent=2,    # Indentasi kiri yang lebih besar
            rightIndent=2,   # Indentasi kanan yang lebih besar
            spaceBefore=2,   # Tambahkan ruang sebelum paragraf
            spaceAfter=2     # Tambahkan ruang setelah paragraf
        )

        # Container for elements
        elements = []

        # Create nama_database - periode string
        periode_string = ""
        if database_name:
            periode_string += f"{database_name}"
        if bulan or tahun:
            if periode_string:
                periode_string += " - "
            if bulan:
                periode_string += f"{bulan}"
            if tahun:
                if bulan:
                    periode_string += " "
                periode_string += f"{tahun}"

        # Add title with database and period
        title_text = "Laporan Verifikasi Transaksi Ifess"
        if periode_string:
            title_text += f"\n{periode_string}"

        title = Paragraph(title_text, title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Add date range information
        if 'min_date' in summary_stats and 'max_date' in summary_stats:
            min_date = summary_stats['min_date']
            max_date = summary_stats['max_date']
            date_range_text = Paragraph(f"Periode Data: {min_date} - {max_date}", normal_style)
            elements.append(date_range_text)
            elements.append(Spacer(1, 0.2*cm))

        # Removed timestamp from the top of the document

        # Create kerani performance summary table (without heading) - MOVED TO TOP

        # Get unique kerani names
        if 'NAME_1' in analyzed_data.columns:
            kerani_names = sorted(analyzed_data['NAME_1'].unique())

            # Prepare kerani summary table
            kerani_table_headers = ["Nama Kerani", "Total Transaksi", "Beda > 5", "Beda ≤ 5", "% Selisih"]
            kerani_summary_data = [kerani_table_headers]

            # For storing kerani scatter plots to add after table
            kerani_scatter_paths = []

            # Calculate statistics for each kerani
            for kerani in kerani_names:
                # Skip empty or invalid names
                if pd.isna(kerani) or kerani == '' or kerani == '-':
                    continue

                # Filter data for this kerani
                kerani_data = analyzed_data[analyzed_data['NAME_1'] == kerani]

                # Calculate statistics
                total_trans = len(kerani_data)
                sig_diff = (kerani_data['TOTAL_DIFF'].abs() > 5).sum() if 'TOTAL_DIFF' in kerani_data.columns else 0
                minor_diff = ((kerani_data['TOTAL_DIFF'] != 0) & (kerani_data['TOTAL_DIFF'].abs() <= 5)).sum() if 'TOTAL_DIFF' in kerani_data.columns else 0
                pct_diff = ((sig_diff + minor_diff) / total_trans * 100) if total_trans > 0 else 0

                # Add row to table
                kerani_summary_data.append([
                    kerani,
                    str(total_trans),
                    str(sig_diff),
                    str(minor_diff),
                    f"{pct_diff:.1f}%"
                ])

                # Create scatter plot for TOTAL only for this kerani if they have enough transactions
                if total_trans >= 5:
                    scatter_path = create_total_scatter_plot(kerani_data, output_dir, f"Kerani {kerani}")
                    if scatter_path:
                        kerani_scatter_paths.append((kerani, scatter_path))

            # Create table if we have data
            if len(kerani_summary_data) > 1:
                # Set column widths - made wider
                kerani_col_widths = [8*cm, 4*cm, 4*cm, 4*cm, 4*cm]
                kerani_table = Table(kerani_summary_data, colWidths=kerani_col_widths, repeatRows=1)

                # Style the table - more compact
                kerani_table_style = TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),  # Larger font
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # More padding
                ('TOPPADDING', (0, 0), (-1, 0), 6),  # More padding

                # Grid and borders
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),

                # Default alignment and font
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align kerani names
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center align numbers
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),  # Larger font
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # More padding
                ('TOPPADDING', (0, 1), (-1, -1), 3),  # More padding
                ])

                # Highlight rows with high percentage of differences
                for i in range(1, len(kerani_summary_data)):
                    # Extract percentage from last column (remove % sign and convert to float)
                    pct_str = kerani_summary_data[i][4].replace('%', '')
                    try:
                        pct_val = float(pct_str)

                        if pct_val > 50:  # More than 50% have differences
                            kerani_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFCDD2'))  # Light red
                        elif pct_val > 20:  # 20-50% have differences
                            kerani_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF9C4'))  # Light yellow
                        elif i % 2 == 0:  # Alternate background for low percentage rows
                            kerani_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F5F5F5'))
                    except ValueError:
                        # In case of formatting issues
                        if i % 2 == 0:  # Just do alternating background
                            kerani_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F5F5F5'))

                # Apply table style
                kerani_table.setStyle(kerani_table_style)

                # First add summary information box at the very top
                summary_box = create_summary_info_box(analyzed_data, styles)
                elements.append(summary_box)
                elements.append(Spacer(1, 0.5*cm))

                # Then add kerani performance table
                elements.append(kerani_table)
                elements.append(Spacer(1, 0.5*cm))

                # Removed color legend explanation

        # Removed histogram for transactions with differences

            # Removed per-kerani histograms

        # Add explanation text for transaction tables
        elements.append(PageBreak())  # Start on a new page for transaction details
        transaction_detail_heading = Paragraph("Detail Transaksi dengan Selisih", heading_style)
        elements.append(transaction_detail_heading)
        elements.append(Spacer(1, 0.5*cm))

        # Removed explanatory text for transaction details

        # Add information about transactions with differences
        # Check if there are any difference columns
        diff_cols = [col for col in analyzed_data.columns if col.endswith('_DIFF')]

        # Count transactions with significant differences (> 5)
        sig_diff_mask = False
        for col in diff_cols:
            sig_diff_mask = sig_diff_mask | (analyzed_data[col].abs() > 5)

        sig_diff_count = sig_diff_mask.sum() if isinstance(sig_diff_mask, pd.Series) else 0

        if sig_diff_count > 0:
            diff_info_text = Paragraph(f"Ditemukan {sig_diff_count} transaksi dengan selisih signifikan (>5) dari total {len(analyzed_data)} transaksi.", normal_style)
            elements.append(diff_info_text)
        else:
            no_diff_text = Paragraph("Tidak ditemukan transaksi dengan selisih signifikan (>5) dalam periode ini.", normal_style)
            elements.append(no_diff_text)
        elements.append(Spacer(1, 0.5*cm))

        # Sort data by kerani name and then by absolute TOTAL_DIFF in descending order
        # Always show all transactions with differences
        display_data = diff_data.copy()
        if 'TOTAL_DIFF' in display_data.columns:
            display_data['ABS_TOTAL_DIFF'] = display_data['TOTAL_DIFF'].abs()

        # Group by kerani name
        if 'NAME_1' in display_data.columns:
            # Sort first by NAME_1 (kerani) and then by absolute difference
            display_data = display_data.sort_values(['NAME_1', 'ABS_TOTAL_DIFF'], ascending=[True, False])
        else:
            # If no NAME_1 column, just sort by absolute difference
            display_data = display_data.sort_values('ABS_TOTAL_DIFF', ascending=False)

        # Columns yang akan dibandingkan
        bunch_columns = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT', 'TOTAL']

        # Buat dictionary untuk nama header yang lebih pendek/singkat agar tidak tumpang tindih
        header_display_names = {
            'RIPEBCH': 'RIPE',
            'UNRIPEBCH': 'UNRIPE',
            'BLACKBCH': 'BLACK',
            'ROTTENBCH': 'ROTTEN',
            'LONGSTALKBCH': 'L.STALK',  # Memperpendek lagi
            'RATDMGBCH': 'RATDMG',
            'LOOSEFRUIT': 'LOOSE',
            'TOTAL': 'TOTAL'
        }

        # Buat dictionary untuk deskripsi tooltip yang lebih lengkap (untuk dokumentasi)
        header_descriptions = {
            'RIPEBCH': 'Jumlah Tandan Matang',
            'UNRIPEBCH': 'Jumlah Tandan Mentah',
            'BLACKBCH': 'Jumlah Tandan Hitam',
            'ROTTENBCH': 'Jumlah Tandan Busuk',
            'LONGSTALKBCH': 'Jumlah Tandan Tangkai Panjang',
            'RATDMGBCH': 'Jumlah Tandan Rusak Tikus',
            'LOOSEFRUIT': 'Jumlah Brondolan',
            'TOTAL': 'Total Keseluruhan'
        }

        # Initialize transaction counter
        transaction_counter = 0

        # Group data by kerani name first
        kerani_groups = {}
        for _, record in display_data.iterrows():
            # Check if this record has significant differences (> 5)
            has_significant_diff = False
            for col in record.index:
                if col.endswith('_DIFF') and abs(record[col]) > 5:
                    has_significant_diff = True
                    break

            # Skip records without significant differences
            if not has_significant_diff:
                continue

            # Get kerani name
            kerani_name = record['NAME_1'] if 'NAME_1' in record else 'Unknown'

            # Add record to appropriate kerani group
            if kerani_name not in kerani_groups:
                kerani_groups[kerani_name] = []
            kerani_groups[kerani_name].append(record)

        # Now process each kerani group
        for kerani_name, records in kerani_groups.items():
            # Add kerani header (more compact)
            kerani_header = Paragraph(f"<b>Kerani: {kerani_name}</b>", ParagraphStyle(
                'KeraniFontStyle',
                parent=heading_style,
                fontSize=8,  # Smaller font
                spaceAfter=0
            ))
            elements.append(kerani_header)
            elements.append(Spacer(1, 0.05*cm))  # Minimal spacing

            # Process each record for this kerani
            for record in records:
                # Get transaction info
                transno = record['TRANSNO'] if 'TRANSNO' in record else '-'
                transdate = record['TRANSDATE'] if 'TRANSDATE' in record else '-'
                fieldno = record['FIELDNO'] if 'FIELDNO' in record else '-'
                recordtag1 = record['RECORDTAG_1'] if 'RECORDTAG_1' in record else '-'
                recordtag2 = record['RECORDTAG_2'] if 'RECORDTAG_2' in record else '-'
                asisten_name = record['NAME_2'] if 'NAME_2' in record else 'Mandor/Asisten'

                # Get TRANSSTATUS info for header (preferring non-kerani status if available)
                transstatus_info = ""

                # First try to get status from non-kerani record (P1 or P5)
                if ('RECORDTAG_2' in record and record['RECORDTAG_2'] in ['P1', 'P5']):
                    if 'TRANSSTATUS_NAME_2' in record:
                        transstatus_info = f" | <b>STATUS:</b> {record['TRANSSTATUS_NAME_2']}"
                    elif 'TRANSSTATUS_2' in record:
                        transstatus_info = f" | <b>STATUS:</b> {record['TRANSSTATUS_2']}"
                # If not available, fall back to kerani status
                elif 'TRANSSTATUS_NAME_1' in record:
                    transstatus_info = f" | <b>STATUS:</b> {record['TRANSSTATUS_NAME_1']}"
                elif 'TRANSSTATUS_1' in record:
                    transstatus_info = f" | <b>STATUS:</b> {record['TRANSSTATUS_1']}"

                # Create more compact transaction header
                trans_header = Paragraph(f"<b>TRANSNO:</b> {transno} | <b>TRANSDATE:</b> {transdate} | <b>FIELDNO:</b> {fieldno} | <b>RECORDTAG:</b> {recordtag1}/{recordtag2}{transstatus_info}",
                                        ParagraphStyle('TransHeader',
                                                      parent=normal_style,
                                                      fontSize=7,  # Smaller font
                                                      spaceAfter=0))
                elements.append(trans_header)

                # Create table for this transaction
                # First, prepare the header row with column names
                header_row = [Paragraph('<b>Personil</b>', ParagraphStyle('HeaderCompact',
                                                                        fontName='Helvetica-Bold',
                                                                        fontSize=6,
                                                                        leading=8,
                                                                        alignment=1))]

                # Add bunch column headers
                for col in bunch_columns:
                    display_name = header_display_names[col]
                    header_row.append(Paragraph(f'<b>{display_name}</b>', ParagraphStyle('HeaderCompact',
                                                                                      fontName='Helvetica-Bold',
                                                                                      fontSize=6,
                                                                                      leading=8,
                                                                                      alignment=1)))

                # Get TRANSSTATUS info for the table (preferring non-kerani status)
                status_text = "-"

                # First try to get status from non-kerani record (P1 or P5)
                if ('RECORDTAG_2' in record and record['RECORDTAG_2'] in ['P1', 'P5']):
                    if 'TRANSSTATUS_NAME_2' in record:
                        status_text = record['TRANSSTATUS_NAME_2']
                    elif 'TRANSSTATUS_2' in record:
                        status_text = f"Status: {record['TRANSSTATUS_2']}"
                # If not available, fall back to kerani status
                elif 'TRANSSTATUS_NAME_1' in record:
                    status_text = record['TRANSSTATUS_NAME_1']
                elif 'TRANSSTATUS_1' in record:
                    status_text = f"Status: {record['TRANSSTATUS_1']}"

                # Get role information based on RECORDTAG
                role1 = ""
                role2 = ""

                if 'RECORDTAG_1' in record:
                    if record['RECORDTAG_1'] == 'PM':
                        role1 = " (KERANI)"
                    elif record['RECORDTAG_1'] == 'P1':
                        role1 = " (ASISTEN)"
                    elif record['RECORDTAG_1'] == 'P5':
                        role1 = " (MANDOR)"

                if 'RECORDTAG_2' in record:
                    if record['RECORDTAG_2'] == 'PM':
                        role2 = " (KERANI)"
                    elif record['RECORDTAG_2'] == 'P1':
                        role2 = " (ASISTEN)"
                    elif record['RECORDTAG_2'] == 'P5':
                        role2 = " (MANDOR)"

                # Create paragraphs with wrapping for all cells including role
                kerani_para = Paragraph(f"{kerani_name}{role1}", ParagraphStyle('KeraniFontStyle',
                                                                  fontName='Helvetica',
                                                                  fontSize=6,  # Smaller font
                                                                  leading=8,   # Reduced leading
                                                                  alignment=0))  # Left alignment
                asisten_para = Paragraph(f"{asisten_name}{role2}", ParagraphStyle('AsistenFontStyle',
                                                                    fontName='Helvetica',
                                                                    fontSize=6,  # Smaller font
                                                                    leading=8,   # Reduced leading
                                                                    alignment=0))  # Left alignment

                # Create status paragraph with wrapping
                status_para = Paragraph(status_text, ParagraphStyle('StatusFontStyle',
                                                              fontName='Helvetica',
                                                              fontSize=6,  # Smaller font
                                                              leading=8,   # Reduced leading
                                                              alignment=0))  # Left alignment

                # Add STATUS to header row
                header_row.insert(1, Paragraph('<b>STATUS</b>', ParagraphStyle('HeaderCompact',
                                                                            fontName='Helvetica-Bold',
                                                                            fontSize=6,
                                                                            leading=8,
                                                                            alignment=1)))

                # Create empty status cells for rows that don't need status
                empty_status = Paragraph("", ParagraphStyle('EmptyStatus',
                                                         fontName='Helvetica',
                                                         fontSize=6,
                                                         leading=8,
                                                         alignment=0))

                table_data = [
                    header_row,
                    [kerani_para, empty_status],  # Kerani row with empty status
                    [asisten_para, status_para],  # Asisten/Mandor row with status
                    ['Selisih', empty_status]  # Selisih row with empty status
                ]

                # Add values for each column
                for col in bunch_columns:
                    col1 = f'{col}_1'
                    col2 = f'{col}_2'
                    diff_col = f'{col}_DIFF'

                    if col1 in record and col2 in record and diff_col in record:
                        # Add values to rows
                        table_data[1].append(format_value(record[col1]))
                        table_data[2].append(format_value(record[col2]))
                        table_data[3].append(format_value(record[diff_col]))
                    else:
                        # If data doesn't exist, fill with '-'
                        table_data[1].append('-')
                        table_data[2].append('-')
                        table_data[3].append('-')

                # Set column widths with separate status column
                personil_width = 5*cm  # Back to original width since status has its own column
                status_width = 3*cm    # Width for the status column
                value_width = (landscape(A4)[0] - 2*cm - personil_width - status_width) / len(bunch_columns)
                col_widths = [personil_width, status_width] + [value_width] * len(bunch_columns)

                # Create row heights with more space for status text
                row_heights = [0.6*cm, 0.5*cm, 0.5*cm, 0.4*cm]

                # Create the table
                detail_table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)

                # Create table style
                detail_style = TableStyle([
                    # Header row style
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),

                    # Grid and borders
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),

                    # Default alignment
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Left align first column
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Center align value columns
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'), # Vertical middle for all rows
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),

                    # Garis di atas baris selisih
                    ('LINEABOVE', (0, 3), (-1, 3), 1.0, colors.black),
                ])

                # Highlight differences > 5 in red (only in data columns, not in status column)
                for i, col in enumerate(bunch_columns):
                    diff_col = f'{col}_DIFF'
                    if diff_col in record and abs(record[diff_col]) > 5:
                        col_idx = i + 2  # +2 because first column is 'Personil' and second is 'STATUS'
                        detail_style.add('BACKGROUND', (col_idx, 3), (col_idx, 3), colors.HexColor('#FFCDD2'))
                        detail_style.add('TEXTCOLOR', (col_idx, 3), (col_idx, 3), colors.darkred)
                        detail_style.add('FONTNAME', (col_idx, 3), (col_idx, 3), 'Helvetica-Bold')

                # Apply style to table
                detail_table.setStyle(detail_style)

                # Add table to elements
                elements.append(detail_table)
                elements.append(Spacer(1, 0.1*cm))  # Reduced spacing between tables

                transaction_counter += 1

            # Add minimal space between kerani groups
            elements.append(Spacer(1, 0.2*cm))

        # Header style already defined above

        # Removed column legend

            # Removed summary total section

        # Removed summary table for differences by column

        # Removed per-kerani scatter plots section

        # Add scatter plot at the very end
        elements.append(PageBreak())  # Start on a new page for the scatter plot

        # Add scatter plot for ALL kerani - TOTAL comparison on the last page
        scatter_heading = Paragraph("Perbandingan TOTAL", ParagraphStyle(
            'ScatterHeadingStyle',
            parent=styles['Normal'],
            fontSize=16,  # Larger font
            alignment=1,  # Center alignment
            spaceAfter=0.5*cm
        ))
        elements.append(scatter_heading)

        total_scatter_path = create_total_scatter_plot(analyzed_data, output_dir)
        if total_scatter_path and os.path.exists(total_scatter_path):
            # Make the scatter plot fill the entire page width
            page_width = landscape(A4)[0] - 2*cm  # Full page width minus margins
            page_height = landscape(A4)[1] - 4*cm  # Full page height minus margins and space for title
            scatter_img = Image(total_scatter_path, width=page_width, height=page_height)  # Maximum size
            elements.append(scatter_img)

        # Define header and footer
        def add_header_footer(canvas, doc):  # pylint: disable=unused-argument
            # doc parameter is required by ReportLab but not used in this function
            canvas.saveState()

            # Header - adjusted for landscape orientation
            canvas.setFont('Helvetica', 8)
            # Right side header
            canvas.drawString(1*cm, landscape(A4)[1] - 1*cm, "Ifess Transaction Verification Report")

            # Left side header - add generation timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            canvas.drawRightString(landscape(A4)[0] - 1*cm, landscape(A4)[1] - 1*cm, f"Generated: {timestamp}")

            # Footer with page number - adjusted for landscape orientation
            canvas.setFont('Helvetica', 8)
            # Right side footer - page number
            page_num = canvas.getPageNumber()
            canvas.drawRightString(landscape(A4)[0] - 1*cm, 1*cm, f"Page {page_num}")

            # Left side footer - database and period
            db_period = ""
            if database_name:
                db_period += f"{database_name}"
            if bulan or tahun:
                if db_period:
                    db_period += " - "
                if bulan and tahun:
                    db_period += f"{bulan} {tahun}"
                elif bulan:
                    db_period += f"{bulan}"
                elif tahun:
                    db_period += f"{tahun}"

            if db_period:
                canvas.drawString(1*cm, 1*cm, db_period)

            canvas.restoreState()

        # Build PDF
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

        logging.info(f"PDF report generated: {pdf_path}")
        return pdf_path

    except Exception as e:
        logging.error(f"Error generating PDF report: {e}")
        print(f"Error generating PDF report: {e}")
        return None

def format_value(value):
    """Format a numeric value for display in the table."""
    if pd.isna(value):
        return "0"
    elif isinstance(value, (int, float)):
        return f"{value:.1f}" if value != int(value) else f"{int(value)}"
    else:
        return str(value)
