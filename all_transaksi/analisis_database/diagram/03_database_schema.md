# Database Schema Analysis

## Database Architecture Overview

```
Multi-Estate Firebird Database Structure
┌─────────────────────────────────────────────────────────────────┐
│                    ESTATE DATABASES                             │
│                                                                 │
│ Each Estate has separate .fdb file:                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ PGE 1A: PTRJ_P1A.FDB                                      │ │
│ │ PGE 1B: PTRJ_P1B.FDB                                      │ │
│ │ PGE 2A: IFESS_PGE_2A_*.FDB                               │ │
│ │ PGE 2B: PTRJ_P2B.FDB                                      │ │
│ │ IJL: PTRJ_IJL_IMPIANJAYALESTARI.FDB                       │ │
│ │ DME: PTRJ_DME.FDB                                         │ │
│ │ Are B2: PTRJ_AB2.FDB                                      │ │
│ │ Are B1: PTRJ_AB1.FDB                                      │ │
│ │ Are A: PTRJ_ARA.FDB                                       │ │
│ │ Are C: PTRJ_ARC.FDB                                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Monthly Transaction Tables Structure

```
Monthly Transaction Data Tables: FFBSCANNERDATA[MM]
┌─────────────────────────────────────────────────────────────────┐
│ Table Naming Convention:                                        │
│ FFBSCANNERDATA01 through FFBSCANNERDATA12 (Monthly Tables)      │
│                                                                 │
│ Core Transaction Fields:                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Column Name          │ Type    │ Description                │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ ID                   │ INTEGER │ Primary Key                │ │
│ │ SCANUSERID           │ INTEGER │ User ID (Employee)         │ │
│ │ OCID                 │ INTEGER │ OC (Operating Unit) ID     │ │
│ │ WORKERID             │ INTEGER │ Worker ID                  │ │
│ │ CARRIERID            │ INTEGER │ Carrier ID                 │ │
│ │ FIELDID              │ INTEGER │ Field ID                   │ │
│ │ TASKNO               │ VARCHAR │ Task Number                │ │
│ │ RIPEBCH              │ FLOAT   │ Ripe Bunches Count         │ │
│ │ UNRIPEBCH            │ FLOAT   │ Unripe Bunches Count       │ │
│ │ BLACKBCH             │ FLOAT   │ Black Bunches Count        │ │
│ │ ROTTENBCH            │ FLOAT   │ Rotten Bunches Count       │ │
│ │ LONGSTALKBCH         │ FLOAT   │ Long Stalk Bunches Count   │ │
│ │ RATDMGBCH            │ FLOAT   │ Rat Damaged Bunches Count  │ │
│ │ LOOSEFRUIT           │ FLOAT   │ Loose Fruit Count          │ │
│ │ TRANSNO              │ VARCHAR │ Transaction Number (KEY)   │ │
│ │ TRANSDATE            │ DATE    │ Transaction Date            │ │
│ │ TRANSTIME            │ TIME    │ Transaction Time            │ │
│ │ UPLOADDATETIME       │ TIMESTAMP │ Upload DateTime          │ │
│ │ RECORDTAG            │ CHAR(2) │ Record Type (PM/P1/P5)     │ │
│ │ TRANSSTATUS          │ VARCHAR │ Transaction Status         │ │
│ │ TRANSTYPE            │ VARCHAR │ Transaction Type           │ │
│ │ LASTUSER             │ VARCHAR │ Last Modified User         │ │
│ │ LASTUPDATED          │ TIMESTAMP │ Last Update Timestamp    │ │
│ │ OVERRIPEBCH          │ FLOAT   │ Overripe Bunches Count     │ │
│ │ UNDERRIPEBCH         │ FLOAT   │ Underripe Bunches Count    │ │
│ │ ABNORMALBCH          │ FLOAT   │ Abnormal Bunches Count     │ │
│ │ LOOSEFRUIT2          │ FLOAT   │ Additional Loose Fruit     │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Reference Tables Structure

```
Employee Reference Table: EMP
┌─────────────────────────────────────────────────────────────────┐
│ EMP Table - Employee Master Data                                │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Column Name    │ Type    │ Description                      │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ ID             │ INTEGER │ Employee ID (Primary Key)        │ │
│ │ NAME           │ VARCHAR │ Employee Full Name               │ │
│ │ [Other Fields] │ ...     │ Additional employee data         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Purpose:                                                        │
│ ├── Employee ID to Name mapping                                 │
│ ├── Employee validation                                         │
│ └── User identification in reports                              │
└─────────────────────────────────────────────────────────────────┘

Field Reference Table: OCFIELD
┌─────────────────────────────────────────────────────────────────┐
│ OCFIELD Table - Field Information                                │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Column Name    │ Type    │ Description                      │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ ID             │ INTEGER │ Field ID (Primary Key)           │ │
│ │ OCID           │ INTEGER │ Operating Unit ID                │ │
│ │ DIVID          │ INTEGER │ Division ID                      │ │
│ │ [Other Fields] │ ...     │ Field-specific data              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Purpose:                                                        │
│ ├── Link transactions to divisions                              │
│ ├── Field identification                                        │
│ └── Organizational structure mapping                           │
└─────────────────────────────────────────────────────────────────┘

Division Reference Table: CRDIVISION
┌─────────────────────────────────────────────────────────────────┐
│ CRDIVISION Table - Division Information                          │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Column Name    │ Type    │ Description                      │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ ID             │ INTEGER │ Division ID (Primary Key)        │ │
│ │ DIVNAME        │ VARCHAR │ Division Name                    │ │
│ │ DIVCODE        │ VARCHAR │ Division Code                    │ │
│ │ OCID           │ INTEGER │ Operating Unit ID                │ │
│ │ [Other Fields] │ ...     │ Division-specific data           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Purpose:                                                        │
│ ├── Division name resolution                                    │
│ ├── Organizational hierarchy                                    │
│ └── Report grouping by division                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Business Logic Tables

```
Transaction Verification Logic - Key Tables and Fields
┌─────────────────────────────────────────────────────────────────┐
│ Transaction Verification Data Flow                              │
│                                                                 │
│ 1. Primary Transaction Table: FFBSCANNERDATA[MM]                │
│    ├── TRANSNO (Transaction Number) - Key field               │
│    ├── RECORDTAG (Record Type)                                 │
│    │   ├── 'PM' = Kerani (Scanner)                            │
│    │   ├── 'P1' = Mandor (Supervisor)                         │
│    │   └── 'P5' = Asisten (Assistant)                         │
│    ├── TRANSSTATUS (Transaction Status)                        │
│    │   ├── '704' = Special status (May 2025 filter)          │
│    │   ├── '731' = Normal status                              │
│    │   └── '732' = Normal status                              │
│    └── SCANUSERID (Employee ID)                               │
│                                                                 │
│ 2. Verification Logic:                                         │
│    ├── Find duplicate TRANSNO with different RECORDTAGs       │
│    ├── PM + (P1 or P5) = Verified Transaction                │
│    ├── Apply TRANSSTATUS 704 filter for May 2025              │
│    └── Calculate verification rates                           │
│                                                                 │
│ 3. Performance Metrics:                                        │
│    ├── Kerani Performance:                                     │
│    │   ├── Total transactions created                          │
│    │   ├── Verified transactions count                         │
│    │   └── Verification percentage                             │
│    ├── Mandor/Asisten Performance:                            │
│    │   ├── Total verification activities                       │
│    │   └── Contribution percentage vs Kerani                   │
│    └── Discrepancy Analysis:                                   │
│        ├── Field-level differences (RIPEBCH, UNRIPEBCH, etc.) │
│        └── Difference count per transaction                    │
└─────────────────────────────────────────────────────────────────┘
```

## Table Relationships and Joins

```
Database Join Structure for Analysis
┌─────────────────────────────────────────────────────────────────┐
│ Primary Join Pattern Used in Application:                      │
│                                                                 │
│ SELECT a.*, b.DIVID, c.DIVNAME                                │
│ FROM FFBSCANNERDATA[MM] a                                     │
│ JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID        │
│ LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID   │
│ WHERE [date conditions]                                        │
│                                                                 │
│ Join Logic Explanation:                                         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ a (FFBSCANNERDATA)                                          │ │
│ │ ├── Contains transaction data                                │ │
│ │ ├── Links to fields via FIELDID                             │ │
│ │ └── Links to operating units via OCID                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                 │                                               │
│                 ▼                                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ b (OCFIELD)                                                 │ │
│ │ ├── Contains field information                              │ │
│ │ ├── Links to divisions via DIVID                            │ │
│ │ └── Joins on FIELDID + OCID (composite key)                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                 │                                               │
│                 ▼                                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ c (CRDIVISION)                                              │ │
│ │ ├── Contains division names                                 │ │
│ │ ├── Joins on DIVID + OCID (composite key)                  │ │
│ │ └── LEFT JOIN (divisions may be null)                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

Employee Data Join Pattern:
┌─────────────────────────────────────────────────────────────────┐
│ Employee Information Lookup:                                    │
│                                                                 │
│ SELECT ID, NAME FROM EMP                                        │
│                                                                 │
│ Application Logic:                                             │
│ ├── Cache employee mappings at startup                         │
│ ├── Use SCANUSERID from transactions                           │
│ ├── Map to employee names for reports                          │
│ └── Handle missing employees with default names                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Volume and Performance Considerations

```
Data Volume Characteristics:
┌─────────────────────────────────────────────────────────────────┐
│ Monthly Data Volume Estimates:                                   │
│                                                                 │
│ FFBSCANNERDATA[MM] Tables:                                      │
│ ├── 50,000+ records per month per estate                        │
│ ├── 30+ fields per record                                       │
│ ├── 12 monthly tables per estate                               │
│ └── ~600,000 total records per estate per year                 │
│                                                                 │
│ Reference Tables:                                               │
│ ├── EMP: ~1,000 records (employees)                            │
│ ├── OCFIELD: ~1,000 records (fields)                           │
│ └── CRDIVISION: ~50 records (divisions)                        │
│                                                                 │
│ Performance Optimization Strategies:                            │
│                                                                 │
│ 1. Query Optimization:                                          │
│    ├── Date range filtering on TRANSDATE                      │
│    ├── Division filtering on DIVID                            │
│    ├── Index usage on TRANSNO, FIELDID, TRANSDATE             │
│    └── Monthly table partitioning                              │
│                                                                 │
│ 2. Data Processing:                                            │
│    ├── Pandas DataFrame operations                              │
│    ├── In-memory processing for analysis                       │
│    ├── Batch processing for large datasets                     │
│    └── Memory-efficient algorithms                             │
│                                                                 │
│ 3. Database Connections:                                        │
│    ├── Connection pooling via FirebirdConnector               │
│    ├── Timeout handling (300-600 seconds)                      │
│    ├── Error recovery and retry logic                         │
│    └── ISQL process management                                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Integrity and Validation

```
Data Validation Rules:
┌─────────────────────────────────────────────────────────────────┐
│ Primary Data Validation Checks:                                 │
│                                                                 │
│ 1. Transaction Data Integrity:                                  │
│    ├── TRANSNO must be unique within date range (per RECORDTAG) │
│    ├── SCANUSERID must exist in EMP table                       │
│    ├── FIELDID must exist in OCFIELD table                      │
│    ├── TRANSDATE must be valid date                             │
│    └── Record quantities must be numeric (>= 0)                │
│                                                                 │
│ 2. Reference Data Integrity:                                    │
│    ├── EMP.ID must be unique                                   │
│    ├── OCFIELD.ID must be unique per OCID                      │
│    ├── CRDIVISION.ID must be unique per OCID                   │
│    └── DIVNAME should not be null                             │
│                                                                 │
│ 3. Business Logic Validation:                                   │
│    ├── RECORDTAG must be one of: 'PM', 'P1', 'P5'              │
│    ├── TRANSSTATUS must be valid status code                   │
│    ├── Verified transactions must have matching TRANSNOs      │
│    └── Date ranges must be within available monthly tables    │
│                                                                 │
│ 4. Application-Level Validation:                                │
│    ├── Config.json must contain valid database paths          │
│    ├── Selected estates must have accessible database files    │
│    ├── Date ranges must be valid (start <= end)               │
│    └── Output directory must be writable                      │
└─────────────────────────────────────────────────────────────────┘
```

## Special Cases and Business Rules

```
Special Business Rules and Cases:
┌─────────────────────────────────────────────────────────────────┐
│ Special Transaction Handling:                                   │
│                                                                 │
│ 1. May 2025 TRANSSTATUS 704 Filter:                             │
│    ├── Applied specifically to May 2025 data                   │
│    ├── Only count transactions with TRANSSTATUS = '704'       │
│    │   for Mandor/Asisten in verification calculations          │
│    ├── Kerani transactions can have any status (731/732/704)   │
│    └── Improves verification accuracy for specific period     │
│                                                                 │
│ 2. Multi-Estate Data Variations:                                │
│    ├── Different estates may have different data availability   │
│    ├── Some estates may skip certain months                    │
│    ├── Database file formats may vary slightly                 │
│    └── Connection strings adapt to file vs folder paths       │
│                                                                 │
│ 3. Duplicate Transaction Logic:                                 │
│    ├── Same TRANSNO + Different RECORDTAG = Verification       │
│    ├── Priority order: P1 (Asisten) > P5 (Mandor)              │
│    ├── If both P1 and P5 exist, prioritize P1                  │
│    └── Single TRANSNO per role per day                         │
│                                                                 │
│ 4. Performance Calculation Rules:                               │
│    ├── Kerani: % Verified = (Verified / Total Created) × 100   │
│    ├── Mandor/Asisten: % Contribution = (Their Total / Total Kerani) × 100 │
│    ├── Division Summary: % Verified = (Total Verified / Total Kerani) × 100 │
│    └── Grand Total: Cross-estate aggregation of all metrics   │
│                                                                 │
│ 5. Discrepancy Analysis Rules:                                  │
│    ├── Compare 7 fields: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, │
│    │   LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT                    │
│    ├── Count as 1 difference per transaction if ANY field differs │
│    ├── Calculate % difference = (Differences / Verified) × 100 │
│    └── Used as quality indicator for Kerani performance       │
└─────────────────────────────────────────────────────────────────┘
```