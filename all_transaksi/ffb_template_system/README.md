# FFB Template System

A modern, web-based template management system for Fresh Fruit Bunch (FFB) Scanner Analysis in palm oil agricultural operations.

## 🌟 Features

- **Template Management**: Create, edit, and manage report templates with version control
- **Web-Based Editor**: Monaco Editor integration for advanced template editing
- **Jasper Reports Integration**: Professional PDF report generation
- **Multi-Estate Support**: Support for 10 palm oil estates
- **Real-time Preview**: Live template preview with dummy data
- **Parameter System**: Dynamic parameter substitution in SQL queries
- **REST API**: Complete API for template and report operations

## 🏗️ Architecture

### 4-Layer Architecture
```
┌─────────────────────────────────────┐
│        Presentation Layer            │
│  (Flask Web UI + Monaco Editor)     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│       Business Logic Layer          │
│   (Template Services + Jasper)      │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│        Data Access Layer            │
│  (SQLAlchemy + Repository Pattern)  │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│          Database Layer             │
│   (Firebird + Template Metadata)   │
└─────────────────────────────────────┘
```

### Key Components

#### Database Layer
- **Firebird Integration**: Native Firebird database connectivity
- **SQLAlchemy Models**: Complete ORM models for template management
- **Multi-Estate Support**: Automatic connection management for 10 estates

#### Business Logic Layer
- **Template Service**: Template validation, versioning, and management
- **Jasper Integration**: Jasper Reports engine for PDF generation
- **Parameter System**: Secure parameter substitution in SQL queries

#### API Layer
- **RESTful API**: Complete CRUD operations for templates and reports
- **Background Tasks**: Asynchronous report generation
- **File Management**: Template file upload and report download

#### Web Interface
- **Monaco Editor**: Advanced code editor for template editing
- **Bootstrap 5**: Modern, responsive UI design
- **Live Preview**: Real-time template preview functionality

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Firebird Database Server
- Java Runtime Environment (for Jasper Reports)
- Node.js (for frontend dependencies)

### Installation

1. **Clone the Repository**
```bash
git clone <repository-url>
cd ffb-template-system
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**
```bash
cd src/web/static
npm install
```

4. **Configure Database**
```json
{
  "estates": [
    {
      "name": "PGE 1A",
      "path": "path/to/PGE1A.FDB"
    }
  ]
}
```

5. **Start the Application**
```bash
# On Windows
start_app.bat

# On Linux/Mac
python src/app.py
```

## 📁 Project Structure

```
ffb_template_system/
├── src/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   └── core/
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py  # Database connection management
│       │   ├── models.py      # SQLAlchemy models
│       │   └── repositories.py # Data access layer
│       ├── templates/
│       │   ├── __init__.py
│       │   └── template_service.py # Template business logic
│       └── reports/
│           ├── __init__.py
│           └── jasper_service.py   # Jasper Reports integration
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── templates.py  # Template API routes
│   │       └── reports.py    # Report API routes
│   └── web/
│       ├── __init__.py
│       ├── routes/
│       │   └── main.py       # Web UI routes
│       └── templates/
│           ├── index.html      # Main layout
│           ├── dashboard.html  # Dashboard page
│           └── template_editor.html # Template editor
├── templates/
│   ├── jasper/               # Jasper report templates
│   └── uploads/             # Template file uploads
├── reports/                 # Generated reports
├── logs/                    # Application logs
├── config.json              # Database configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 Core Features

### Template Management

#### Creating Templates
1. Navigate to Templates → Create New Template
2. Choose template type (FFB_ANALYSIS, EMPLOYEE_PERFORMANCE, etc.)
3. Configure SQL queries with parameters
4. Set up Jasper report template
5. Test with live preview

#### Parameter System
Templates support dynamic parameters using `$P{parameter_name}` syntax:

```sql
SELECT
    t.TRANSNO,
    t.SCANUSERID,
    t.RECORDTAG,
    t.TRANSDATE,
    f.DIVID,
    d.DIVNAME
FROM FFBSCANNERDATA$P{month} t
JOIN OCFIELD f ON t.FIELDID = f.ID
LEFT JOIN CRDIVISION d ON f.DIVID = d.ID
WHERE t.TRANSDATE BETWEEN $P{start_date} AND $P{end_date}
  AND f.DIVID = $P{division_id}
```

### Report Generation

#### Jasper Reports Integration
- **Professional PDFs**: High-quality PDF reports with corporate styling
- **Dynamic Data**: Real-time data from Firebird databases
- **Charts and Graphs**: Visual representations of FFB analysis
- **Multi-page Support**: Complex report layouts with headers/footers

#### Background Processing
Reports are generated asynchronously:
1. User submits report request
2. System queues the task
3. Background processor generates report
4. User downloads completed report

### Multi-Estate Support

The system supports analysis across multiple palm oil estates:
- PGE 1A, PGE 1B, PGE 2A, PGE 2B
- IJL, DME, Are B2, Are B1
- Are A, Are C

## 📊 Template Types

### FFB_ANALYSIS
Comprehensive FFB transaction analysis with:
- Verification rates by employee
- Discrepancy identification
- Performance metrics
- Estate comparisons

### EMPLOYEE_PERFORMANCE
Individual employee performance reports:
- Transaction counts
- Verification percentages
- Quality scores
- Trend analysis

### DATA_QUALITY
Data quality assessment reports:
- Data completeness
- Error identification
- Validation results
- Improvement recommendations

### SUMMARY
Executive summary reports:
- KPI dashboards
- Monthly comparisons
- Estate performance summaries
- Management insights

## 🔧 Configuration

### Database Configuration (`config.json`)
```json
{
  "estates": [
    {
      "name": "PGE 1A",
      "path": "C:/Database/PGE1A.FDB",
      "host": "localhost",
      "port": 3050
    }
  ],
  "jasper": {
    "compiler_path": "C:/Program Files/JasperSoft/jasperreports/lib",
    "temp_dir": "temp/jasper"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log"
  }
}
```

### Security Configuration
- **SQL Injection Prevention**: Parameterized queries
- **Template Validation**: Security checks for template content
- **Access Control**: Role-based access control ready
- **Audit Trail**: Complete logging of template operations

## 🌐 API Reference

### Template Management

#### Create Template
```http
POST /api/templates
Content-Type: application/json

{
  "name": "Monthly Performance Report",
  "type": "FFB_ANALYSIS",
  "description": "Monthly FFB analysis report",
  "sql_query": "SELECT * FROM FFBSCANNERDATA$P{month}...",
  "parameters": [
    {"name": "month", "type": "string", "required": true},
    {"name": "start_date", "type": "date", "required": true}
  ],
  "jasper_template": "jasper/ffb_analysis.jrxml"
}
```

#### Execute Template
```http
POST /api/templates/{id}/execute
Content-Type: application/json

{
  "parameters": {
    "month": "09",
    "start_date": "2025-09-01",
    "end_date": "2025-09-30"
  },
  "estates": ["PGE 1A", "PGE 1B"]
}
```

### Report Management

#### Download Report
```http
GET /api/reports/{id}/download
Response: Binary PDF file
```

#### Get Report Status
```http
GET /api/reports/{id}/status
Response:
{
  "id": "report_id",
  "status": "completed",
  "progress": 100,
  "download_url": "/api/reports/{id}/download"
}
```

## 🎨 User Interface

### Dashboard
- System overview cards
- Recent templates list
- Quick actions panel
- System status indicators

### Template Editor
- Monaco Editor with syntax highlighting
- Parameter management interface
- Live preview functionality
- SQL validation tools

### Report Viewer
- Interactive report list
- Filter and search capabilities
- Download and share options
- Generation progress tracking

## 🔄 Migration from Legacy System

### Data Migration
1. **Export existing data**: Use legacy system export tools
2. **Import template data**: Use migration scripts
3. **Validate data integrity**: Run verification checks
4. **Update references**: Update all system references

### Template Migration
1. **Analyze existing reports**: Document current report requirements
2. **Create equivalent templates**: Build new templates
3. **Test output compatibility**: Ensure consistent results
4. **Train users**: Provide training on new system

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### System Tests
```bash
python -m pytest tests/system/
```

## 📈 Performance

### Optimization Features
- **Connection Pooling**: Efficient database connection management
- **Query Caching**: Cache frequent query results
- **Async Processing**: Background task execution
- **Lazy Loading**: On-demand data loading

### Scalability
- **Multi-tenant**: Support for multiple estates
- **Load Balancing**: Ready for horizontal scaling
- **Database Sharding**: Support for large datasets
- **CDN Integration**: Static asset optimization

## 🔍 Monitoring

### Logging
- **Application Logs**: Detailed system operation logs
- **Audit Trails**: Complete user action tracking
- **Error Tracking**: Comprehensive error reporting
- **Performance Metrics**: System health monitoring

### Health Checks
```http
GET /api/health
Response:
{
  "status": "healthy",
  "database": "connected",
  "jasper": "available",
  "memory_usage": "75%"
}
```

## 🛠️ Development

### Adding New Template Types
1. Create new template type enum
2. Add validation rules
3. Create sample Jasper template
4. Update documentation

### Extending API
1. Add new route in appropriate file
2. Implement business logic
3. Add tests
4. Update API documentation

### Customizing UI
1. Modify HTML templates in `src/web/templates/`
2. Update CSS in `src/web/static/css/`
3. Add JavaScript in `src/web/static/js/`
4. Test responsiveness

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Template management system
- ✅ Jasper Reports integration
- ✅ Web-based editor
- ✅ Multi-estate support

### Phase 2 (Planned)
- 🔄 User authentication and authorization
- 🔄 Advanced scheduling system
- 🔄 Email notifications
- 🔄 Mobile-responsive design

### Phase 3 (Future)
- 📊 Machine learning integration
- 📊 Advanced analytics
- 📊 API integrations
- 📊 Cloud deployment options

---

**Built for Palm Oil Agricultural Operations** 🌴

A comprehensive solution for FFB scanner data analysis and reporting across multiple estates.