# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a **Fresh Fruit Bunch (FFB) Scanner Analysis System** for palm oil agricultural operations. The system processes scanner transaction data from multiple estates to monitor data entry quality and employee performance across three roles: Kerani (Scanner), Mandor (Supervisor), and Asisten (Assistant).

### Core Architecture

```
GUI Layer → Analysis Engine → Database Layer → Report Generation
    ↓              ↓              ↓              ↓
Multi-Estate   Transaction    Firebird DB    PDF/Excel/CSV
GUI           Analysis       + Monthly      Reports
               Engine         Tables         (FFBSCANNERDATA[MM])
```

### Key Business Logic

The system identifies data quality issues by finding duplicate transactions with the same `TRANSNO` but different `RECORDTAG` values:
- `PM` = Kerani (Scanner)
- `P1` = Mandor (Supervisor)
- `P5` = Asisten (Assistant)

When a Kerani transaction (`PM`) has corresponding transactions from Mandor/Asisten (`P1`/`P5`) with the same `TRANSNO`, it's considered "verified". The system calculates verification rates and identifies discrepancies between input data from different roles.

## Key Files and Architecture

### Main Applications
- **`gui_multi_estate_ffb_analysis.py`** - Primary multi-estate GUI application with PDF report generation
- **`firebird_connector.py`** - Core Firebird database connectivity using isql.exe
- **`ffb_pdf_report_generator.py`** - Enhanced PDF report generator with professional styling

### Analysis Engine Files
- **`correct_analysis_engine.py`** - Main analysis logic (may be missing/placeholder)
- **`analisis_detail_kerani.py`** - Detailed Kerani transaction analysis
- **`analisis_per_karyawan.py`** - Per-employee performance analysis

### Database Schema
- **Monthly Tables:** `FFBSCANNERDATA[MM]` where MM = 2-digit month (01-12)
- **Reference Tables:** `OCFIELD`, `CRDIVISION`, `EMP`
- **Key Fields:** `TRANSNO`, `SCANUSERID`, `RECORDTAG`, `TRANSDATE`, `DIVID`

### Configuration
- **`config.json`** - Multi-estate database path configuration (10 estates supported)

## Common Development Commands

### Running Applications
```bash
# Primary GUI (most common usage)
python gui_multi_estate_ffb_analysis.py

# Windows batch launcher
run_gui.bat

# Individual analysis components
python analisis_detail_kerani.py
python analisis_per_karyawan.py
```

### Testing
```bash
# Complete system validation
python test_complete_system.py

# Database connection testing
python firebird_connector.py

# Analysis engine testing
python test_corrected_analysis.py

# Firebird compatibility testing
python test_firebird_compatibility.py
```

### Report Generation
```bash
# PDF reports (current system)
python gui_multi_estate_ffb_analysis.py  # PDF generation integrated

# Excel reports (legacy)
python make_excel.py
```

## Database Integration Patterns

### Standard Connection Flow
```python
from firebird_connector import FirebirdConnector

connector = FirebirdConnector(db_path)
if connector.test_connection():
    result = connector.execute_query(query)
    df = connector.to_pandas(result)
```

### Typical Analysis Query Pattern
```sql
SELECT a.TRANSNO, a.SCANUSERID, a.RECORDTAG, b.DIVID, c.DIVNAME
FROM FFBSCANNERDATA09 a
JOIN OCFIELD b ON a.FIELDID = b.ID
LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
WHERE a.TRANSDATE >= '2025-09-01'
  AND a.TRANSDATE <= '2025-09-30'
```

### Data Processing Logic
1. Extract transactions for date range from monthly tables
2. Find duplicates by `TRANSNO` with different `RECORDTAG`
3. Calculate verification rates = (duplicates / total Kerani transactions)
4. Identify field differences between duplicate transactions
5. Aggregate by employee, division, and estate

## Important System Constraints

### Firebird Database Requirements
- Uses isql.exe for command-line database access
- Requires Windows environment (isql.exe path detection)
- Auto-detects Firebird 1.5+ installation paths
- Connection format: `localhost:database_path.fdb`

### Monthly Data Structure
- Each month has separate table: `FFBSCANNERDATA01` to `FFBSCANNERDATA12`
- Current data availability varies by estate and month
- Some estates may not have data for certain months

### Estate Configuration
- Supports 10 estates: PGE 1A, 1B, 2A, 2B, IJL, DME, Are B2, B1, A, C
- Database paths configured in `config.json`
- Path validation required on application startup

## Debugging and Troubleshooting

### Common Issues and Solutions

1. **Database Connection Failed**
   - Verify database paths in `config.json`
   - Check Firebird service status
   - Validate isql.exe auto-detection

2. **No Data Found for Date Range**
   - Check if monthly tables exist for target period
   - Verify data availability using `check_data_available.py`
   - Estates may have different data update schedules

3. **Report Generation Errors**
   - Verify `reports/` directory exists and is writable
   - Check reportlab installation and version compatibility
   - Ensure sufficient memory for large datasets

4. **Multi-Estate Analysis Issues**
   - Each estate has separate database file
   - Cross-estate analysis requires loading multiple databases
   - Date range consistency important for comparative analysis

### Data Validation Patterns
```python
# Check data availability before analysis
for month in target_months:
    table_name = f"FFBSCANNERDATA{month:02d}"
    count_query = f"SELECT COUNT(*) as TOTAL FROM {table_name}"
    # Validate data exists before proceeding
```

### Error Handling Best Practices
- Always validate `config.json` paths exist before connections
- Use try-catch blocks around all database operations
- Implement timeout handling for long-running queries
- Validate date ranges and table existence

## Performance Considerations

- Large monthly tables (>50k records) require efficient queries
- Use indexes on `TRANSDATE`, `TRANSNO`, and `FIELDID` columns
- Implement data pagination for very large date ranges
- Cache employee mappings to reduce lookup overhead

This is a production agricultural data quality monitoring system with real-world deployment across multiple palm oil estates.