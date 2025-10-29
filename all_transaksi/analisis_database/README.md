# FFB Scanner Analysis System v2.0

A comprehensive multi-estate Fresh Fruit Bunch (FFB) scanner transaction analysis system for palm oil agricultural operations.

## System Overview

This system processes scanner transaction data from multiple estates to monitor data entry quality and employee performance across three roles:
- **Kerani (Scanner)**: Primary data entry personnel (`PM` records)
- **Mandor (Supervisor)**: Transaction verification (`P1` records)
- **Asisten (Assistant)**: Additional verification support (`P5` records)

## Key Features

### 🔍 **Transaction Analysis**
- Duplicate transaction detection by TRANSNO with different RECORDTAG values
- Verification rate calculation across estates and employees
- Discrepancy identification between role-based transactions
- Status 704 filtering for May 2025 data accuracy

### 📊 **Multi-Estate Support**
- Support for 10 estates: PGE 1A, 1B, 2A, 2B, IJL, DME, Are B2, B1, A, C
- Individual database configuration per estate
- Comparative analysis across estates
- Consolidated reporting

### 📈 **Comprehensive Reporting**
- PDF reports with professional styling
- Excel data analysis exports
- Interactive charts and visualizations
- Employee performance metrics
- Transaction discrepancy tracking

### 🖥️ **Modern GUI Interface**
- Modular tabbed interface
- Real-time progress tracking
- Interactive results display
- Advanced filtering options
- Export functionality

### 🔧 **Technical Features**
- Firebird database integration via ISQL
- Layered architecture for maintainability
- Portable system design
- Configuration-driven setup
- Comprehensive error handling

## Architecture

```
FFB Analysis System v2.0
├── Presentation Layer (GUI)
│   ├── Main Window with tabbed interface
│   ├── Estate Selection Widget
│   ├── Date Range Widget
│   ├── Progress Widget
│   ├── Results Display Widget
│   └── Report Export Widget
├── Business Logic Layer
│   ├── Analysis Service
│   ├── Validation Service
│   ├── Configuration Service
│   ├── Employee Performance Service
│   └── Report Generation Service
├── Data Access Layer
│   ├── Transaction Repository
│   ├── Employee Repository
│   ├── Estate Repository
│   └── Firebird Database Connector
└── Infrastructure Layer
    ├── Configuration Management
    ├── Logging Framework
    ├── Error Handling
    └── PDF Report Generation
```

## Installation

### Prerequisites

1. **Python 3.8+** installed
2. **Firebird Database Server** with ISQL command-line tool
3. **Windows Operating System** (required for ISQL integration)

### Setup Steps

1. **Clone or extract the system folder:**
   ```
   D:\Gawean Rebinmas\Monitoring Database\Laporan_Ifess_beda_transno\all_transaksi\analisis_database\
   ```

2. **Install Python dependencies:**
   ```bash
   cd "D:\Gawean Rebinmas\Monitoring Database\Laporan_Ifess_beda_transno\all_transaksi\analisis_database"
   pip install -r requirements.txt
   ```

3. **Configure database paths:**
   - Edit `config/database_paths.json`
   - Set the correct paths for each estate's .fdb database file
   - Verify Firebird service is running

4. **Run the application:**
   ```bash
   python main.py
   ```

## Configuration

### Database Configuration

Edit `config/database_paths.json` to configure your estate databases:

```json
{
  "estates": {
    "PGE 1A": {
      "database_path": "C:/Database/PGE1A.FDB",
      "active": true
    },
    "PGE 2A": {
      "database_path": "C:/Database/PGE2A.FDB",
      "active": true
    }
  }
}
```

### Application Settings

Configure application behavior in `config/app_settings.json`:

- GUI preferences (themes, fonts, layouts)
- Analysis preferences (date ranges, thresholds)
- Report settings (formats, styling)
- Export options (paths, compression)

### System Configuration

Main system configuration in `config/config.json`:

- Performance settings
- Logging configuration
- Security options
- Integration settings

## Usage

### Basic Analysis Workflow

1. **Launch Application**
   - Run `main.py` to start the GUI
   - System will validate database connections
   - Configure estates if needed

2. **Select Analysis Parameters**
   - Choose target estates (multi-selection supported)
   - Set date range for analysis
   - Configure analysis options

3. **Run Analysis**
   - Click "Mulai Analisis" button
   - Monitor progress in real-time
   - Review any warnings or errors

4. **Review Results**
   - Browse summary statistics
   - Examine detailed transaction data
   - Analyze employee performance
   - View charts and visualizations

5. **Export Reports**
   - Choose report format (PDF, Excel, CSV)
   - Configure export options
   - Generate and save reports

### Advanced Features

#### Custom Date Ranges
- Quick selection buttons (Current Month, Last 3 Months, etc.)
- Custom range selection with calendar
- Date validation and error handling

#### Employee Performance Tracking
- Individual employee analysis
- Transaction accuracy metrics
- Performance trend analysis
- Discrepancy tracking

#### Multi-Estate Comparative Analysis
- Side-by-side estate comparisons
- Verification rate benchmarking
- Cross-estate employee analysis
- Consolidated reporting

## Database Schema

### Monthly Transaction Tables
- **Pattern**: `FFBSCANNERDATA[MM]` where MM = 2-digit month
- **Key Fields**:
  - `TRANSNO`: Transaction number (primary identifier)
  - `SCANUSERID: Employee ID
  - `RECORDTAG`: Role identifier (PM, P1, P5)
  - `TRANSDATE`: Transaction date
  - `FIELDID`: Field identifier
  - `DIVID`: Division identifier

### Reference Tables
- **OCFIELD**: Field reference data
- **CRDIVISION**: Division reference data
- **EMP**: Employee reference data

## Data Processing Logic

### Verification Detection
The system identifies verified transactions by finding duplicates with the same `TRANSNO` but different `RECORDTAG` values:

1. **Primary Transaction**: Kerani entries (`PM` records)
2. **Verification Records**: Mandor (`P1`) and Asisten (`P5`) entries
3. **Verification Status**: Transaction considered verified when matching P1/P5 records exist

### Performance Metrics
- **Verification Rate**: (Verified Transactions / Total Kerani Transactions) × 100%
- **Discrepancy Count**: Number of transactions with data differences
- **Employee Accuracy**: Individual performance metrics
- **Daily Trends**: Time-based analysis patterns

## Troubleshooting

### Common Issues

#### Database Connection Failed
```
Error: Unable to connect to database
```
**Solutions:**
- Verify Firebird service is running
- Check database paths in `config/database_paths.json`
- Ensure ISQL.exe is accessible (auto-detection or manual path)
- Validate database file permissions

#### No Data Found
```
Warning: No transactions found for selected date range
```
**Solutions:**
- Verify monthly tables exist for target period
- Check date range format and validity
- Use data availability checker
- Confirm estate has data for selected period

#### Report Generation Errors
```
Error: Failed to generate PDF report
```
**Solutions:**
- Ensure `reports/` directory exists and is writable
- Verify ReportLab installation
- Check available memory for large datasets
- Try smaller date ranges for testing

#### Performance Issues
```
Warning: Analysis taking longer than expected
```
**Solutions:**
- Reduce date range scope
- Enable data caching in settings
- Close unnecessary applications
- Consider system resources upgrade

### System Diagnostics

Run built-in diagnostics:
```bash
python -c "from src.infrastructure.database.firebird_connector import FirebirdConnector; FirebirdConnector.test_system()"
```

Check log files in `logs/` directory for detailed error information.

## Development

### Project Structure
```
analisis_database/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── config/                    # Configuration files
│   ├── config.json           # Main system configuration
│   ├── database_paths.json   # Database path configuration
│   └── app_settings.json     # User preferences
├── src/                       # Source code
│   ├── gui/                  # GUI components
│   │   ├── main_window.py    # Main application window
│   │   └── widgets/          # Modular GUI widgets
│   ├── services/             # Business logic services
│   ├── models/               # Domain models
│   ├── repositories/         # Data access layer
│   └── infrastructure/       # Infrastructure components
├── reports/                  # Generated reports
├── logs/                     # Application logs
├── temp/                     # Temporary files
└── backups/                  # Backup files
```

### Adding New Features

1. **GUI Components**: Add to `src/gui/widgets/`
2. **Business Logic**: Add to `src/services/`
3. **Data Models**: Add to `src/models/`
4. **Database Operations**: Add to `src/repositories/`

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Support

### Contact Information
- **System Developer**: Claude AI Assistant
- **Version**: 2.0 (Refactored Modular Architecture)
- **Last Updated**: 2025-10-27

### Documentation
- **Architecture Documentation**: `diagram/` folder
- **API Documentation**: Inline code documentation
- **User Manual**: This README file

### Change Log

#### Version 2.0 (2025-10-27)
- Complete architectural refactoring
- Modular GUI component design
- Enhanced error handling and logging
- Portable system implementation
- Advanced reporting features

#### Version 1.0 (Original)
- Basic multi-estate analysis
- PDF report generation
- Firebird database integration

## License

This system is developed for internal use by PT. Rebinmas for FFB scanner transaction analysis and monitoring.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 or later
- **Python**: 3.8 or later
- **Memory**: 4GB RAM
- **Storage**: 500MB free space
- **Database**: Firebird 2.5+ with ISQL

### Recommended Requirements
- **OS**: Windows 11
- **Python**: 3.10 or later
- **Memory**: 8GB RAM
- **Storage**: 2GB free space
- **Database**: Firebird 3.0+ with ISQL
- **Display**: 1920x1080 resolution

---

**Note**: This system is designed to be portable. The entire `analisis_database` folder can be copied to another computer and will run independently after installing Python dependencies.