# Modular Report Generation System - Architecture Design

## Overview
Sistem generasi laporan modular dengan GUI yang memungkinkan pemilihan bulan, estate, dan template laporan dengan arsitektur bersih yang memisahkan concerns.

## Architecture Layers

### 1. Presentation Layer (GUI)
- **MainReportWindow**: Window utama dengan dropdown bulan, multi-select estate, dan pilihan template
- **Components**:
  - `MonthSelectionWidget`: Dropdown untuk memilih bulan (YYYY-MM)
  - `EstateMultiSelectWidget`: Multi-select widget untuk estate
  - `TemplateSelectionWidget`: Pilihan template laporan
  - `ProgressIndicatorWidget`: Progress bar dan status
  - `ExportOptionsWidget`: Pilihan format export (PDF/Excel)

### 2. Business Logic Layer (Services)
- **TemplateService**: Mengelola loading dan validasi template
- **ReportGenerationService**: Orchestrator untuk proses generasi laporan
- **DataExtractionService**: Ekstraksi data berdasarkan parameter
- **ExportService**: Export ke berbagai format
- **ValidationService**: Validasi input dan business rules

### 3. Data Access Layer (Repositories)
- **TemplateRepository**: Akses ke template files
- **DatabaseRepository**: Akses ke database FFB Scanner
- **ConfigurationRepository**: Akses ke konfigurasi sistem
- **ReportRepository**: Penyimpanan hasil laporan

### 4. Domain Layer (Models)
- **ReportTemplate**: Model untuk template laporan
- **ReportRequest**: Model untuk request generasi laporan
- **ReportResult**: Model untuk hasil laporan
- **Estate**: Model untuk estate
- **ReportConfiguration**: Model untuk konfigurasi laporan

## Directory Structure
```
modular_report_system/
├── architecture/
│   └── system_design.md
├── src/
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── main_report_window.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── month_selection_widget.py
│   │       ├── estate_multiselect_widget.py
│   │       ├── template_selection_widget.py
│   │       ├── progress_indicator_widget.py
│   │       └── export_options_widget.py
│   ├── business/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── template_service.py
│   │   │   ├── report_generation_service.py
│   │   │   ├── data_extraction_service.py
│   │   │   ├── export_service.py
│   │   │   └── validation_service.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── report_template.py
│   │       ├── report_request.py
│   │       ├── report_result.py
│   │       ├── estate.py
│   │       └── report_configuration.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── template_repository.py
│   │   │   ├── database_repository.py
│   │   │   ├── configuration_repository.py
│   │   │   └── report_repository.py
│   │   └── connectors/
│   │       ├── __init__.py
│   │       └── firebird_connector.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   └── logger_config.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── app_config.py
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       └── custom_exceptions.py
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py
│       ├── file_utils.py
│       └── validation_utils.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── config/
│   ├── app_settings.json
│   ├── templates_config.json
│   └── estates_config.json
├── templates/
│   └── (template files)
├── reports/
│   └── (generated reports)
├── logs/
│   └── (log files)
├── requirements.txt
├── main.py
└── README.md
```

## Key Design Principles

### 1. Separation of Concerns
- GUI hanya menangani presentasi dan user interaction
- Business logic terpisah dari presentasi
- Data access terisolasi dalam repositories

### 2. Dependency Injection
- Services menerima dependencies melalui constructor
- Memudahkan testing dan maintenance

### 3. Template-Based Architecture
- Template system yang fleksibel dan extensible
- Template validation dan loading yang robust

### 4. Error Handling Strategy
- Centralized exception handling
- User-friendly error messages
- Comprehensive logging

### 5. Progress Tracking
- Real-time progress updates
- Cancellable operations
- Status reporting

## Integration Points

### 1. Existing Codebase Integration
- Menggunakan `gui_multi_estate_ffb_analysis.py` sebagai entry point
- Memanfaatkan existing `FirebirdConnector`
- Kompatibel dengan struktur database yang ada

### 2. Template System Integration
- Membaca dari `template_exact_match.json`
- Support untuk multiple template formats
- Dynamic template loading

### 3. Configuration Integration
- Menggunakan existing configuration files
- Estate configuration compatibility
- Database path management

## Extensibility Features

### 1. Template Extensibility
- Plugin-based template system
- Custom template validators
- Template inheritance support

### 2. Export Format Extensibility
- Pluggable export formats
- Custom export handlers
- Format-specific configurations

### 3. Data Source Extensibility
- Multiple database support
- Custom data extractors
- Data transformation pipelines

## Performance Considerations

### 1. Asynchronous Operations
- Non-blocking UI during report generation
- Background processing with progress updates
- Cancellable long-running operations

### 2. Memory Management
- Streaming data processing for large datasets
- Efficient memory usage patterns
- Garbage collection optimization

### 3. Caching Strategy
- Template caching
- Configuration caching
- Database connection pooling

## Security Considerations

### 1. Input Validation
- Comprehensive input sanitization
- SQL injection prevention
- Path traversal protection

### 2. File System Security
- Secure file operations
- Temporary file cleanup
- Access control validation

### 3. Database Security
- Secure connection handling
- Credential management
- Query parameterization