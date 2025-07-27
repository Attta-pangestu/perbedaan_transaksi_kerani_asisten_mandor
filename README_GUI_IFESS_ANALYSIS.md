# Ifess Database Analysis Tool - GUI Version

## Overview
GUI Tool yang user-friendly untuk menganalisis database Ifess dengan fokus pada kinerja karyawan dan analisis division. Tool ini menyediakan interface grafis yang intuitif untuk melakukan analisis mendalam terhadap data transaksi FFB Scanner.

## Features Utama

### 1. **Configuration Management**
- Database path configuration dengan file browser
- ISQL path configuration (auto-detect atau manual)
- Period selection (month/year)
- Analysis type selection
- Division filtering capabilities
- Save/Load configuration

### 2. **Database Integration**
- Test connection functionality
- Automatic division data loading
- Enhanced SQL queries dengan join tables:
  - FFBSCANNERDATA{MM} (main transaction data)
  - OCFIELD (field data untuk division mapping)
  - CRDIVISION (division names)
  - EMP (employee mapping)

### 3. **Analysis Capabilities**
- **Employee Performance Analysis**: Analisis kinerja per karyawan
- **Division Summary**: Ringkasan per division
- **Transaction Analysis**: Analisis transaksi detail
- **Verification Status**: Status verifikasi transaksi

### 4. **Real-time Analysis**
- Multi-threaded analysis untuk UI responsiveness
- Real-time progress tracking
- Comprehensive logging system
- Stop/start analysis control

### 5. **Results Visualization**
- Tabular results display dengan sorting
- Summary statistics
- Division-based filtering
- Export capabilities (Excel, CSV, PDF)

### 6. **Advanced Charting**
- Employee performance charts
- Division analysis charts
- Trend analysis charts
- Data export untuk custom analysis

## Installation & Requirements

### Prerequisites
```bash
# Python 3.7+
pip install pandas
pip install openpyxl
pip install matplotlib
pip install seaborn
pip install numpy

# Tkinter (usually included with Python)
```

### Files Required
- `gui_ifess_analysis.py` - Main GUI application
- `gui_charts_module.py` - Chart generation module
- `firebird_connector.py` - Database connector (existing)
- `run_gui_ifess_analysis.bat` - Batch file untuk Windows

## Usage Instructions

### 1. **Starting the Application**
```bash
# Method 1: Using batch file
run_gui_ifess_analysis.bat

# Method 2: Direct Python
python gui_ifess_analysis.py
```

### 2. **Configuration Tab**
1. **Database Configuration**:
   - Set database path (default: `C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB`)
   - Configure ISQL path (auto-detect atau manual)
   - Click "Test Connection" untuk verify koneksi

2. **Analysis Configuration**:
   - Pilih Month (01-12) dan Year
   - Pilih Analysis Type
   - Set Division Filter
   - Click "Load Divisions" untuk populate division data

3. **Save/Load Configuration**:
   - Save current settings ke JSON file
   - Load previous configuration

### 3. **Analysis Tab**
1. Click "Run Analysis" untuk start analysis
2. Monitor progress di progress bar dan log
3. Use "Stop Analysis" jika perlu cancel
4. "Clear Results" untuk reset results
5. "Export Results" untuk various formats

### 4. **Results Tab**
1. **Analysis Summary**: Overview statistik
2. **Detailed Results**: Tabular data dengan sorting
3. **Export Options**:
   - Excel export dengan multiple sheets
   - CSV export
   - PDF export (dalam development)
4. **Generate Charts**: Various visualization options

## Database Schema Integration

### Main Query Structure
```sql
SELECT 
    a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
    a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
    a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
    a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
    a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
    b.DIVID, c.DIVNAME
FROM FFBSCANNERDATA{MM} a
LEFT JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
WHERE a.TRANSDATE >= 'YYYY-MM-01' 
AND a.TRANSDATE < 'YYYY-MM-32'
ORDER BY a.TRANSNO, a.TRANSDATE, a.TRANSTIME
```

### Division Mapping
- **FFBSCANNERDATA{MM}** → **OCFIELD** (via FIELDID)
- **OCFIELD** → **CRDIVISION** (via DIVID)
- **Result**: Transaction data dengan division names

## Analysis Metrics

### Employee Performance
- **Total Transactions**: Jumlah transaksi yang dibuat
- **Verified Transactions**: Jumlah transaksi yang diverifikasi
- **Verification Rate**: Persentase tingkat verifikasi
- **Unique Transactions**: Jumlah transaksi unik (TRANSNO)
- **Role Classification**: KERANI, ASISTEN, MANDOR, ADMIN, LAINNYA

### Division Summary
- **Employee Count**: Jumlah karyawan per division
- **Transaction Volume**: Total transaksi per division
- **Verification Rate**: Tingkat verifikasi per division
- **Productivity Metrics**: Transaksi per karyawan

### Performance Interpretation
- **Green** (≥80%): Excellent performance
- **Orange** (60-79%): Good performance
- **Red** (<60%): Needs improvement

## Chart Types

### 1. **Employee Performance Chart**
- Top 15 karyawan berdasarkan verification rate
- Total transactions per employee
- Division distribution
- Role distribution dengan dual-axis

### 2. **Division Analysis Chart**
- Transactions per division
- Verification rates per division
- Employee distribution (pie chart)
- Productivity vs Quality scatter plot

### 3. **Trend Analysis Chart**
- Correlation analysis
- Productivity vs verification rate
- Trend line untuk pattern recognition

## Export Formats

### Excel Export
- **Sheet 1**: Detailed employee data
- **Sheet 2**: Division summary
- **Sheet 3**: Role summary
- **Features**: Formatting, charts, formulas

### CSV Export
- Simple tabular format
- Compatible dengan Excel dan database tools
- Lightweight untuk large datasets

### Chart Export
- High-resolution PNG (300 DPI)
- Timestamped filenames
- Professional formatting

## Configuration File

### Automatic Configuration Save
```json
{
  "db_path": "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB",
  "isql_path": "Auto-detect",
  "month": "05",
  "year": "2025",
  "analysis_type": "Employee Performance",
  "division_filter": "All Divisions"
}
```

## Error Handling

### Common Issues
1. **Database Connection Failed**:
   - Check database path
   - Verify ISQL path
   - Ensure database accessibility

2. **No Data Found**:
   - Check date range
   - Verify table existence (FFBSCANNERDATA{MM})
   - Check data availability

3. **Chart Generation Failed**:
   - Install matplotlib dan seaborn
   - Check output directory permissions
   - Verify data completeness

### Troubleshooting
- Check log messages di Analysis tab
- Verify all dependencies installed
- Ensure database permissions
- Check file system permissions

## Performance Optimization

### Best Practices
- Test connection sebelum analysis
- Use appropriate date ranges
- Filter by division untuk large datasets
- Close application properly untuk resource cleanup

### Memory Management
- Analysis menggunakan threading untuk UI responsiveness
- Automatic cleanup setelah analysis complete
- Progress tracking untuk large datasets

## Advanced Features

### Multi-threading
- Background analysis tidak block UI
- Real-time progress updates
- Cancellable operations

### Data Validation
- Input validation untuk dates
- Database schema validation
- Error recovery mechanisms

## Future Enhancements

### Planned Features
1. **PDF Report Generation**: Complete PDF reports
2. **Time Series Analysis**: Trend analysis over time
3. **Comparative Analysis**: Month-to-month comparison
4. **Dashboard View**: Real-time dashboard
5. **Scheduled Analysis**: Automated periodic analysis

### Technical Improvements
1. **Database Connection Pool**: Efficient connection management
2. **Caching System**: Performance optimization
3. **Plugin Architecture**: Extensible analysis modules
4. **Web Interface**: Browser-based version

## Support & Maintenance

### Regular Updates
- Bug fixes dan improvements
- New analysis features
- Performance optimizations
- User feedback integration

### Configuration Management
- Backup/restore configurations
- Multiple configuration profiles
- Environment-specific settings

## Conclusion

GUI Ifess Analysis Tool menyediakan solusi komprehensif untuk analisis database Ifess dengan:
- User-friendly interface
- Comprehensive analysis capabilities
- Professional reporting
- Extensible architecture
- Robust error handling

Tool ini dirancang untuk membantu analisis kinerja karyawan dan division dengan cara yang efisien dan professional. 