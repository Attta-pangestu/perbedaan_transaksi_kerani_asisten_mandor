# SISTEM LAPORAN VERIFIKASI FFB - TEMPLATE MANAGER

Sistem desktop untuk generating laporan verifikasi transaksi FFB scanner multi-estate dengan template manager yang komprehensif.

## 🏗️ ARSITEKTUR SISTEM

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Desktop GUI   │    │  Template Manager │    │ Report Generator│
│   (main_gui.py) │◄──►│ (template_manager.py)│◄──►│(report_generator.py)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ FFB Analysis    │
                       │ Engine          │
                       │(ffb_analysis_   │
                       │engine.py)       │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Database        │
                       │ Connectivity    │
                       │(firebird_       │
                       │connector.py)    │
                       └─────────────────┘
```

## 📋 FITUR UTAMA

### 1. Template Management System
- **Template JSON**: Konfigurasi laporan dalam format JSON terstruktur
- **Dynamic Parameters**: Parameter laporan yang dapat dikonfigurasi
- **Query SQL**: Query database terintegrasi dalam template
- **Business Logic**: Logika perhitungan dan validasi dalam template
- **Report Structure**: Struktur laporan lengkap dengan styling

### 2. Comprehensive Template Structure
Template mengandung informasi lengkap:
- **Business Context**: Tujuan, konsep kunci, aturan bisnis
- **Database Schema**: Struktur tabel dan field yang digunakan
- **SQL Queries**: Query untuk ekstraksi data dengan penjelasan
- **Data Processing**: Algoritma analisis 5-langkah
- **Verification Logic**: Logika deteksi duplikat dan verifikasi
- **Performance Metrics**: Formula KPI dan target performa
- **Report Structure**: Layout tabel, styling, dan kalkulasi
- **Business Interpretation**: Panduan interpretasi hasil

### 3. Analysis Engine
- **Duplicate Detection**: Identifikasi transaksi terverifikasi berdasarkan TRANSNO
- **Role-based Analysis**: Analisis kinerja per role (Kerani, Mandor, Asisten)
- **Input Difference Analysis**: Deteksi perbedaan input data
- **Multi-estate Support**: Analisis multi-estate dalam satu laporan
- **Status 704 Filter**: Filter khusus untuk bulan Mei 2024

### 4. Desktop Application
- **Multi-tab Interface**: Tab Generate Laporan, Template Manager, Konfigurasi
- **Real-time Progress**: Progress bar dan log proses real-time
- **Parameter Configuration**: Dynamic parameter controls berdasarkan template
- **Template Selection**: Dropdown untuk pemilihan template
- **Output Management**: Otomatis buka folder output

## 🚀 INSTALASI DAN SETUP

### Prerequisites
```bash
# Install required packages
pip install tkcalendar pandas reportlab
```

### File Structure
```
Reporting_System_Ifes/
├── src/
│   ├── main_gui.py              # Main GUI application
│   ├── template_manager.py      # Template management
│   ├── report_generator.py      # PDF report generation
│   └── ffb_analysis_engine.py   # Analysis logic engine
├── templates/
│   └── laporan_verifikasi_multi_estate.json  # Main template
├── logs/                        # Application logs
├── reports/                     # Generated reports
├── assets/                      # Company logo, etc.
├── config.json                  # Database configuration
├── requirements.txt             # Python dependencies
├── start_app.py                # Application launcher
└── README.md                   # This file
```

### Running the Application
```bash
# Method 1: Using start script
python start_app.py

# Method 2: Direct execution
cd src
python main_gui.py
```

## 📊 TEMPLATE COMPREHENSIVE STRUCTURE

### Template JSON Contains:
1. **Business Context**
   - Purpose dan objectives
   - Key concepts (TRANSNO, RECORDTAG, verification logic)
   - Business rules dan stakeholders

2. **Database Schema**
   - Table structures (FFBSCANNERDATA, OCFIELD, CRDIVISION, EMP)
   - Field explanations dan purposes
   - Data flow documentation

3. **SQL Queries**
   - Employee mapping query
   - Division detection query
   - Main analysis query dengan joins
   - Query purposes dan expected outputs

4. **Data Processing Logic**
   - 5-step analysis algorithm
   - Verification logic details
   - Difference calculation methods
   - Performance metrics formulas

5. **Report Structure**
   - Table column definitions
   - Styling configuration
   - Calculations and formulas
   - Business interpretation guidelines

## 🔧 KONFIGURASI

### Database Configuration (config.json)
```json
{
  "PGE 1A": "path/to/database.fdb",
  "PGE 1B": "path/to/database.fdb",
  ...
}
```

### Template Parameters
- **START_DATE**: Tanggal mulai periode laporan
- **END_DATE**: Tanggal akhir periode laporan
- **ESTATES**: Pilihan estate yang akan dianalisis
- **USE_STATUS_704_FILTER**: Filter khusus bulan Mei

## 📈 ALUR ANALISIS

### Step 1: Data Collection
- Connect ke setiap estate database
- Detect monthly tables (FFBSCANNERDATA01-12)
- Execute query untuk setiap divisi
- Combine data dari multiple tables

### Step 2: Duplicate Detection
- Identify duplicates berdasarkan TRANSNO
- Generate set of verified TRANSNO values
- Priority: P1 (Asisten) > P5 (Mandor)

### Step 3: Performance Calculation
- Calculate metrics per employee role
- Verification rates untuk Kerani
- Participation rates untuk Mandor/Asisten

### Step 4: Difference Analysis
- Compare field values between Kerani and verifiers
- Apply TRANSSTATUS 704 filter untuk Mei 2024
- Count transactions dengan input differences

### Step 5: Aggregation
- Aggregate results per employee, division, estate
- Generate summary statistics
- Calculate grand totals

## 📋 METRIK KINERJA

### Kerani KPIs
- **Verification Rate**: % transaksi yang diverifikasi (Target: >90%)
- **Accuracy Rate**: % transaksi tanpa perbedaan (Target: >95%)

### Mandor/Asisten KPIs
- **Participation Rate**: % keterlibatan verifikasi (Target: >80%)

### Overall Health Indicators
- **Excellent**: >90% verification AND <10% differences
- **Good**: >80% verification AND <15% differences
- **Needs Attention**: <80% verification OR >15% differences
- **Critical**: <70% verification OR >20% differences

## 🎨 STYLING LAPORAN

### Color Coding
- **KERANI**: Red theme (critical data entry role)
- **MANDOR**: Green theme (verification role)
- **ASISTEN**: Blue theme (verification role)
- **SUMMARY**: Professional blue (highlights)

### Visual Elements
- Alternating row colors untuk readability
- Role-based color coding
- Emphasis on key metrics
- Professional corporate design

## 🔍 BUSINESS INTERPRETATION

### High Verification Rate (>90%)
- Excellent data entry quality
- Efficient verification process
- Good system adoption

### High Difference Rate (>15%)
- Potential training needs
- System usability issues
- Process improvement opportunities

### Low Participation Rate (<60%)
- Insufficient oversight
- Resource allocation issues
- Process compliance problems

## 📝 CUSTOMIZATION

### Creating New Templates
1. Copy existing template
2. Modify business context dan parameters
3. Update SQL queries sesuai kebutuhan
4. Adjust report structure dan styling
5. Test dengan sample data

### Adding New Metrics
1. Define calculation formula
2. Add to performance metrics section
3. Update report structure
4. Add business interpretation guidelines

## 🐛 TROUBLESHOOTING

### Common Issues
1. **Database Connection Failed**
   - Check file path di config.json
   - Verify database file exists
   - Check isql.exe availability

2. **No Data Found**
   - Verify date range contains data
   - Check estate database content
   - Validate monthly table existence

3. **Template Loading Error**
   - Validate JSON syntax
   - Check required fields
   - Verify file permissions

4. **PDF Generation Failed**
   - Check output directory permissions
   - Verify reportlab installation
   - Check template structure validity

### Logging
- Application logs: `logs/app.log`
- Error messages displayed in GUI
- Detailed processing information in log widget

## 🔄 MAINTENANCE

### Regular Tasks
- Review template parameters quarterly
- Update business rules as needed
- Monitor performance metric targets
- Backup configuration files

### Updates
- Template versioning untuk perubahan
- Database schema updates documentation
- Performance metric adjustment
- Business rule refinement

## 📞 SUPPORT

### Technical Support
- Check logs untuk error details
- Verify template JSON structure
- Validate database connectivity
- Review parameter configuration

### Business Support
- Review metric interpretations
- Adjust KPI targets as needed
- Update business rules
- Customize reporting requirements

---

**Version**: 2.0.0
**Last Updated**: 2025-10-29
**Compatible with**: Original gui_multi_estate_ffb_analysis.py logic