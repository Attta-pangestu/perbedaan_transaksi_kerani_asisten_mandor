# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FFB SCANNER ANALYSIS SYSTEM                            │
│                             Multi-Estate Monitoring System                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GUI Layer     │    │  Analysis Layer │    │  Database Layer │
│                 │    │                 │    │                 │
│ • Multi-Estate  │◄──►│ • Transaction   │◄──►│ • Firebird DB   │
│   Selection     │    │   Analysis      │    │ • Monthly Tables│
│ • Date Range    │    │ • Verification  │    │ • Reference     │
│ • Progress Bar  │    │   Logic         │    │   Tables        │
│ • PDF Export    │    │ • Employee      │    │                 │
│                 │    │   Performance   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Report Generation                  │
         │                                                 │
         │ • PDF Reports (Professional)                   │
         │ • Excel Reports (Legacy)                       │
         │ • Multi-Estate Summaries                       │
         │ • Employee Performance Metrics                 │
         └─────────────────────────────────────────────────┘
```

## Component Flow Diagram

```
User Input ──► GUI Application ──► Analysis Engine ──► Database Query
    │               │                      │                  │
    │               │                      │                  ▼
    │               │                      │            ┌─────────────┐
    │               │                      │            │ Firebird DB │
    │               │                      │            │ (Multiple   │
    │               │                      │            │  Estates)   │
    │               │                      │            └─────────────┘
    │               │                      │                  │
    │               │                      ▼                  │
    │               │            ┌─────────────────┐         │
    │               │            │ Analysis Results │         │
    │               │            │ - Verification  │◄────────┘
    │               │            │ - Performance   │
    │               │            │ - Discrepancies │
    │               │            └─────────────────┘
    │               │                      │
    │               ▼                      ▼
    │        ┌─────────────┐        ┌─────────────┐
    │        │ Display UI  │        │ PDF/Excel   │
    │        │ Progress &  │        │ Reports     │
    │        │ Results     │        │ Export      │
    │        └─────────────┘        └─────────────┘
    ▼
User Views Results
```

## Estate Configuration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Multi-Estate Configuration                    │
│                                                                 │
│  Estate Name    Database Path                                   │
│  ───────────    ──────────────────                              │
│  PGE 1A         C:\Data\PTRJ_P1A.FDB                           │
│  PGE 1B         C:\Data\PTRJ_P1B.FDB                           │
│  PGE 2A         C:\Data\IFESS_PGE_2A\                          │
│  PGE 2B         C:\Data\IFESS_2B\PTRJ_P2B.FDB                  │
│  IJL            C:\Data\IFESS_IJL\PTRJ_IJL.FDB                 │
│  DME            C:\Data\IFESS_DME\PTRJ_DME.FDB                 │
│  Are B2         C:\Data\IFESS_ARE_B2\PTRJ_AB2.FDB              │
│  Are B1         C:\Data\IFESS_ARE_B1\PTRJ_AB1.FDB              │
│  Are A          C:\Data\IFESS_ARE_A\PTRJ_ARA.FDB               │
│  Are C          C:\Data\IFESS_ARE_C\PTRJ_ARC.FDB               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   config.json       │
                    │   (JSON Storage)    │
                    └─────────────────────┘
```

## Data Processing Pipeline

```
Raw Data Extraction
        │
        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Monthly Tables  │    │  Employee Data  │    │ Division Data   │
│ FFBSCANNERDATA01│    │ EMP Table       │    │ OCFIELD +       │
│ FFBSCANNERDATA02│    │ - ID, NAME      │    │ CRDIVISION      │
│ ...             │    │                 │    │                 │
│ FFBSCANNERDATA12│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │ Transaction     │
                    │ Analysis Engine │
                    │                 │
                    │ • Find Duplicates│
                    │ • Verification  │
                    │ • Performance   │
                    │ • Discrepancies │
                    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Report        │
                    │ Generation      │
                    │                 │
                    │ • PDF Reports   │
                    │ • Excel Export  │
                    │ • Statistics    │
                    └─────────────────┘
```

## Key Business Logic Flow

```
Transaction Processing Logic
┌─────────────────────────────────────────────────────────────┐
│ 1. Extract transactions from monthly tables (FFBSCANNERDATA) │
│ 2. Find duplicates by TRANSNO with different RECORDTAGs    │
│ 3. Verification Rules:                                      │
│    - PM (Kerani) + P1/P5 (Mandor/Asisten) = Verified       │
│ 4. Performance Metrics:                                     │
│    - Kerani: % verified from total created                  │
│    - Mandor/Asisten: % contribution vs total Kerani       │
│ 5. Discrepancy Analysis:                                    │
│    - Compare field values between duplicate transactions    │
│    - Count differences per transaction                      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
Frontend Layer:
├── Tkinter (GUI Framework)
├── tkcalendar (Date Selection)
└── Custom UI Components

Backend Layer:
├── Python 3.x
├── Pandas (Data Processing)
├── ReportLab (PDF Generation)
└── Threading (Non-blocking Operations)

Database Layer:
├── Firebird SQL Database
├── ISQL Command Line Interface
├── Monthly Table Partitioning
└── Windows Integration

Configuration & Storage:
├── JSON Configuration Files
├── File System Storage
└── Multi-Estate Support
```

## System Integration Points

```
External Systems Integration:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Firebird DB     │    │ Windows File    │    │ PDF/Excel       │
│ (Multiple       │    │ System          │    │ Export          │
│  Estates)       │    │                 │    │                 │
│                 │    │                 │    │                 │
│ • Real-time     │    │ • Database      │    │ • Reports       │
│   Queries       │    │   Files         │    │ • Analytics     │
│ • Data          │    │ • Config Files  │    │ • Sharing       │
│   Processing    │    │ • Output Folder │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```