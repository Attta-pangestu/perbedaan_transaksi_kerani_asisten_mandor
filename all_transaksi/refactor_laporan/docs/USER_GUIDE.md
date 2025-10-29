# FFB Analysis System - User Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Configuration](#configuration)
5. [Using the Application](#using-the-application)
6. [Understanding Reports](#understanding-reports)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## System Overview

FFB Analysis System adalah aplikasi untuk menganalisis kualitas data entry transaksi FFB (Fresh Fruit Bunch) Scanner dari multiple estate. Sistem ini membantu memantau performa karyawan dan mengidentifikasi isu kualitas data.

### Key Features

- **Multi-Estate Analysis**: Analisis simultan untuk beberapa estate
- **Transaction Verification**: Deteksi otomatis transaksi yang terverifikasi
- **Performance Monitoring**: Tracking performa individual karyawan
- **Professional Reports**: Generate laporan PDF yang komprehensif
- **Data Quality Analysis**: Identifikasi perbedaan dan isu kualitas data

### Supported Estates

System ini support untuk 10 estates:
- PGE 1A, PGE 1B, PGE 2A, PGE 2B
- IJL, DME
- Are B2, Are B1, Are A, Are C

## Installation

### System Requirements

**Minimum Requirements:**
- Windows 10 or higher
- Python 3.8 or higher (recommended: Python 3.10+)
- 4GB RAM
- 2GB free disk space
- Firebird database server

**Software Dependencies:**
- Microsoft Excel (untuk export functionality)
- PDF reader (Adobe Acrobat Reader atau sejenisnya)

### Installation Steps

1. **Download the Application**
   ```
   Copy folder `refactor_laporan` ke lokasi yang diinginkan
   ```

2. **Install Python Dependencies**
   ```bash
   cd refactor_laporan
   pip install -r requirements.txt
   ```

3. **Verify Firebird Installation**
   Pastikan Firebird database sudah terinstall dan isql.exe dapat diakses

4. **Test Database Connections**
   ```bash
   python main.py --test-connections
   ```

5. **Launch Application**
   ```bash
   python main.py
   ```

### Automatic Installation (Windows)

Run `install.bat` untuk otomatis:
- Install Python dependencies
- Create desktop shortcut
- Test database connections

## Getting Started

### First Time Setup

1. **Launch the Application**
   Double-click `main.py` atau run dari command line

2. **Configure Database Paths**
   - Klik "Configuration" tab
   - Verify semua estate database paths
   - Update path jika diperlukan
   - Click "Test All Connections"

3. **Verify Data Availability**
   - Select estate dan date range
   - Click "Check Data Availability"
   - Verify ada data untuk periode yang dipilih

### Basic Workflow

1. **Select Estates**
   - Pilih estates yang akan dianalisis
   - Bisa single estate atau multiple estates

2. **Set Date Range**
   - Pilih start dan end date untuk analisis
   - System otomatis detect monthly tables

3. **Run Analysis**
   - Click "Start Analysis"
   - Monitor progress di progress bar
   - Tunggu hingga analysis complete

4. **Generate Reports**
   - Click "Generate Report" untuk PDF report
   - Choose output location
   - Report akan otomatis dibuka setelah generated

## Configuration

### Database Configuration

Configuration disimpan di `src/config/estate_config.json`:

```json
{
    "PGE 1A": "D:/Database/PTRJ_P1A.FDB",
    "PGE 1B": "D:/Database/PTRJ_P1B.FDB",
    ...
}
```

### Updating Database Paths

1. **Via GUI**
   - Go to Configuration tab
   - Select estate dari dropdown
   - Browse ke database file
   - Click "Update Path"

2. **Manual Edit**
   - Edit `src/config/estate_config.json`
   - Update path yang diperlukan
   - Save file

### Report Configuration

Report settings di `src/config/report_config.json`:

```json
{
    "company": {
        "name": "PT. Rebinmas",
        "address": "Jakarta, Indonesia"
    },
    "report": {
        "title": "FFB SCANNER DATA ANALYSIS REPORT"
    }
}
```

## Using the Application

### Main Interface

**Tab 1: Analysis**
- Estate selection
- Date range picker
- Analysis controls
- Progress indicator

**Tab 2: Configuration**
- Database path management
- Connection testing
- System information

**Tab 3: Results**
- Analysis results display
- Verification summary
- Performance metrics

### Analysis Process

#### Step 1: Select Estates
- Checkbox untuk select/deselect estates
- "Select All" untuk semua estates
- Estates dengan connection error ditandai merah

#### Step 2: Set Date Range
- Use calendar widgets untuk select dates
- Atau input manual format YYYY-MM-DD
- System validate date range

#### Step 3: Configure Analysis Options
- **Include Discrepancies**: Include discrepancy analysis
- **Detailed Employee Report**: Generate per-employee details
- **Summary Only**: Generate summary report only

#### Step 4: Run Analysis
- Click "Start Analysis" button
- Progress bar menunjukkan status
- Real-time log di text area
- Cancel button untuk stop analysis

#### Step 5: Review Results
- Summary statistics ditampilkan
- Verification rate per estate
- Top/bottom performers
- Discrepancy summary

### Generating Reports

#### PDF Report Options
1. **Comprehensive Report**: All analysis results
2. **Summary Report**: Key metrics only
3. **Employee Performance**: Per-employee details
4. **Discrepancy Report**: Data quality issues

#### Report Contents
- **Executive Summary**: High-level overview
- **Methodology**: Analysis approach
- **Results**: Detailed findings
- **Recommendations**: Action items
- **Appendices**: Raw data tables

## Understanding Reports

### Report Sections

#### 1. Cover Page
- Company information
- Report title and date
- Analysis period
- Prepared by information

#### 2. Executive Summary
- Overall verification rate
- Key findings
- Performance highlights
- Critical issues

#### 3. Methodology
- Data sources
- Analysis period
- Verification rules
- Calculation methods

#### 4. Analysis Results

**Verification Summary**
- Total transactions analyzed
- Verified vs unverified breakdown
- Verification rate per estate
- Trend analysis

**Employee Performance**
- Top performers table
- Bottom performers table
- Performance distribution
- Departmental breakdown

**Data Quality Analysis**
- Discrepancy summary
- Common error patterns
- Data completeness metrics
- Quality recommendations

#### 5. Detailed Tables
- Transaction-level details
- Employee performance metrics
- Discrepancy listings
- Raw data appendix

### Interpreting Metrics

#### Verification Rate
- **Excellent**: 95%+ - High data quality
- **Good**: 85-94% - Acceptable quality
- **Fair**: 70-84% - Needs improvement
- **Poor**: 50-69% - Significant issues
- **Very Poor**: <50% - Critical issues

#### Performance Score
Based on verification rate:
- **Excellent**: Consistently high verification
- **Good**: Generally reliable data entry
- **Fair**: Occasional quality issues
- **Poor**: Frequent data issues
- **Very Poor**: Systematic data problems

#### Discrepancy Severity
- **Critical**: Affects weight or quantity
- **High**: Affects operational data
- **Medium**: Affects reporting data
- **Low**: Minor administrative issues

## Troubleshooting

### Common Issues

#### Database Connection Errors

**Problem**: "Cannot connect to database"
**Solutions**:
1. Verify database path di Configuration tab
2. Check Firebird service status
3. Verify isql.exe accessibility
4. Test connection untuk setiap estate

**Problem**: "isql.exe not found"
**Solutions**:
1. Install Firebird client tools
2. Add Firebird bin directory ke PATH
3. Copy isql.exe ke application folder

#### Data Issues

**Problem**: "No data found for selected period"
**Solutions**:
1. Verify monthly tables exist (FFBSCANNERDATA[MM])
2. Check data availability di target period
3. Try shorter date range
4. Verify estate ada data untuk period

**Problem**: "Invalid date format"
**Solutions**:
1. Use calendar widgets instead of manual input
2. Verify format YYYY-MM-DD
3. Check date range validity

#### Performance Issues

**Problem**: Analysis runs very slow
**Solutions**:
1. Reduce date range
2. Select fewer estates
3. Close other applications
4. Check available memory

**Problem**: Application freezes
**Solutions**:
1. Wait longer for large datasets
2. Use Task Manager to monitor
3. Restart application
4. Check database server performance

#### Report Generation Issues

**Problem**: "Cannot generate PDF report"
**Solutions**:
1. Check write permissions di output folder
2. Verify sufficient disk space
3. Close other PDF applications
4. Try different output location

### Error Messages

#### Configuration Errors
- **"Estate path not found"**: Update database path di Configuration
- **"Invalid configuration file"**: Delete config files and restart

#### Data Errors
- **"Missing required columns"**: Check database schema
- **"Invalid data format"**: Verify data integrity

#### System Errors
- **"Memory error"**: Reduce data range or restart application
- **"Permission denied"**: Run as administrator

### Getting Help

#### Log Files
Check log files di `logs/` folder:
- `ffb_analysis_YYYYMMDD.log`: Daily application logs
- Error details dengan timestamps
- Stack traces untuk debugging

#### Diagnostic Information
Use `--test-connections` command untuk diagnostic:
```bash
python main.py --test-connections
```

#### Support Information
Contact technical support dengan:
- Error message screenshots
- Log files
- System information
- Steps to reproduce

## FAQ

### General Questions

**Q: Apa itu FFB Analysis System?**
A: Sistem untuk menganalisis kualitas data entry transaksi FFB Scanner dan monitoring performa karyawan.

**Q: Estates apa saja yang didukung?**
A: 10 estates: PGE 1A, 1B, 2A, 2B, IJL, DME, Are B2, B1, A, C.

**Q: Bagaimana sistem verifikasi bekerja?**
A: Transaksi dianggap verified jika ada entry dari Kerani (PM) dan Mandor (P1) atau Asisten (P5) dengan TRANSNO sama.

### Data Questions

**Q: Data dari periode berapa yang tersedia?**
A: Tergantung ketersediaan data di masing-masing estate. Check dengan "Check Data Availability" feature.

**Q: Mengapa ada transaksi yang unverified?**
A: Transaksi PM tidak memiliki corresponding entry dari P1 atau P5 untuk verification.

**Q: Apa itu discrepancies?**
A: Perbedaan data antar entries dengan TRANSNO sama (misal: weight berbeda antara PM dan P1).

### Technical Questions

**Q: Apakah perlu install Firebird?**
A: Ya, Firebird database server harus terinstall dengan isql.exe accessible.

**Q: Bagaimana mengupdate database paths?**
A: Via Configuration tab atau edit manual `src/config/estate_config.json`.

**Q: Can sistem run tanpa GUI?**
A: Saat ini sistem memerlukan GUI untuk operation.

### Report Questions

**Q: Format laporan apa yang tersedia?**
A: PDF reports dengan professional styling dan company branding.

**Q: Bagaimana interpret verification rate?**
A: Excellent: 95%+, Good: 85-94%, Fair: 70-84%, Poor: 50-69%, Very Poor: <50%.

**Q: Can reports di-customize?**
A: Ya, edit `src/config/report_config.json` untuk customizing report content dan styling.

### Performance Questions

**Q: Berapa lama analysis biasanya berjalan?**
A: Tergantung data volume:
- 1 month, 1 estate: 1-5 minutes
- 3 months, multiple estates: 10-30 minutes
- Large datasets: 30+ minutes

**Q: Mengapa analysis lambat?**
A: Large data volume, slow database connection, or limited system resources.

### Troubleshooting Questions

**Q: Application tidak start?**
A: Check Python installation, dependencies, dan run sebagai administrator.

**Q: Database connection gagal?**
A: Verify database paths, Firebird service, dan network connectivity.

**Q: Reports tidak tergenerate?**
A: Check disk space, write permissions, dan close PDF applications.

---

For additional support or questions, contact the system administrator or technical support team.