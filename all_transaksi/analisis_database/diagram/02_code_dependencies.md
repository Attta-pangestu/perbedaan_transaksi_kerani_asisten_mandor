# Code Dependencies Analysis

## Entry Point and Main Components

### Primary Entry Point
```
gui_multi_estate_ffb_analysis.py (Main Application)
├── Imports:
│   ├── tkinter (GUI Framework)
│   ├── pandas (Data Processing)
│   ├── firebird_connector (Local Module)
│   ├── reportlab (PDF Generation)
│   └── Standard Libraries (os, datetime, threading, json)
```

## Core Dependencies Map

```
gui_multi_estate_ffb_analysis.py
┌─────────────────────────────────────────────────────────────────┐
│ MAIN APPLICATION                                                │
│                                                                 │
│ Direct Dependencies:                                            │
│ ├── firebird_connector.py                                      │
│ ├── tkinter (external)                                         │
│ ├── pandas (external)                                          │
│ ├── reportlab (external)                                       │
│ ├── tkcalendar (external)                                      │
│ └── Standard Libraries                                          │
│                                                                 │
│ Internal Logic:                                                │
│ ├── Multi-Estate Configuration Management                       │
│ ├── Database Connection Handling                               │
│ ├── Transaction Analysis Engine                                │
│ ├── PDF Report Generation                                      │
│ └── GUI Event Handling                                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ firebird_connector.py                                          │
│                                                                 │
│ Dependencies:                                                  │
│ ├── subprocess (system calls to isql.exe)                      │
│ ├── pandas (external)                                          │
│ ├── tempfile (temporary file handling)                         │
│ └── Standard Libraries                                          │
│                                                                 │
│ Responsibilities:                                              │
│ ├── Database Connection Management                             │
│ ├── SQL Query Execution                                        │
│ ├── Result Parsing and Formatting                              │
│ ├── Connection Testing                                         │
│ └── Error Handling                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Secondary Analysis Modules

```
Analysis Engine Modules (Imported by Main Application):
┌─────────────────────────────────────────────────────────────────┐
│ analisis_detail_kerani.py                                     │
│                                                                 │
│ Dependencies:                                                  │
│ ├── firebird_connector.py                                      │
│ ├── analisis_per_karyawan.py                                  │
│ ├── pandas (external)                                          │
│ └── Standard Libraries                                          │
│                                                                 │
│ Functions:                                                     │
│ ├── get_detailed_transaction_data()                            │
│ ├── analyze_kerani_transactions_detailed()                     │
│ └── Division-level analysis                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ analisis_per_karyawan.py                                       │
│                                                                 │
│ Dependencies:                                                  │
│ ├── firebird_connector.py                                      │
│ ├── pdf_report_advanced.py                                     │
│ ├── matplotlib/seaborn (external)                              │
│ ├── pandas (external)                                          │
│ └── Standard Libraries                                          │
│                                                                 │
│ Functions:                                                     │
│ ├── get_employee_mapping()                                     │
│ ├── get_transstatus_mapping()                                  │
│ ├── get_division_mapping()                                     │
│ └── Employee performance analysis                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ffb_pdf_report_generator.py                                    │
│                                                                 │
│ Dependencies:                                                  │
│ ├── reportlab (external)                                       │
│ ├── pandas (external)                                          │
│ └── Standard Libraries                                          │
│                                                                 │
│ Class: FFBPDFReportGenerator                                   │
│ ├── create_division_report()                                   │
│ ├── create_title_page()                                        │
│ ├── create_executive_summary()                                 │
│ └── Professional PDF formatting                                │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration and Utility Files

```
Configuration Management:
┌─────────────────────────────────────────────────────────────────┐
│ config.json                                                    │
│                                                                 │
│ Multi-Estate Database Configuration                             │
│ {                                                               │
│   "PGE 1A": "path/to/database1.fdb",                           │
│   "PGE 1B": "path/to/database2.fdb",                           │
│   ...                                                           │
│ }                                                               │
│                                                                 │
│ Purpose:                                                       │
│ ├── Database path storage                                      │
│ ├── Estate configuration                                        │
│ ├── Runtime configuration persistence                           │
│ └── Multi-estate support                                       │
└─────────────────────────────────────────────────────────────────┘
```

## External Library Dependencies

```
External Dependencies Tree:
┌─────────────────────────────────────────────────────────────────┐
│ External Libraries                                             │
│                                                                 │
│ GUI Frameworks:                                               │
│ ├── tkinter (Python Standard Library)                          │
│ │   ├── ttk (themed widgets)                                   │
│ │   ├── messagebox (dialogs)                                   │
│ │   └── filedialog (file selection)                            │
│ └── tkcalendar (third-party)                                   │
│     └── DateEntry widget                                        │
│                                                                 │
│ Data Processing:                                               │
│ ├── pandas (external)                                          │
│ │   ├── DataFrame operations                                    │
│ │   ├── Data manipulation                                       │
│ │   └── Statistical analysis                                    │
│ └── numpy (external - used by pandas)                          │
│                                                                 │
│ PDF Generation:                                                │
│ └── reportlab (external)                                       │
│     ├── SimpleDocTemplate                                       │
│     ├── Table, Paragraph, Spacer                               │
│     ├── Page formatting                                         │
│     └── Professional styling                                    │
│                                                                 │
│ Visualization (Optional):                                      │
│ ├── matplotlib (external)                                      │
│ └── seaborn (external)                                         │
│                                                                 │
│ System Integration:                                            │
│ ├── subprocess (Python Standard Library)                       │
│ │   └── isql.exe execution                                      │
│ ├── os (Python Standard Library)                               │
│ │   ├── File system operations                                 │
│ │   └── Path handling                                          │
│ └── threading (Python Standard Library)                        │
│     └── Non-blocking operations                                │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema Dependencies

```
Database Schema Structure:
┌─────────────────────────────────────────────────────────────────┐
│ Firebird Database Tables                                       │
│                                                                 │
│ Transaction Tables (Monthly):                                   │
│ ├── FFBSCANNERDATA01 through FFBSCANNERDATA12                  │
│ │   ├── ID, SCANUSERID, TRANSNO                                │
│ │   ├── TRANSDATE, TRANSTIME                                    │
│ │   ├── RECORDTAG (PM/P1/P5)                                   │
│ │   ├── TRANSSTATUS                                             │
│ │   ├── Field data (RIPEBCH, UNRIPEBCH, etc.)                 │
│ │   └── Location data (FIELDID, OCID)                          │
│                                                                 │
│ Reference Tables:                                               │
│ ├── EMP (Employee Data)                                        │
│ │   └── ID, NAME                                               │
│ ├── OCFIELD (Field Information)                                │
│ │   └── ID, DIVID, OCID                                        │
│ └── CRDIVISION (Division Information)                          │
│     └── ID, DIVNAME, DIVCODE                                   │
│                                                                 │
│ Database Dependencies:                                         │
│ ├── Firebird 1.5+ Compatibility                                │
│ ├── ISQL Command Line Interface                                │
│ ├── Multi-estate database files                                │
│ └── Monthly table partitioning                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Dependencies

```
Data Processing Flow Dependencies:
┌─────────────────────────────────────────────────────────────────┐
│ Data Extraction Layer                                          │
│                                                                 │
│ gui_multi_estate_ffb_analysis.py                               │
│ ├── get_divisions() → FFBSCANNERDATA tables                   │
│ ├── get_employee_mapping() → EMP table                        │
│ └── analyze_division() → Multiple table joins                  │
│                                                                 │
│           │                                                   │
│           ▼                                                   │
│                                                                 │
│ firebird_connector.py                                          │
│ ├── execute_query() → ISQL execution                          │
│ ├── to_pandas() → DataFrame conversion                        │
│ └── _parse_isql_output() → Result formatting                  │
│                                                                 │
│           │                                                   │
│           ▼                                                   │
│                                                                 │
│ Analysis Modules                                               │
│ ├── analisis_detail_kerani.py                                 │
│ ├── analisis_per_karyawan.py                                  │
│ └── Verification logic implementation                          │
│                                                                 │
│           │                                                   │
│           ▼                                                   │
│                                                                 │
│ Report Generation                                              │
│ ├── ffb_pdf_report_generator.py                               │
│ ├── reportlab library                                         │
│ └── PDF/Excel output creation                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Dependencies

```
Error Handling Chain:
┌─────────────────────────────────────────────────────────────────┐
│ Error Dependencies                                              │
│                                                                 │
│ Database Layer:                                                │
│ ├── firebird_connector.py                                      │
│ │   ├── Connection testing                                      │
│ │   ├── Query validation                                        │
│ │   ├── ISQL process monitoring                                 │
│ │   └── Timeout handling                                        │
│ │                                                               │
│ │   └── subprocess.CalledProcessError handling                 │
│                                                                 │
│ Application Layer:                                             │
│ ├── gui_multi_estate_ffb_analysis.py                           │
│ │   ├── File existence validation                               │
│ │   ├── Date range validation                                   │
│ │   ├── Estate selection validation                             │
│ │   └── Progress monitoring                                     │
│ │                                                               │
│ │   └── Exception propagation to GUI                           │
│                                                                 │
│ Report Generation:                                             │
│ ├── PDF creation error handling                                │
│ ├── File permission validation                                 │
│ └── Memory usage monitoring                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Import Hierarchy Summary

```
Import Dependency Hierarchy (Top-Level First):

1. gui_multi_estate_ffb_analysis.py (Main Application)
   ├── firebird_connector.py
   ├── Standard libraries
   └── External libraries

2. firebird_connector.py (Database Layer)
   ├── Standard libraries (subprocess, tempfile, etc.)
   └── pandas (external)

3. analisis_per_karyawan.py (Analysis Module)
   ├── firebird_connector.py
   ├── pdf_report_advanced.py
   └── External libraries (pandas, matplotlib, seaborn)

4. analisis_detail_kerani.py (Analysis Module)
   ├── firebird_connector.py
   ├── analisis_per_karyawan.py
   └── Standard libraries + pandas

5. ffb_pdf_report_generator.py (Report Generation)
   ├── reportlab (external)
   ├── pandas (external)
   └── Standard libraries

6. pdf_report_advanced.py (Advanced Reports)
   └── reportlab + pandas dependencies
```

## Critical Dependencies Summary

```
Critical Path Dependencies:
┌─────────────────────────────────────────────────────────────────┐
│ Must-Have Dependencies for Core Functionality:                 │
│                                                                 │
│ 1. Firebird Database                                           │
│    ├── Firebird 1.5+ installed                                │
│    ├── isql.exe accessible                                    │
│    └── Database files (.fdb) available                        │
│                                                                 │
│ 2. Python Environment                                          │
│    ├── Python 3.x                                             │
│    ├── pandas library                                          │
│    ├── reportlab library                                       │
│    └── tkinter (standard library)                              │
│                                                                 │
│ 3. File System Access                                          │
│    ├── Read access to database files                           │
│    ├── Write access for reports/ folder                       │
│    └── Config file read/write permissions                     │
│                                                                 │
│ 4. Windows Integration                                         │
│    ├── Windows OS (ISQL compatibility)                        │
│    ├── Path handling support                                   │
│    └── File association support                                │
└─────────────────────────────────────────────────────────────────┘
```