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
- **`gui_multi_estate_ffb_analysis.py`** - Primary multi-estate GUI application with integrated PDF report generation
- **`firebird_connector.py`** - Core Firebird database connectivity using isql.exe command-line tool
- **`gui_ffb_analysis_corrected.py`** - Alternative GUI implementation with enhanced features

### Core Business Logic Classes
- **`MultiEstateFFBAnalysisGUI`** - Main GUI class containing analysis methods
- **`FirebirdConnector`** - Database connection and query execution wrapper
- **Analysis methods**: `analyze_estate()`, `analyze_division()` - Core transaction verification logic

### Database Schema
- **Monthly Tables:** `FFBSCANNERDATA[MM]` where MM = 2-digit month (01-12)
- **Reference Tables:** `OCFIELD` (field info), `CRDIVISION` (division/estate), `EMP` (employee data)
- **Key Fields:** `TRANSNO` (transaction number), `SCANUSERID` (employee ID), `RECORDTAG` (role: PM/P1/P5), `TRANSDATE`, `FIELDID`

### Configuration
- **`config.json`** - Multi-estate database path configuration for 10 estates
- **Estates supported:** PGE 1A, 1B, 2A, 2B, IJL, DME, Are B2, B1, A, C

## Common Development Commands

### Running Applications
```bash
# Primary GUI (main application)
python gui_multi_estate_ffb_analysis.py

# Alternative GUI implementation
python gui_ffb_analysis_corrected.py

# Legacy GUI versions (backups)
python "gui_multi_estate_ffb_analysis - Copy.py"
python "gui_multi_estate_ffb_analysis backup.py"
```

### Database Testing
```bash
# Test database connectivity and isql.exe detection
python firebird_connector.py

# Test individual estate connections
python gui_multi_estate_ffb_analysis.py  # Use "Test All Connections" button
```

### Report Generation
```bash
# PDF reports are generated through the GUI interface
# 1. Run the GUI: python gui_multi_estate_ffb_analysis.py
# 2. Select estates and date range
# 3. Click "Start Analysis"
# 4. Reports are automatically generated in reports/ folder
```

## High-Level Architecture and Analysis Flow

### Core Analysis Pipeline
The system processes transactions through this flow:
```
Estate Selection → Date Range → Monthly Table Detection →
Transaction Extraction → TRANSNO Grouping → Verification Logic →
Performance Calculation → PDF Report Generation
```

### Verification Logic Implementation
The system implements transaction verification through these key methods:

1. **`analyze_estate()`** - Main entry point for single estate analysis
   - Handles database connection and path resolution
   - Determines available monthly tables for date range
   - Coordinates division-level analysis
   - Aggregates results across divisions

2. **`analyze_division()`** - Core business logic for transaction verification
   - Extracts transactions from monthly tables (FFBSCANNERDATA[MM])
   - Groups by TRANSNO to find duplicates
   - Identifies verification status (PM + P1/P5 = VERIFIED)
   - Calculates employee performance metrics
   - Detects field discrepancies between verified transactions

### Database Query Patterns
The system dynamically builds queries based on date range:

```sql
-- Base query pattern for transaction extraction
SELECT a.TRANSNO, a.SCANUSERID, a.RECORDTAG, a.TRANSDATE,
       a.FIELDID, a.AFD, a.BLOCK, a.TREECOUNT, a.BUNCHCOUNT,
       a.WEIGHT, a.TBS, a.HARVESTER, a.TAKENBY,
       b.DIVID, c.DIVNAME
FROM FFBSCANNERDATA{MM} a
JOIN OCFIELD b ON a.FIELDID = b.ID
LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
WHERE a.TRANSDATE BETWEEN '{start_date}' AND '{end_date}'
```

### Performance Metrics Calculation
Employee performance is calculated by:
- **Verification Rate** = (Verified PM transactions / Total PM transactions) × 100
- **Transaction Counts** = PM, Mandor (P1), Asisten (P5) totals
- **Discrepancy Detection** = Field differences between PM and verification records

## Critical System Constraints and Requirements

### Firebird Database Integration
- **isql.exe Dependency**: System uses command-line Firebird interface, not Python drivers
- **Windows Environment Required**: isql.exe path detection and Windows-specific execution
- **Auto-Detection Logic**: System searches multiple standard Firebird installation paths
- **Connection Format**: Supports both direct paths and `localhost:database_path` formats

### Monthly Table Architecture
- **Table Naming**: `FFBSCANNERDATA[MM]` where MM is 2-digit month (01-12)
- **Dynamic Detection**: System automatically determines which monthly tables exist for date ranges
- **Data Availability**: Varies significantly by estate and time period
- **Query Construction**: SQL queries are dynamically built based on available months

### Estate-Specific Considerations
- **Separate Databases**: Each estate has its own .FDB file with independent schema
- **Path Management**: Database paths can be directories (auto-detect .FDB) or direct file paths
- **Status 704 Filter**: Special filtering logic applies for May 2024 data (TRANSSTATUS = 704)

## GUI Application Architecture

### Main GUI Class Structure
```python
class MultiEstateFFBAnalysisGUI:
    def __init__(self, root):
        # Initialize GUI components
        # Load estate configuration
        # Setup date selection and progress tracking

    def analyze_estate(self, estate_name, db_path, start_date, end_date):
        # Entry point for single estate analysis
        # Handles path resolution and connection testing
        # Coordinates division-level analysis

    def analyze_division(self, connector, estate_name, div_id, div_name, ...):
        # Core transaction verification logic
        # Implements PM + P1/P5 = VERIFIED rules
        # Calculates employee performance metrics
```

### Configuration Management
- **Runtime Updates**: GUI allows live modification of database paths
- **Path Validation**: Real-time testing of database connectivity
- **Multi-Estate Selection**: Checkbox-based estate selection with "Select All" functionality
- **Date Range Selection**: Calendar widgets with default month selection

## Debugging and Troubleshooting

### Common Production Issues

1. **Database Path Resolution**
   - System handles both directory and direct file paths
   - Auto-searches for .FDB files in provided directories
   - Validates path existence before connection attempts

2. **Monthly Table Detection**
   - System queries metadata to identify available monthly tables
   - Gracefully handles missing tables for certain months
   - Logs table detection status for debugging

3. **Memory and Performance**
   - Large datasets (>100k records) may cause memory issues
   - Implement chunked processing for date ranges spanning multiple months
   - Monitor memory usage during multi-estate analysis

4. **GUI Responsiveness**
   - Long-running analyses run in separate threads
   - Progress updates via GUI text widget
   - Cancel functionality for interrupted analyses

### Data Quality Validation
- **TRANSNO Consistency**: System validates transaction number integrity
- **Employee Mapping**: Cross-checks employee IDs across tables
- **Date Range Validation**: Ensures transaction dates fall within expected ranges
- **Field Completeness**: Validates required fields are populated

## Production Deployment Notes

This is a **live production system** deployed across multiple palm oil estates with:
- Real-time monitoring of data entry quality
- Daily operational use by estate managers
- Integration with existing Firebird database infrastructure
- Monthly performance reporting for management review

The system processes actual agricultural operational data and is critical for quality assurance in palm oil harvesting operations.