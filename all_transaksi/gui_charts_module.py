"""
Chart Generation Module untuk Ifess Analysis GUI
Modul untuk membuat visualisasi data hasil analisis kinerja karyawan
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict
import os
from datetime import datetime

# Set matplotlib backend untuk GUI
import matplotlib
matplotlib.use('TkAgg')

class IfessChartsGenerator:
    def __init__(self):
        """Initialize chart generator."""
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Configure matplotlib for better display
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
        
    def generate_employee_performance_chart(self, analysis_results, output_path=None):
        """Generate employee performance charts."""
        if not analysis_results:
            return None
            
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analisis Kinerja Karyawan - Ifess Database', fontsize=16, fontweight='bold')
        
        # Sort employees by total created transactions
        sorted_employees = sorted(analysis_results.items(), 
                                key=lambda x: x[1]['total_created'], reverse=True)[:15]
        
        if sorted_employees:
            # 1. Verification Rate Chart
            names = [emp[0][:20] + '...' if len(emp[0]) > 20 else emp[0] for emp, _ in sorted_employees]
            rates = [stats['verification_rate'] for _, stats in sorted_employees]
            colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in rates]
            
            axes[0,0].barh(names, rates, color=colors)
            axes[0,0].set_xlabel('Tingkat Verifikasi (%)')
            axes[0,0].set_title('Top 15 Karyawan - Tingkat Verifikasi')
            axes[0,0].grid(axis='x', alpha=0.3)
            
            # Add values at the end of bars
            for i, rate in enumerate(rates):
                axes[0,0].text(rate + 1, i, f'{rate:.1f}%', va='center', fontsize=8)
            
            # 2. Total Transactions Chart
            totals = [stats['total_created'] for _, stats in sorted_employees]
            
            axes[0,1].barh(names, totals, color='skyblue')
            axes[0,1].set_xlabel('Jumlah Transaksi Dibuat')
            axes[0,1].set_title('Top 15 Karyawan - Total Transaksi Dibuat')
            axes[0,1].grid(axis='x', alpha=0.3)
            
            # Add values at the end of bars
            for i, total in enumerate(totals):
                axes[0,1].text(total + max(totals)*0.01, i, str(total), va='center', fontsize=8)
        
        # 3. Division Summary
        division_summary = self._get_division_summary(analysis_results)
        if division_summary:
            divisions = list(division_summary.keys())
            emp_counts = [division_summary[div]['employees'] for div in divisions]
            
            axes[1,0].bar(divisions, emp_counts, color='lightcoral')
            axes[1,0].set_ylabel('Jumlah Karyawan')
            axes[1,0].set_title('Jumlah Karyawan per Division')
            axes[1,0].grid(axis='y', alpha=0.3)
            axes[1,0].tick_params(axis='x', rotation=45)
            
            # Add values on top of bars
            for i, count in enumerate(emp_counts):
                axes[1,0].text(i, count + max(emp_counts)*0.01, str(count), 
                              ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 4. Role Distribution
        role_summary = self._get_role_summary(analysis_results)
        if role_summary:
            roles = list(role_summary.keys())
            role_counts = [role_summary[role]['employees'] for role in roles]
            avg_rates = [role_summary[role]['avg_verification_rate'] for role in roles]
            
            # Create bar chart with verification rates as colors
            colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in avg_rates]
            
            axes[1,1].bar(roles, role_counts, color=colors)
            axes[1,1].set_ylabel('Jumlah Karyawan')
            axes[1,1].set_title('Distribusi Karyawan per Role')
            axes[1,1].grid(axis='y', alpha=0.3)
            
            # Add dual axis for verification rates
            ax2 = axes[1,1].twinx()
            ax2.plot(roles, avg_rates, 'ro-', linewidth=2, markersize=8)
            ax2.set_ylabel('Rata-rata Tingkat Verifikasi (%)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            
            # Add values on bars
            for i, (count, rate) in enumerate(zip(role_counts, avg_rates)):
                axes[1,1].text(i, count + max(role_counts)*0.01, str(count), 
                              ha='center', va='bottom', fontsize=10, fontweight='bold')
                ax2.text(i, rate + 2, f'{rate:.1f}%', 
                        ha='center', va='bottom', fontsize=9, color='red')
        
        plt.tight_layout()
        
        # Save chart if output path provided
        if output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ifess_analysis_chart_{timestamp}.png"
            full_path = os.path.join(output_path, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            plt.close()
            return full_path
        else:
            plt.show()
            return None
            
    def generate_division_analysis_chart(self, analysis_results, output_path=None):
        """Generate division-focused analysis charts."""
        if not analysis_results:
            return None
            
        division_summary = self._get_division_summary(analysis_results)
        if not division_summary:
            return None
            
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analisis per Division - Ifess Database', fontsize=16, fontweight='bold')
        
        divisions = list(division_summary.keys())
        
        # 1. Transactions per Division
        transactions = [division_summary[div]['transactions'] for div in divisions]
        
        axes[0,0].bar(divisions, transactions, color='lightblue')
        axes[0,0].set_ylabel('Total Transaksi')
        axes[0,0].set_title('Total Transaksi per Division')
        axes[0,0].grid(axis='y', alpha=0.3)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        for i, trans in enumerate(transactions):
            axes[0,0].text(i, trans + max(transactions)*0.01, str(trans), 
                          ha='center', va='bottom', fontsize=10)
        
        # 2. Verification Rates per Division
        verification_rates = [division_summary[div]['verification_rate'] for div in divisions]
        colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in verification_rates]
        
        axes[0,1].bar(divisions, verification_rates, color=colors)
        axes[0,1].set_ylabel('Tingkat Verifikasi (%)')
        axes[0,1].set_title('Tingkat Verifikasi per Division')
        axes[0,1].grid(axis='y', alpha=0.3)
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].set_ylim(0, 100)
        
        for i, rate in enumerate(verification_rates):
            axes[0,1].text(i, rate + 2, f'{rate:.1f}%', 
                          ha='center', va='bottom', fontsize=10)
        
        # 3. Employee Distribution per Division (Pie Chart)
        emp_counts = [division_summary[div]['employees'] for div in divisions]
        
        axes[1,0].pie(emp_counts, labels=divisions, autopct='%1.1f%%', startangle=90)
        axes[1,0].set_title('Distribusi Karyawan per Division')
        
        # 4. Productivity vs Quality Scatter Plot
        productivity = transactions  # Total transactions as productivity metric
        quality = verification_rates  # Verification rate as quality metric
        
        scatter = axes[1,1].scatter(productivity, quality, 
                                   s=[emp*20 for emp in emp_counts],  # Size based on employee count
                                   alpha=0.7, c=range(len(divisions)), cmap='viridis')
        
        axes[1,1].set_xlabel('Produktivitas (Total Transaksi)')
        axes[1,1].set_ylabel('Kualitas (Tingkat Verifikasi %)')
        axes[1,1].set_title('Produktivitas vs Kualitas per Division')
        axes[1,1].grid(True, alpha=0.3)
        
        # Add division labels to scatter points
        for i, div in enumerate(divisions):
            axes[1,1].annotate(div, (productivity[i], quality[i]), 
                              xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.tight_layout()
        
        # Save chart if output path provided
        if output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ifess_division_analysis_{timestamp}.png"
            full_path = os.path.join(output_path, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            plt.close()
            return full_path
        else:
            plt.show()
            return None
            
    def generate_trend_analysis_chart(self, analysis_results, output_path=None):
        """Generate trend analysis charts."""
        # This would require time-series data, placeholder for now
        if not analysis_results:
            return None
            
        # Create a simple summary chart for now
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Extract verification rates and sort
        emp_names = list(analysis_results.keys())
        verification_rates = [stats['verification_rate'] for stats in analysis_results.values()]
        total_transactions = [stats['total_created'] for stats in analysis_results.values()]
        
        # Create scatter plot
        scatter = ax.scatter(total_transactions, verification_rates, 
                           alpha=0.7, s=60, c='blue')
        
        ax.set_xlabel('Total Transaksi Dibuat')
        ax.set_ylabel('Tingkat Verifikasi (%)')
        ax.set_title('Korelasi Produktivitas vs Tingkat Verifikasi')
        ax.grid(True, alpha=0.3)
        
        # Add trend line
        if len(total_transactions) > 1:
            z = np.polyfit(total_transactions, verification_rates, 1)
            p = np.poly1d(z)
            ax.plot(sorted(total_transactions), p(sorted(total_transactions)), 
                   "r--", alpha=0.8, linewidth=2, label='Trend Line')
            ax.legend()
        
        plt.tight_layout()
        
        # Save chart if output path provided
        if output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ifess_trend_analysis_{timestamp}.png"
            full_path = os.path.join(output_path, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            plt.close()
            return full_path
        else:
            plt.show()
            return None
            
    def _get_division_summary(self, analysis_results):
        """Get summary statistics by division."""
        division_summary = defaultdict(lambda: {
            'employees': 0,
            'transactions': 0,
            'verified': 0,
            'verification_rate': 0
        })
        
        for emp_name, stats in analysis_results.items():
            div = stats['division']
            division_summary[div]['employees'] += 1
            division_summary[div]['transactions'] += stats['total_created']
            division_summary[div]['verified'] += stats['total_verified']
        
        # Calculate verification rates
        for div in division_summary:
            if division_summary[div]['transactions'] > 0:
                division_summary[div]['verification_rate'] = (
                    division_summary[div]['verified'] / 
                    division_summary[div]['transactions']
                ) * 100
        
        return dict(division_summary)
        
    def _get_role_summary(self, analysis_results):
        """Get summary statistics by role."""
        role_summary = defaultdict(lambda: {
            'employees': 0,
            'transactions': 0,
            'verified': 0,
            'avg_verification_rate': 0,
            'verification_rates': []
        })
        
        for emp_name, stats in analysis_results.items():
            role = stats['role']
            role_summary[role]['employees'] += 1
            role_summary[role]['transactions'] += stats['total_created']
            role_summary[role]['verified'] += stats['total_verified']
            role_summary[role]['verification_rates'].append(stats['verification_rate'])
        
        # Calculate average verification rates
        for role in role_summary:
            if role_summary[role]['verification_rates']:
                role_summary[role]['avg_verification_rate'] = (
                    sum(role_summary[role]['verification_rates']) / 
                    len(role_summary[role]['verification_rates'])
                )
        
        return dict(role_summary)
        
    def export_chart_data(self, analysis_results, output_path):
        """Export chart data to Excel for further analysis."""
        if not analysis_results:
            return None
            
        try:
            # Create detailed DataFrame
            data = []
            for emp_name, stats in analysis_results.items():
                data.append({
                    'Employee Name': emp_name,
                    'Role': stats['role'],
                    'Division': stats['division'],
                    'Total Transactions': stats['total_created'],
                    'Verified Transactions': stats['total_verified'],
                    'Verification Rate (%)': round(stats['verification_rate'], 2),
                    'Unique Transactions': stats['unique_transactions']
                })
            
            df_detailed = pd.DataFrame(data)
            
            # Create summary DataFrames
            division_summary = self._get_division_summary(analysis_results)
            df_division = pd.DataFrame.from_dict(division_summary, orient='index')
            
            role_summary = self._get_role_summary(analysis_results)
            df_role = pd.DataFrame.from_dict(role_summary, orient='index')
            
            # Save to Excel with multiple sheets
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ifess_chart_data_{timestamp}.xlsx"
            full_path = os.path.join(output_path, filename)
            
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                df_detailed.to_excel(writer, sheet_name='Detailed Data', index=False)
                df_division.to_excel(writer, sheet_name='Division Summary', index=True)
                df_role.to_excel(writer, sheet_name='Role Summary', index=True)
            
            return full_path
            
        except Exception as e:
            print(f"Error exporting chart data: {e}")
            return None