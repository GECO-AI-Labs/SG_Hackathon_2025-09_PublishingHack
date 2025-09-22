#!/usr/bin/env python3
"""
World Scientific Publishing - AI-Enhanced Sales Assistant
DB-first pipeline with rule-based insights, year/region filters, and readable visualizations
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv
import re

# ---- Load .env (must be next to this file) ----
load_dotenv()

app = Flask(__name__)
CORS(app)

# ---- DB CONFIG ----
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "temp"),
    "charset": "utf8mb4",
    "connection_timeout": 10,
}

# ---------- DB LAYER ----------
class AIDatabase:
    def __init__(self):
        self.connection = None
        # Patterns tuned to your schema and use-cases
        self.ai_query_patterns = {
            # 1) China universities
            "china_universities": {
                "keywords": ["china", "chinese", "university", "universities", "visit", "priority", "prioritise", "prioritize"],
                "sql": """
                    SELECT 
                        affiliation AS university_name,
                        country,
                        COUNT(DISTINCT CONCAT(firstname, ' ', lastname)) AS author_count,
                        COUNT(DISTINCT bookcode) AS publication_count,
                        GROUP_CONCAT(DISTINCT email ORDER BY email SEPARATOR '; ') AS contact_emails,
                        MAX(year) AS latest_publication_year,
                        CASE 
                            WHEN COUNT(DISTINCT CONCAT(firstname, ' ', lastname)) >= 20 THEN 'High Priority'
                            WHEN COUNT(DISTINCT CONCAT(firstname, ' ', lastname)) >= 10 THEN 'Medium Priority'
                            ELSE 'Low Priority'
                        END AS priority_level
                    FROM book_contributor_info
                    WHERE UPPER(country) LIKE '%CHINA%'
                      AND affiliation IS NOT NULL AND affiliation <> '' AND LENGTH(affiliation) > 5
                    GROUP BY affiliation, country
                    HAVING author_count >= 3
                    ORDER BY author_count DESC, publication_count DESC
                    LIMIT 25;
                """,
                "insight": "University prioritization for China market expansion",
                "viz": {"label_field": "university_name", "value_field": "author_count", "value_label": "Unique Authors"}
            },

            # 2) APAC subscriptions
            "apac_subscriptions": {
                "keywords": ["apac", "asia pacific", "subscription", "subscriptions", "subscriber", "subscribed"],
                "sql": """
                    WITH apac_unis AS (
                        SELECT 
                            affiliation AS university_name,
                            country,
                            COUNT(DISTINCT CONCAT(firstname, ' ', lastname)) AS author_count,
                            COUNT(DISTINCT bookcode) AS publication_count
                        FROM book_contributor_info
                        WHERE country IS NOT NULL AND country <> ''
                          AND (
                               UPPER(country) IN ('SINGAPORE','MALAYSIA','INDONESIA','THAILAND','VIETNAM','PHILIPPINES','BRUNEI','MYANMAR','LAOS','CAMBODIA')
                            OR UPPER(country) IN ('CHINA','HONG KONG','TAIWAN','JAPAN','KOREA','SOUTH KOREA')
                            OR UPPER(country) IN ('INDIA','PAKISTAN','BANGLADESH','SRI LANKA','NEPAL')
                            OR UPPER(country) IN ('AUSTRALIA','NEW ZEALAND')
                          )
                          AND affiliation IS NOT NULL AND affiliation <> '' AND LENGTH(affiliation) > 5
                        GROUP BY affiliation, country
                    ),
                    country_subs AS (
                        SELECT 
                            country,
                            region,
                            SUM(COALESCE(subscription_qty,0)) AS total_subscriptions,
                            SUM(COALESCE(nett_value_SGD,0)) AS total_revenue_sgd
                        FROM journal_subscription
                        WHERE content_year >= 2022
                          AND nett_value_SGD > 0
                        GROUP BY country, region
                    )
                    SELECT 
                        a.university_name,
                        a.country,
                        a.author_count,
                        a.publication_count,
                        CASE WHEN COALESCE(cs.total_subscriptions,0) > 0 THEN 'Country Subscribed' ELSE 'No Country Subscription' END AS subscription_status,
                        COALESCE(cs.total_subscriptions, 0) AS country_subscription_qty,
                        COALESCE(cs.total_revenue_sgd, 0) AS country_subscription_revenue_sgd,
                        cs.region AS country_region
                    FROM apac_unis a
                    LEFT JOIN country_subs cs
                      ON UPPER(a.country) = UPPER(cs.country)
                    ORDER BY cs.total_revenue_sgd DESC, a.author_count DESC
                    LIMIT 50;
                """,
                "insight": "APAC universities with country-level subscription signal",
                "viz": {"label_field": "country", "value_field": "country_subscription_revenue_sgd", "value_label": "Country Subscription Revenue (SGD)"}
            },

            # 3) NTU vs NUS comparison
            "ntu_nus_compare": {
                "keywords": ["ntu", "nus", "nanyang", "national university of singapore", "compare", "comparison"],
                "sql": """
                    SELECT 
                        CASE
                            WHEN UPPER(affiliation) LIKE '%NANYANG TECHNOLOGICAL UNIVERSITY%' OR UPPER(affiliation) LIKE '% NTU %' THEN 'NTU'
                            WHEN UPPER(affiliation) LIKE '%NATIONAL UNIVERSITY OF SINGAPORE%' OR UPPER(affiliation) LIKE '% NUS %' THEN 'NUS'
                            ELSE 'OTHER'
                        END AS university,
                        COUNT(DISTINCT CONCAT(firstname, ' ', lastname)) AS author_count,
                        COUNT(DISTINCT bookcode) AS publication_count,
                        MAX(year) AS latest_publication_year,
                        MIN(year) AS first_publication_year
                    FROM book_contributor_info
                    WHERE affiliation IS NOT NULL AND affiliation <> ''
                      AND (
                            UPPER(affiliation) LIKE '%NANYANG TECHNOLOGICAL UNIVERSITY%'
                         OR UPPER(affiliation) LIKE '%NATIONAL UNIVERSITY OF SINGAPORE%'
                         OR UPPER(affiliation) LIKE '% NTU %'
                         OR UPPER(affiliation) LIKE '% NUS %'
                      )
                    GROUP BY university
                    HAVING university IN ('NTU', 'NUS')
                    ORDER BY publication_count DESC;
                """,
                "insight": "Head-to-head: NTU vs NUS research output",
                "viz": {"label_field": "university", "value_field": "publication_count", "value_label": "Distinct Publications"}
            },

            # 4) Top authors
            "top_authors": {
                "keywords": ["top author", "best author", "researcher", "productive", "most productive authors", "top 10 authors"],
                "sql": """
                    SELECT 
                        CONCAT(firstname, ' ', lastname) AS author_name,
                        email,
                        affiliation AS university,
                        country,
                        COUNT(DISTINCT bookcode) AS publication_count,
                        MAX(year) AS latest_publication,
                        MIN(year) AS first_publication,
                        (MAX(year) - MIN(year) + 1) AS active_years,
                        ROUND(COUNT(DISTINCT bookcode) / NULLIF((MAX(year) - MIN(year) + 1),0), 2) AS publications_per_year
                    FROM book_contributor_info
                    WHERE firstname IS NOT NULL AND lastname IS NOT NULL
                      AND firstname <> '' AND lastname <> ''
                    GROUP BY firstname, lastname, email, affiliation, country
                    HAVING publication_count >= 2
                    ORDER BY publication_count DESC, publications_per_year DESC
                    LIMIT 15;
                """,
                "insight": "Top researcher identification",
                "viz": {"label_field": "author_name", "value_field": "publication_count", "value_label": "Publications"}
            },

            # 5) Revenue analysis
            "revenue_analysis": {
                "keywords": ["revenue", "sales", "income", "profit", "financial", "earnings", "market"],
                "sql": """
                    SELECT 
                        bill_to_country AS country,
                        bill_to_region AS region,
                        calendar_year AS year,
                        COUNT(DISTINCT journal_id) AS journal_count,
                        SUM(COALESCE(gross_base, 0)) AS total_gross_revenue,
                        SUM(COALESCE(net_base, 0)) AS total_net_revenue,
                        AVG(COALESCE(net_base, 0)) AS avg_transaction_value,
                        SUM(COALESCE(qty, 0)) AS total_quantity_sold,
                        CASE 
                            WHEN SUM(COALESCE(net_base, 0)) >= 100000 THEN 'Major Market'
                            WHEN SUM(COALESCE(net_base, 0)) >= 50000 THEN 'Growing Market'
                            ELSE 'Emerging Market'
                        END AS market_category
                    FROM journal_revenue
                    WHERE bill_to_country IS NOT NULL 
                      AND calendar_year >= 2022
                      AND net_base > 0
                    GROUP BY bill_to_country, bill_to_region, calendar_year
                    ORDER BY calendar_year DESC, total_net_revenue DESC
                    LIMIT 30;
                """,
                "insight": "Revenue performance by market",
                "viz": {"label_field": "country", "value_field": "total_net_revenue", "value_label": "Net Revenue"}
            },
        }

    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            # verify connection
            self.connection.ping(reconnect=True, attempts=2, delay=1)
            print("✅ MySQL connected:", DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["database"], DB_CONFIG["user"])
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("❌ Access denied (check DB_USER/DB_PASSWORD).", err)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("❌ Database does not exist (check DB_NAME).", err)
            else:
                print("❌ MySQL error:", err)
            return False
        except Exception as e:
            print("❌ Unexpected DB error:", e)
            return False

    def _ensure_conn(self) -> bool:
        if not self.connection or not self.connection.is_connected():
            return self.connect()
        return True

    def execute_query_params(self, sql: str, params: List[Any]) -> List[Dict]:
        if not self._ensure_conn():
            return []
        try:
            cur = self.connection.cursor(dictionary=True)
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"❌ Query error: {e}\nSQL: {sql}\nParams: {params}")
            return []

# ---------- YEAR / REGION FILTER PARSER ----------
REGION_ALIASES = {
    "APAC": {"APAC", "ASIA PACIFIC", "ASIA-PACIFIC", "ASIA"},
    "EMEA": {"EMEA", "EUROPE", "MIDDLE EAST", "AFRICA"},
    "AMER": {"AMER", "AMERICA", "AMERICAS", "NORTH AMERICA", "SOUTH AMERICA", "LATAM"},
}
COUNTRY_TO_REGION = {
    "SINGAPORE": "APAC", "MALAYSIA": "APAC", "INDIA": "APAC", "CHINA": "APAC", "JAPAN": "APAC",
    "AUSTRALIA": "APAC", "NEW ZEALAND": "APAC",
    "UNITED KINGDOM": "EMEA", "FRANCE": "EMEA", "GERMANY": "EMEA", "UAE": "EMEA", "SOUTH AFRICA": "EMEA",
    "UNITED STATES": "AMER", "USA": "AMER", "CANADA": "AMER", "BRAZIL": "AMER", "MEXICO": "AMER",
}

YEAR_RE = re.compile(r"(?:(since|from)\s+)?(20\d{2})(?:\s*[-–—]\s*(20\d{2}))?", re.IGNORECASE)
REGION_RE = re.compile(r"\b(APAC|ASIA PACIFIC|ASIA-PACIFIC|ASIA|EMEA|EUROPE|MIDDLE EAST|AFRICA|AMER|AMERICAS|NORTH AMERICA|SOUTH AMERICA|LATAM)\b", re.IGNORECASE)

def detect_filters(user_query: str) -> Dict[str, Any]:
    q_upper = user_query.upper()

    years = None
    m = YEAR_RE.search(q_upper)
    if m:
        since_kw, y1, y2 = m.groups()
        y1, y2 = int(y1), int(y2) if y2 else None
        if since_kw or (y2 and y2 >= y1):
            years = {"mode": "range", "from": y1, "to": y2 or 9999}
        else:
            years = {"mode": "eq", "year": y1}

    region = None
    rm = REGION_RE.search(q_upper)
    if rm:
        token = rm.group(1).upper().replace("-", " ")
        for key, aliases in REGION_ALIASES.items():
            if token in aliases:
                region = {"type": "macro", "value": key}
                break

    # country inference (optional)
    countries: List[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z ]{1,30}", user_query):
        T = token.strip().upper()
        if T in COUNTRY_TO_REGION and T not in countries:
            countries.append(T)

    if countries and not region:
        macro = COUNTRY_TO_REGION[countries[0]]
        region = {"type": "macro", "value": macro}

    return {"years": years, "region": region, "countries": countries}

# ---------- RULE-BASED INSIGHTS ----------
class InsightEngine:
    @staticmethod
    def for_china_universities(data: List[Dict]) -> List[str]:
        if not data: return ["No data found for China universities."]
        top = data[:5]
        insights = [
            f"📊 Identified {len(data)} Chinese universities with ≥3 unique authors.",
        ]
        if top:
            insights.append(f"🏆 Top university by authors: {top[0].get('university_name')} ({top[0].get('author_count')} authors)")
        high = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('high'))
        med  = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('medium'))
        low  = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('low'))
        insights.append(f"🎯 Priority mix → High: {high}, Medium: {med}, Low: {low}.")
        with_contacts = sum(1 for r in data if r.get('contact_emails'))
        insights.append(f"✉️ Contact emails available for {with_contacts} universities.")
        insights.append("💡 Action: Visit High Priority universities first; prepare co-publishing pitches and invite top authors for campus events.")
        return [i for i in insights if i]

    @staticmethod
    def for_apac_subscriptions(data: List[Dict]) -> List[str]:
        if not data: return ["No APAC university data available."]
        subscribed = sum(1 for r in data if str(r.get("subscription_status","")).startswith("Country Subscribed"))
        not_sub = len(data) - subscribed
        top_country = max(data, key=lambda r: float(r.get("country_subscription_revenue_sgd", 0))) if data else {}
        insights = [
            f"🌏 {len(data)} APAC universities analyzed across multiple countries.",
            f"💼 Country subscription signal → Subscribed: {subscribed}, Not Subscribed: {not_sub}.",
            f"💰 Highest subscription revenue (country): {top_country.get('country','N/A')} ({int(float(top_country.get('country_subscription_revenue_sgd',0))):,} SGD).",
            "🎯 Action: Focus on unis in subscribed countries with high author/publication counts; pilot bundles elsewhere."
        ]
        return insights

    @staticmethod
    def for_ntu_nus_compare(data: List[Dict]) -> List[str]:
        if not data: return ["No NTU/NUS data available."]
        lookup = {r["university"]: r for r in data}
        ntu, nus = lookup.get("NTU"), lookup.get("NUS")
        insights = []
        if ntu and nus:
            insights.append(f"🏁 NTU vs NUS — Publications: NTU {ntu['publication_count']} vs NUS {nus['publication_count']}.")
            insights.append(f"👥 Unique authors: NTU {ntu['author_count']} vs NUS {nus['author_count']}.")
            insights.append(f"⏳ Active span: NTU {ntu.get('first_publication_year')}–{ntu.get('latest_publication_year')} vs NUS {nus.get('first_publication_year')}–{nus.get('latest_publication_year')}.")
            focus = 'NTU' if ntu['publication_count'] >= nus['publication_count'] else 'NUS'
            insights.append(f"🎯 Action: Prioritize {focus} for keynotes; run cross-campus campaigns at the other.")
        else:
            insights.append("ℹ️ Could not find both NTU and NUS; check affiliation patterns.")
        return insights

    @staticmethod
    def for_top_authors(data: List[Dict]) -> List[str]:
        if not data: return ["No top authors found."]
        top = data[:5]
        insights = [
            f"🏆 Top {len(top)} prolific authors identified (≥2 publications).",
        ]
        insights.extend([f"• {r['author_name']} — {r['publication_count']} pubs ({r.get('publications_per_year','-')}/yr)" for r in top])
        insights.append("🎯 Action: Invite top authors for editorial boards and special issues; target co-authorships.")
        return insights

    @staticmethod
    def for_revenue(data: List[Dict]) -> List[str]:
        if not data: return ["No revenue rows available."]
        by_year: Dict[int, float] = {}
        for r in data:
            y = int(r["year"])
            by_year[y] = by_year.get(y, 0.0) + float(r.get("total_net_revenue", 0))
        latest_year = max(by_year) if by_year else None
        top_market = max(data, key=lambda r: float(r.get("total_net_revenue",0)))
        insights = [
            f"📈 Revenue across {len(set(r['country'] for r in data))} countries.",
            f"🗓️ Latest year analyzed: {latest_year}",
            f"💰 Top market (net): {top_market['country']} — {int(float(top_market['total_net_revenue'])):,}",
            "🎯 Action: Double down on top markets; test pricing uplift and bundles; seed emerging markets with campus-wide trials."
        ]
        return insights

    @staticmethod
    def generic(data: List[Dict]) -> List[str]:
        if not data: return ["No data found."]
        return [
            f"📊 Returned {len(data)} records.",
            "💡 Tip: Filter by country/affiliation keywords to surface more specific opportunities.",
        ]

# ---------- QUERY ANALYZER ----------
class Analyzer:
    def __init__(self, db: AIDatabase):
        self.db = db

    def analyze(self, user_query: str) -> Dict[str, Any]:
        filters = detect_filters(user_query)
        q = user_query.lower()
        best, score = None, 0
        for name, pat in self.db.ai_query_patterns.items():
            s = sum(1 for kw in pat["keywords"] if kw in q)
            if s > score and s >= 2:
                best, score = name, s

        if best:
            pat = self.db.ai_query_patterns[best]
            return {
                "query_type": best,
                "sql_query": pat["sql"],
                "ai_context": pat["insight"],
                "viz": pat["viz"],
                "method": "pattern_match",
                "filters": filters,
            }
        return {
            "query_type": "general",
            "sql_query": "SELECT 'No matching query pattern' AS message",
            "ai_context": "General analysis",
            "viz": {"label_field": None, "value_field": None, "value_label": None},
            "method": "fallback",
            "filters": filters,
        }

# ---------- APPLY FILTERS SAFELY ----------
def apply_filters(sql_base: str, plan: Dict[str, Any]) -> Tuple[str, List[Any]]:
    filters = plan.get("filters", {})
    years = filters.get("years")
    region = filters.get("region")
    countries = filters.get("countries", [])

    params: List[Any] = []
    sql = sql_base
    qtype = plan.get("query_type")

    def year_clause(col: str):
        if not years: return "", []
        if years["mode"] == "eq":
            return f" AND {col} = %s ", [years["year"]]
        else:
            return f" AND {col} BETWEEN %s AND %s ", [years["from"], years["to"]]

    def region_clause(col_region: str = None, col_country: str = None):
        if not region and not countries: return "", []
        if region and region.get("type") == "macro":
            macro = region["value"]
            if col_region:
                return f" AND UPPER({col_region}) = %s ", [macro]
            if col_country:
                mapped = [c for c, m in COUNTRY_TO_REGION.items() if m == macro]
                if mapped:
                    ph = ",".join(["%s"] * len(mapped))
                    return f" AND UPPER({col_country}) IN ({ph}) ", mapped
        if countries and col_country:
            ph = ",".join(["%s"] * len(countries))
            return f" AND UPPER({col_country}) IN ({ph}) ", countries
        return "", []

    if qtype == "china_universities":
        yc, yp = year_clause("year")
        rc, rp = region_clause(None, "country")
        sql = sql.replace("GROUP BY affiliation, country", f"{yc}{rc} GROUP BY affiliation, country")
        params += yp + rp

    elif qtype == "apac_subscriptions":
        yc1, yp1 = year_clause("year")
        yc2, yp2 = year_clause("content_year")
        rc_unis, rp_unis = region_clause(None, "country")
        rc_subs, rp_subs = region_clause("region", "country")
        sql = sql.replace("GROUP BY affiliation, country", f"{yc1}{rc_unis} GROUP BY affiliation, country")
        sql = sql.replace("WHERE content_year >= 2022", f"WHERE content_year >= 2022{yc2}{rc_subs}")
        params += yp1 + rp_unis + yp2 + rp_subs

    elif qtype == "ntu_nus_compare":
        yc, yp = year_clause("year")
        sql = sql.replace("GROUP BY university", f"{yc} GROUP BY university")
        params += yp

    elif qtype == "top_authors":
        yc, yp = year_clause("year")
        rc, rp = region_clause(None, "country")
        sql = sql.replace(
            "GROUP BY firstname, lastname, email, affiliation, country",
            f"{yc}{rc} GROUP BY firstname, lastname, email, affiliation, country"
        )
        params += yp + rp

    elif qtype == "revenue_analysis":
        yc, yp = year_clause("calendar_year")
        rc, rp = region_clause("bill_to_region", "bill_to_country")
        sql = sql.replace("AND calendar_year >= 2022", f"AND calendar_year >= 2022{yc}{rc}")
        params += yp + rp

    return sql, params

# ---------- HELPERS ----------
def rule_based_insights(qtype: str, rows: List[Dict]) -> List[str]:
    if qtype == "china_universities":
        return InsightEngine.for_china_universities(rows)
    if qtype == "apac_subscriptions":
        return InsightEngine.for_apac_subscriptions(rows)
    if qtype == "ntu_nus_compare":
        return InsightEngine.for_ntu_nus_compare(rows)
    if qtype == "top_authors":
        return InsightEngine.for_top_authors(rows)
    if qtype == "revenue_analysis":
        return InsightEngine.for_revenue(rows)
    return InsightEngine.generic(rows)

def build_viz_config(plan: Dict[str, Any], rows: List[Dict]) -> Dict[str, Any]:
    label_field = plan["viz"].get("label_field")
    value_field = plan["viz"].get("value_field")
    value_label = plan["viz"].get("value_label")
    top = rows[:10] if rows else []

    if top and (not label_field or label_field not in top[0] or not value_field or value_field not in top[0]):
        label_field, value_field, value_label = None, None, None

    return {
        "type": "bar",
        "label_field": label_field,
        "value_field": value_field,
        "value_label": value_label,
        "data": top
    }

# ---------- ROUTES ----------
def _print_routes_now():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {sorted(rule.methods)}  {rule.rule}")

@app.route("/")
def home():
    return "<h2>WS — AI Sales Assistant (DB-first, filters enabled)</h2>"

@app.route("/api/health")
@app.route("/health")
def health():
    db = AIDatabase()
    ok = db.connect()
    return jsonify({
        "status": "healthy" if ok else "degraded",
        "database": "✅ connected" if ok else "❌ disconnected",
        "config_echo": {
            "host": DB_CONFIG.get("host"),
            "port": DB_CONFIG.get("port", 3306),
            "user": DB_CONFIG.get("user"),
            "database": DB_CONFIG.get("database"),
            "has_password": bool(DB_CONFIG.get("password")),
        },
        "timestamp": datetime.now().isoformat()
    })

# ---------- MINI ANALYZER + HELPERS (required by run_query) ----------
REGION_ALIASES = {
    "APAC": {"APAC", "ASIA PACIFIC", "ASIA-PACIFIC", "ASIA"},
    "EMEA": {"EMEA", "EUROPE", "MIDDLE EAST", "AFRICA"},
    "AMER": {"AMER", "AMERICA", "AMERICAS", "NORTH AMERICA", "SOUTH AMERICA", "LATAM"},
}
COUNTRY_TO_REGION = {
    "SINGAPORE": "APAC", "MALAYSIA": "APAC", "INDIA": "APAC", "CHINA": "APAC", "JAPAN": "APAC",
    "AUSTRALIA": "APAC", "NEW ZEALAND": "APAC",
    "UNITED KINGDOM": "EMEA", "FRANCE": "EMEA", "GERMANY": "EMEA", "UAE": "EMEA", "SOUTH AFRICA": "EMEA",
    "UNITED STATES": "AMER", "USA": "AMER", "CANADA": "AMER", "BRAZIL": "AMER", "MEXICO": "AMER",
}

import re
YEAR_RE = re.compile(r"(?:(since|from)\s+)?(20\d{2})(?:\s*[-–—]\s*(20\d{2}))?", re.IGNORECASE)
REGION_RE = re.compile(r"\b(APAC|ASIA PACIFIC|ASIA-PACIFIC|ASIA|EMEA|EUROPE|MIDDLE EAST|AFRICA|AMER|AMERICAS|NORTH AMERICA|SOUTH AMERICA|LATAM)\b", re.IGNORECASE)

def detect_filters(user_query: str) -> Dict[str, Any]:
    q_upper = user_query.upper()
    years = None
    m = YEAR_RE.search(q_upper)
    if m:
        since_kw, y1, y2 = m.groups()
        y1, y2 = int(y1), int(y2) if y2 else None
        if since_kw or (y2 and y2 >= y1):
            years = {"mode": "range", "from": y1, "to": y2 or 9999}
        else:
            years = {"mode": "eq", "year": y1}
    region = None
    rm = REGION_RE.search(q_upper)
    if rm:
        token = rm.group(1).upper().replace("-", " ")
        for key, aliases in REGION_ALIASES.items():
            if token in aliases:
                region = {"type": "macro", "value": key}
                break
    countries: List[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z ]{1,30}", user_query):
        T = token.strip().upper()
        if T in COUNTRY_TO_REGION and T not in countries:
            countries.append(T)
    if countries and not region:
        region = {"type": "macro", "value": COUNTRY_TO_REGION[countries[0]]}
    return {"years": years, "region": region, "countries": countries}

class Analyzer:
    def __init__(self, db: AIDatabase):
        self.db = db
    def analyze(self, user_query: str) -> Dict[str, Any]:
        filters = detect_filters(user_query)
        q = user_query.lower()
        best, score = None, 0
        for name, pat in self.db.ai_query_patterns.items():
            s = sum(1 for kw in pat["keywords"] if kw in q)
            if s > score and s >= 2:
                best, score = name, s
        if best:
            pat = self.db.ai_query_patterns[best]
            return {
                "query_type": best,
                "sql_query": pat["sql"],
                "ai_context": pat["insight"],
                "viz": pat["viz"],
                "method": "pattern_match",
                "filters": filters,
            }
        return {
            "query_type": "general",
            "sql_query": "SELECT 'No matching query pattern' AS message",
            "ai_context": "General analysis",
            "viz": {"label_field": None, "value_field": None, "value_label": None},
            "method": "fallback",
            "filters": filters,
        }

def apply_filters(sql_base: str, plan: Dict[str, Any]) -> Tuple[str, List[Any]]:
    filters = plan.get("filters", {})
    years = filters.get("years"); region = filters.get("region"); countries = filters.get("countries", [])
    params: List[Any] = []; sql = sql_base; qtype = plan.get("query_type")

    def year_clause(col: str):
        if not years: return "", []
        if years["mode"] == "eq":  return f" AND {col} = %s ", [years["year"]]
        else:                      return f" AND {col} BETWEEN %s AND %s ", [years["from"], years["to"]]

    def region_clause(col_region: str = None, col_country: str = None):
        if not region and not countries: return "", []
        if region and region.get("type") == "macro":
            macro = region["value"]
            if col_region:
                return f" AND UPPER({col_region}) = %s ", [macro]
            if col_country:
                mapped = [c for c, m in COUNTRY_TO_REGION.items() if m == macro]
                if mapped:
                    ph = ",".join(["%s"] * len(mapped))
                    return f" AND UPPER({col_country}) IN ({ph}) ", mapped
        if countries and col_country:
            ph = ",".join(["%s"] * len(countries))
            return f" AND UPPER({col_country}) IN ({ph}) ", countries
        return "", []

    if qtype == "china_universities":
        yc, yp = year_clause("year")
        rc, rp = region_clause(None, "country")
        sql = sql.replace("GROUP BY affiliation, country", f"{yc}{rc} GROUP BY affiliation, country")
        params += yp + rp
    elif qtype == "apac_subscriptions":
        yc1, yp1 = year_clause("year")
        yc2, yp2 = year_clause("content_year")
        rc_unis, rp_unis = region_clause(None, "country")
        rc_subs, rp_subs = region_clause("region", "country")
        sql = sql.replace("GROUP BY affiliation, country", f"{yc1}{rc_unis} GROUP BY affiliation, country")
        sql = sql.replace("WHERE content_year >= 2022", f"WHERE content_year >= 2022{yc2}{rc_subs}")
        params += yp1 + rp_unis + yp2 + rp_subs
    elif qtype == "ntu_nus_compare":
        yc, yp = year_clause("year")
        sql = sql.replace("GROUP BY university", f"{yc} GROUP BY university")
        params += yp
    elif qtype == "top_authors":
        yc, yp = year_clause("year")
        rc, rp = region_clause(None, "country")
        sql = sql.replace(
            "GROUP BY firstname, lastname, email, affiliation, country",
            f"{yc}{rc} GROUP BY firstname, lastname, email, affiliation, country"
        )
        params += yp + rp
    elif qtype == "revenue_analysis":
        yc, yp = year_clause("calendar_year")
        rc, rp = region_clause("bill_to_region", "bill_to_country")
        sql = sql.replace("AND calendar_year >= 2022", f"AND calendar_year >= 2022{yc}{rc}")
        params += yp + rp

    return sql, params

class InsightEngine:
    @staticmethod
    def for_china_universities(data: List[Dict]) -> List[str]:
        if not data: return ["No data found for China universities."]
        top = data[:5]
        insights = [f"📊 Identified {len(data)} Chinese universities with ≥3 unique authors."]
        if top:
            insights.append(f"🏆 Top university by authors: {top[0].get('university_name')} ({top[0].get('author_count')} authors)")
        high = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('high'))
        med  = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('medium'))
        low  = sum(1 for r in data if str(r.get('priority_level','')).lower().startswith('low'))
        insights.append(f"🎯 Priority mix → High: {high}, Medium: {med}, Low: {low}.")
        with_contacts = sum(1 for r in data if r.get('contact_emails'))
        insights.append(f"✉️ Contact emails available for {with_contacts} universities.")
        insights.append("💡 Action: Visit High Priority universities first; prepare co-publishing pitches and invite top authors for campus events.")
        return insights

    @staticmethod
    def for_apac_subscriptions(data: List[Dict]) -> List[str]:
        if not data: return ["No APAC university data available."]
        subscribed = sum(1 for r in data if str(r.get("subscription_status","")).startswith("Country Subscribed"))
        not_sub = len(data) - subscribed
        top_country = max(data, key=lambda r: float(r.get("country_subscription_revenue_sgd", 0))) if data else {}
        return [
            f"🌏 {len(data)} APAC universities analyzed across multiple countries.",
            f"💼 Country subscription signal → Subscribed: {subscribed}, Not Subscribed: {not_sub}.",
            f"💰 Highest subscription revenue (country): {top_country.get('country','N/A')} ({int(float(top_country.get('country_subscription_revenue_sgd',0))):,} SGD).",
            "🎯 Action: Focus on unis in subscribed countries with high author/publication counts; pilot bundles elsewhere."
        ]

    @staticmethod
    def for_ntu_nus_compare(data: List[Dict]) -> List[str]:
        if not data: return ["No NTU/NUS data available."]
        lookup = {r["university"]: r for r in data}
        ntu, nus = lookup.get("NTU"), lookup.get("NUS")
        if not (ntu and nus):
            return ["ℹ️ Could not find both NTU and NUS; check affiliation patterns."]
        focus = 'NTU' if ntu['publication_count'] >= nus['publication_count'] else 'NUS'
        return [
            f"🏁 NTU vs NUS — Publications: NTU {ntu['publication_count']} vs NUS {nus['publication_count']}.",
            f"👥 Unique authors: NTU {ntu['author_count']} vs NUS {nus['author_count']}.",
            f"⏳ Active span: NTU {ntu.get('first_publication_year')}–{ntu.get('latest_publication_year')} vs NUS {nus.get('first_publication_year')}–{nus.get('latest_publication_year')}.",
            f"🎯 Action: Prioritize {focus} for keynotes; run cross-campus campaigns at the other."
        ]

    @staticmethod
    def for_top_authors(data: List[Dict]) -> List[str]:
        if not data: return ["No top authors found."]
        top = data[:5]
        bullets = [f"• {r['author_name']} — {r['publication_count']} pubs ({r.get('publications_per_year','-')}/yr)" for r in top]
        return [f"🏆 Top {len(top)} prolific authors identified (≥2 publications)."] + bullets + [
            "🎯 Action: Invite top authors for editorial boards and special issues; target co-authorships."
        ]

    @staticmethod
    def for_revenue(data: List[Dict]) -> List[str]:
        if not data: return ["No revenue rows available."]
        top_market = max(data, key=lambda r: float(r.get("total_net_revenue",0)))
        return [
            f"📈 Revenue across {len(set(r['country'] for r in data))} countries.",
            f"🗓️ Years covered: {', '.join(sorted({str(int(r['year'])) for r in data}))}",
            f"💰 Top market (net): {top_market['country']} — {int(float(top_market['total_net_revenue'])):,}",
            "🎯 Action: Double down on top markets; test pricing uplift and bundles; seed emerging markets with campus-wide trials."
        ]

    @staticmethod
    def generic(data: List[Dict]) -> List[str]:
        if not data: return ["No data found."]
        return [f"📊 Returned {len(data)} records.", "💡 Tip: Filter by country/affiliation keywords to surface specific opportunities."]

def rule_based_insights(qtype: str, rows: List[Dict]) -> List[str]:
    if qtype == "china_universities":   return InsightEngine.for_china_universities(rows)
    if qtype == "apac_subscriptions":   return InsightEngine.for_apac_subscriptions(rows)
    if qtype == "ntu_nus_compare":      return InsightEngine.for_ntu_nus_compare(rows)
    if qtype == "top_authors":          return InsightEngine.for_top_authors(rows)
    if qtype == "revenue_analysis":     return InsightEngine.for_revenue(rows)
    return InsightEngine.generic(rows)

def build_viz_config(plan: Dict[str, Any], rows: List[Dict]) -> Dict[str, Any]:
    label_field = plan["viz"].get("label_field")
    value_field = plan["viz"].get("value_field")
    value_label = plan["viz"].get("value_label")
    top = rows[:10] if rows else []
    if top and (not label_field or label_field not in top[0] or not value_field or value_field not in top[0]):
        label_field, value_field, value_label = None, None, None
    return {
        "type": "bar",
        "label_field": label_field,
        "value_field": value_field,
        "value_label": value_label,
        "data": top
    }

@app.route("/api/query", methods=["POST"])
def run_query():
    try:
        payload = request.get_json(silent=True) or {}
        user_query = (payload.get("query") or "").strip()
        if not user_query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        db = AIDatabase()
        plan = Analyzer(db).analyze(user_query)
        sql, params = apply_filters(plan["sql_query"], plan)
        rows = db.execute_query_params(sql, params)

        insights = rule_based_insights(plan["query_type"], rows)
        viz_cfg = build_viz_config(plan, rows)

        return jsonify({
            "success": True,
            "query": user_query,
            "results": {
                "summary": f"✅ Found {len(rows)} records",
                "data": rows,
                "insights": insights,
                "query_type": plan["query_type"],
                "ai_context": plan["ai_context"],
                "visualization": viz_cfg
            },
            "detected_filters": plan.get("filters", {}),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        # Never return None: always return a JSON error payload
        print(f"❌ /api/query error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
from openai import OpenAI
import json

# Create client once (using Bitdeer/OpenAI API key)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.bitdeer.ai/v1"),
)

@app.route("/api/ai-insight", methods=["POST"])
def ai_insight():
    try:
        payload = request.get_json(silent=True) or {}
        user_query = (payload.get("query") or "").strip()
        sample_data = payload.get("data", [])

        if not user_query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        # LLM prompt
        prompt = f"""
        You are a sales assistant. The user asked:
        "{user_query}"

        Data:
        {json.dumps(sample_data[:5], indent=2)}

        Give 3–4 concise, actionable business insights.
        """

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful sales insights assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=300
        )

        text = response.choices[0].message.content
        insights = [line.strip("•- ") for line in text.split("\n") if line.strip()]

        return jsonify({
            "success": True,
            "query": user_query,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print("⚠️ AI error:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------- MAIN ----------
if __name__ == "__main__":
    print("Starting WS AI Sales Assistant (DB-first, filters enabled)…")
    _print_routes_now()
    app.run(host="0.0.0.0", port=5000, debug=True)
