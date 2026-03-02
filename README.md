# 🚀 World Scientific Publishing - AI Sales Assistant

> **Transform your publishing data into actionable sales intelligence with AI-powered insights**

An intelligent sales and marketing assistant that helps World Scientific Publishing teams make data-driven decisions about university partnerships, author relationships, and market opportunities using natural language queries.

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Sample Queries](#-sample-queries)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Advanced Features](#-advanced-features)
- [FAQ](#-faq)
- [Support](#-support)

---

## ✨ Features

### 🤖 AI-Enhanced Query Processing
- **Natural Language Understanding**: Ask questions in plain English
- **Smart Pattern Matching**: Instant responses for common business queries
- **OpenAI Integration**: Advanced analysis using Bitdeer OpenAI API
- **Contextual Intelligence**: Understands sales and marketing context

### 📊 Business Intelligence Capabilities
- **University Prioritization**: Rank institutions by author count, publications, and activity
- **Author Analytics**: Identify top researchers and collaboration opportunities
- **Revenue Analysis**: Track performance across countries and regions
- **Market Intelligence**: Discover emerging markets and growth opportunities
- **Journal Performance**: Analyze publication trends and productivity

### 🎨 User Interface
- **Beautiful Dashboard**: Modern, responsive web interface
- **Real-time Results**: Live data visualization and insights
- **Interactive Charts**: Visual representation of business metrics
- **One-Click Queries**: Pre-built sample queries for common use cases
- **Mobile Friendly**: Works seamlessly on desktop and mobile devices

### ⚡ Performance
- **Fast Pattern Matching**: Sub-second responses for common queries
- **Smart Caching**: Optimized database queries
- **Scalable Architecture**: Handles large datasets efficiently
- **Fallback Support**: Works even without API key (limited features)

---

## 🚀 Quick Start

Get up and running in 3 minutes:

```bash
# 1. Clone or download the project
cd wsp-sales-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your credentials
# Edit .env file with your database password and API key

# 4. Start the backend
python app.py

# 5. Open dashboard.html in your browser
```

**Test Query:** *"Sales team visiting China which universities to prioritise"*

---

## 💻 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **MySQL/MariaDB**: 5.7 or higher (with your World Scientific database)
- **RAM**: 2GB minimum
- **Storage**: 500MB for application + database size
- **Browser**: Chrome, Firefox, Edge, or Safari (latest versions)

### Recommended Setup
- **Python**: 3.10+
- **MySQL**: 8.0+
- **RAM**: 4GB+
- **CPU**: Multi-core processor for better performance

### External Dependencies
- **Bitdeer OpenAI API**: For advanced AI features (optional but recommended)
- **Internet Connection**: Required for AI analysis

---

## 📦 Installation

### Step 1: Download the Project

Create a project folder and add these files:

```
wsp-sales-assistant/
├── app.py              # Backend server
├── dashboard.html      # Frontend interface
├── .env               # Configuration (create this)
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

### Step 2: Install Python Dependencies

```bash
# Create requirements.txt with:
Flask==2.3.3
Flask-CORS==4.0.0
mysql-connector-python==8.1.0
openai==0.28.1
pandas==2.0.3
python-dotenv==1.0.0

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database Setup

Ensure your MySQL database is running with the World Scientific Publishing schema containing these tables:
- `affid_info_xml_new`
- `book_contributor_info`
- `chapter_contributor_info`
- `bmcustomers`
- `bmtitle`
- `journal_revenue`
- `journal_subscription`
- `sales_cust_title`
- `dimension_list`

### Step 4: Optional Database Optimization

For better performance, create these indexes:

```sql
-- University analysis optimization
CREATE INDEX idx_book_contributor_country_year 
    ON book_contributor_info(country, year);
CREATE INDEX idx_book_contributor_affiliation 
    ON book_contributor_info(affiliation);

-- Revenue analysis optimization
CREATE INDEX idx_journal_revenue_country_year 
    ON journal_revenue(bill_to_country, calendar_year);

-- Author search optimization
CREATE INDEX idx_book_contributor_name 
    ON book_contributor_info(firstname, lastname);
```

---

## ⚙️ Configuration

### Create `.env` File

Create a file named `.env` in your project root:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=temp

# Bitdeer OpenAI API Configuration
OPENAI_API_KEY=your_bitdeer_api_key_here
OPENAI_BASE_URL=https://api-inference.bitdeer.ai/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3

# Optional: Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Configuration Parameters Explained

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `DB_HOST` | MySQL server address | ✅ Yes | localhost |
| `DB_USER` | MySQL username | ✅ Yes | root |
| `DB_PASSWORD` | MySQL password | ✅ Yes | (empty) |
| `DB_NAME` | Database name | ✅ Yes | temp |
| `OPENAI_API_KEY` | Bitdeer API key | ⚠️ Optional* | - |
| `OPENAI_BASE_URL` | API endpoint | ⚠️ Optional | Bitdeer URL |
| `OPENAI_MODEL` | Model to use | ⚠️ Optional | gpt-3.5-turbo |

*System works with pattern matching without API key, but AI features require it.

### Getting Your Bitdeer API Key

1. Visit [Bitdeer AI Platform](https://bitdeer.ai)
2. Sign up or log into your account
3. Navigate to **API Keys** or **Developer Settings**
4. Generate a new API key
5. Copy the key (starts with `sk-`)
6. Paste into your `.env` file

---

## 🎯 Usage

### Starting the Application

**Step 1: Start Backend Server**

```bash
# Navigate to project directory
cd wsp-sales-assistant

# Start the server
python app.py
```

You should see:
```
======================================================================
🚀 WORLD SCIENTIFIC PUBLISHING
   AI-Enhanced Sales Assistant
======================================================================
✅ Database: Connected
✅ Bitdeer API: Configured (https://api-inference.bitdeer.ai/v1)
======================================================================
🌐 Starting server on http://localhost:5000
📊 Open dashboard.html in your browser
======================================================================
```

**Step 2: Open Frontend Dashboard**

- **Option 1**: Double-click `dashboard.html`
- **Option 2**: Right-click → "Open with" → Browser
- **Option 3**: Drag and drop into browser window

### Using the Dashboard

#### 1. **Quick Sample Queries**
Click any pre-built query button:
- 🇨🇳 China Universities Priority
- 👥 Top CS Authors
- 💰 2024 Revenue Analysis
- 📰 Singapore Journals
- 🌍 Emerging Markets
- 📊 APAC Subscriptions

#### 2. **Custom Queries**
Type natural language questions:
- "Which universities in Beijing have the most authors?"
- "Show me revenue trends in Asia for last 3 years"
- "Find top journals in materials science"
- "Authors with most recent publications in physics"

#### 3. **Interpreting Results**

Results are displayed in three sections:

**📊 Summary Stats**
- Total records found
- Analysis type
- Key metrics

**💡 AI Insights**
- Business recommendations
- Strategic opportunities
- Market trends
- Action items

**📋 Data Table**
- Detailed results
- Priority badges (High/Medium/Low)
- Sortable columns
- Contact information

---

## 🔍 Sample Queries

### University Prioritization

```
"Sales team visiting China which universities to prioritise"
```
**Returns:**
- Ranked list of Chinese universities
- Author counts and publication metrics
- Priority levels (High/Medium/Low)
- Contact emails and recent activity
- Strategic recommendations

### Author Intelligence

```
"Top 10 most productive authors in computer science"
```
**Returns:**
- Author names and affiliations
- Publication counts and rates
- Active years and latest work
- Contact information
- Collaboration opportunities

### Revenue Analysis

```
"Revenue performance analysis by country for 2024"
```
**Returns:**
- Country-wise revenue breakdown
- Market categories (Major/Growing/Emerging)
- Year-over-year comparisons
- Strategic insights
- Growth opportunities

### Journal Performance

```
"Which journals perform best in Singapore"
```
**Returns:**
- Journal productivity metrics
- Author engagement statistics
- Regional performance
- Subscription trends
- Content strategy recommendations

### Market Intelligence

```
"Find emerging markets with growth potential"
```
**Returns:**
- Market opportunity assessment
- Growth patterns and trends
- Competitive landscape
- Expansion recommendations
- Risk analysis

### Subscription Analysis

```
"Show subscription trends in Asia Pacific region"
```
**Returns:**
- Regional subscription patterns
- Customer segmentation (Premium/Standard/Basic)
- Revenue trends
- Market penetration
- Retention insights

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────┐
│   Web Browser       │
│  (dashboard.html)   │
└──────────┬──────────┘
           │ HTTP/JSON
           ▼
┌─────────────────────┐
│   Flask Backend     │
│     (app.py)        │
│                     │
│  ┌───────────────┐  │
│  │ AI Assistant  │  │
│  │ - Pattern     │  │
│  │   Matching    │  │
│  │ - OpenAI      │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌──────────┐
│ MySQL   │  │ Bitdeer  │
│Database │  │ OpenAI   │
└─────────┘  └──────────┘
```

### Components

#### **Frontend (dashboard.html)**
- **Technology**: HTML5, CSS3, JavaScript, Chart.js
- **Responsibilities**:
  - User interface and interactions
  - Query input and submission
  - Results visualization
  - Status monitoring

#### **Backend (app.py)**
- **Technology**: Python, Flask, Flask-CORS
- **Components**:
  - `AIDatabase`: Database connection and query execution
  - `AIAssistant`: Query analysis and processing
  - REST API endpoints
- **Responsibilities**:
  - Natural language processing
  - SQL query generation
  - Data retrieval and formatting
  - AI insight generation

#### **Database (MySQL)**
- **Technology**: MySQL/MariaDB
- **Content**: World Scientific Publishing data
- **Optimization**: Indexed for fast queries

#### **AI Service (Bitdeer OpenAI)**
- **Technology**: OpenAI GPT-3.5-turbo via Bitdeer
- **Purpose**: Advanced query analysis and insight generation
- **Fallback**: Pattern matching when unavailable

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### **1. Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "✅ connected",
  "ai_service": "✅ Bitdeer configured",
  "api_endpoint": "https://api-inference.bitdeer.ai/v1",
  "features": {
    "pattern_matching": "✅ active",
    "ai_analysis": "✅ active",
    "smart_insights": "✅ active"
  },
  "timestamp": "2025-09-18T22:22:29.684022"
}
```

#### **2. Process Query**
```http
POST /api/query
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Sales team visiting China which universities to prioritise"
}
```

**Response:**
```json
{
  "success": true,
  "query": "Sales team visiting China which universities to prioritise",
  "results": {
    "summary": "✅ Found 20 results using pattern_match analysis",
    "data": [
      {
        "university_name": "Tsinghua University",
        "country": "China",
        "author_count": 45,
        "publication_count": 123,
        "priority_level": "High Priority",
        "contact_emails": "email1@example.com; email2@example.com",
        "latest_publication_year": 2024
      }
    ],
    "insights": [
      "📊 20 universities identified with 850 total authors",
      "🏆 Top priority: Tsinghua University with 45 authors",
      "🔥 15 universities with recent publications (2023+)"
    ],
    "query_type": "china_universities",
    "ai_context": "University prioritization for China market expansion"
  },
  "timestamp": "2025-09-18T22:25:00.123456"
}
```

#### **3. Sample Queries**
```http
GET /api/sample-queries
```

**Response:**
```json
{
  "sample_queries": [
    {
      "query": "Sales team visiting China which universities to be prioritised",
      "category": "🇨🇳 University Prioritization",
      "description": "AI-powered university ranking for China market",
      "expected_insights": "Priority levels, contact info, author metrics"
    }
  ],
  "ai_features": [
    "🤖 Natural language understanding",
    "🧠 Smart query pattern matching",
    "📊 Automated insight generation",
    "🎯 Business-focused recommendations"
  ]
}
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### **Issue 1: Backend Won't Start**

**Symptoms:**
```
ImportError: No module named 'flask'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

#### **Issue 2: Database Connection Failed**

**Symptoms:**
```
❌ Database: Connection failed
```

**Solutions:**
1. **Check MySQL is running:**
   ```bash
   # Windows
   net start MySQL80
   
   # Mac
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

2. **Verify credentials in `.env`:**
   ```env
   DB_PASSWORD=correct_password_here
   ```

3. **Test connection manually:**
   ```bash
   mysql -u root -p
   USE temp;
   SHOW TABLES;
   ```

---

#### **Issue 3: "Partial Functionality" Warning**

**Symptoms:**
Dashboard shows: `⚠️ Partial Functionality`

**Meaning:**
- ✅ Database connected
- ✅ Pattern matching works
- ❌ API key missing or invalid

**Solutions:**
1. **Add API key to `.env`:**
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Restart backend:**
   ```bash
   # Stop: Ctrl+C
   python app.py
   ```

3. **System still works without API key** - just limited AI features

---

#### **Issue 4: Frontend Can't Connect**

**Symptoms:**
```
Failed to connect to AI backend
```

**Solutions:**
1. **Verify backend is running:**
   - Check terminal for startup messages
   - Visit `http://localhost:5000` in browser

2. **Check port number:**
   - Backend default: port 5000
   - If changed, update `dashboard.html`:
     ```javascript
     const API_BASE_URL = 'http://127.0.0.1:YOUR_PORT/api';
     ```

3. **Firewall/antivirus:**
   - Allow Python through firewall
   - Add exception for port 5000

---

#### **Issue 5: No Data Returned**

**Symptoms:**
Query returns empty results

**Solutions:**
1. **Verify data exists:**
   ```sql
   SELECT COUNT(*) FROM book_contributor_info;
   SELECT COUNT(*) FROM journal_revenue;
   ```

2. **Check country names:**
   ```sql
   SELECT DISTINCT country FROM book_contributor_info LIMIT 10;
   ```

3. **Try simpler query:**
   - Start with: "Show me some authors"
   - Then refine to specific countries/topics

---

#### **Issue 6: Slow Performance**

**Solutions:**
1. **Add database indexes** (see Installation section)
2. **Limit result size** - queries automatically limit to 20-50 rows
3. **Check database server resources**
4. **Optimize MySQL configuration**

---

### Debug Mode

Enable detailed logging:

```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5000)
```

Check browser console (F12) for JavaScript errors.

---

## 🚀 Advanced Features

### Custom Query Patterns

Add your own query patterns in `app.py`:

```python
self.ai_query_patterns['custom_pattern'] = {
    'keywords': ['keyword1', 'keyword2'],
    'sql': """
        SELECT your_custom_query
        FROM your_table
        WHERE conditions
    """,
    'ai_insight': 'Description of what this analyzes'
}
```

### Database Optimization

```sql
-- Analyze table statistics
ANALYZE TABLE book_contributor_info;
ANALYZE TABLE journal_revenue;

-- Check query performance
EXPLAIN SELECT * FROM book_contributor_info 
WHERE country = 'China';
```

### API Rate Limiting

Modify in `app.py` to add rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/api/query', methods=['POST'])
@limiter.limit("20 per minute")
def smart_query():
    # ... existing code
```

### Export Functionality

Add to dashboard for data export:

```javascript
function exportToCSV(data) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'wsp-export.csv';
    a.click();
}
```

---

## ❓ FAQ

### General Questions

**Q: Do I need the Bitdeer API key to use the system?**
A: No! The system works with pattern matching without an API key. You'll get university lists, author data, and revenue analysis. The API key adds enhanced AI insights and handles complex queries.

**Q: How much does the Bitdeer API cost?**
A: Pricing varies. Check [Bitdeer AI Platform](https://bitdeer.ai) for current rates. Typical usage for a sales team is very affordable.

**Q: Can I use regular OpenAI instead of Bitdeer?**
A: Yes! Just change in `.env`:
```env
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Q: Is my data secure?**
A: Yes. Data stays on your local MySQL server. Only query summaries (not full data) go to the AI service for analysis.

**Q: Can multiple users use this simultaneously?**
A: Yes! The backend handles multiple concurrent requests. Each user opens their own `dashboard.html`.

**Q: What browsers are supported?**
A: Chrome, Firefox, Edge, Safari - any modern browser from the last 2 years.

### Technical Questions

**Q: Why Python 3.8+?**
A: Uses features like f-strings and type hints that require 3.8 or newer.

**Q: Can I deploy this to a server?**
A: Yes! Deploy Flask backend to any server (AWS, Azure, Heroku, etc.). Update `API_BASE_URL` in dashboard to point to your server.

**Q: How do I backup my configuration?**
A: Copy your `.env` file to a secure location. Never commit it to version control.

**Q: Can I customize the queries?**
A: Yes! Edit the `ai_query_patterns` dictionary in `app.py` to add custom business queries.

**Q: What if my database has different table names?**
A: Update the SQL queries in `app.py` to match your table names.

---

## 📞 Support

### Getting Help

1. **Check this README** - Most answers are here
2. **Review error messages** - They usually indicate the problem
3. **Check browser console** (F12) - For frontend issues
4. **Check terminal output** - For backend issues

### Reporting Issues

When reporting problems, include:
- Error messages (full text)
- Steps to reproduce
- Your environment (OS, Python version, MySQL version)
- Backend terminal output
- Browser console output (F12 → Console tab)

### Contact

- **Project Maintainer**: World Scientific Publishing IT Team
- **Email**: [your-support-email]
- **Internal Wiki**: [your-wiki-link]

---

## 📄 License

Copyright © 2025 World Scientific Publishing

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🙏 Acknowledgments

- **World Scientific Publishing** - Data and business requirements
- **OpenAI / Bitdeer** - AI capabilities
- **Flask Team** - Backend framework
- **Chart.js** - Visualization library

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

## 🔄 Version History

### Version 1.0.0 (Current)
- ✅ Initial release
- ✅ AI-enhanced query processing
- ✅ Pattern matching for common queries
- ✅ Beautiful dashboard interface
- ✅ University prioritization
- ✅ Author and revenue analytics
- ✅ Bitdeer API integration

### Planned Features (Future Releases)
- 📊 Advanced data visualization options
- 📈 Historical trend analysis
- 🔔 Real-time alerts and notifications
- 👥 Multi-user authentication
- 📱 Mobile app version
- 📤 PDF export functionality
- 🌐 Multi-language support

---

**Built for World Scientific Publishing Sales & Marketing Teams**

*Last Updated: September 2025*
