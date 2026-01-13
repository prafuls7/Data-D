import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime
import io
import base64
import zipfile
from io import BytesIO
import warnings
import random
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Dict
import uuid

warnings.filterwarnings('ignore')

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="BADDIE - ETL | Bond Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with BADDIE branding - DARK THEME
st.markdown("""
<style>
    /* DARK THEME */
    .stApp {
        background-color: #0f172a;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* BADDIE Branding Header */
    .baddie-header {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.4);
        border: 1px solid #3b82f6;
    }
    
    .baddie-title {
        font-size: 3.2rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(90deg, #60a5fa, #93c5fd, #bfdbfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .baddie-subtitle {
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 300;
        margin-bottom: 10px;
        color: #dbeafe;
    }
    
    .funny-fullform {
        background: rgba(255, 255, 255, 0.1);
        padding: 12px 24px;
        border-radius: 25px;
        display: inline-block;
        font-weight: 600;
        margin-top: 10px;
        color: #93c5fd;
        border: 1px solid rgba(147, 197, 253, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* DARK CARDS */
    .feature-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        border-left: 4px solid #3b82f6;
        border: 1px solid #334155;
    }
    
    .info-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #334155;
        border-left: 4px solid #10b981;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
    }
    
    /* Success box */
    .success-box {
        padding: 20px;
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 10px 0;
        border: 1px solid #065f46;
        color: #d1fae5;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
    }
    
    p, li, span, div {
        color: #cbd5e1 !important;
    }
    
    .stMarkdown {
        color: #cbd5e1 !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background-color: #1e293b;
        border: 2px dashed #475569;
        border-radius: 10px;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
    }
    
    /* Logo */
    .logo-circle {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 24px;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        background-color: #1e293b;
        border-radius: 8px;
        margin: 2px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        color: #f1f5f9 !important;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: #e2e8f0 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    
    /* Download links */
    .download-btn {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
        margin: 5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        color: white;
        text-decoration: none;
    }
    
    .download-btn-blue {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .download-btn-blue:hover {
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Warning/Info boxes */
    .stAlert {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
    }
    
    /* Sample table */
    .sample-table {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #334155;
    }
    
    /* Steps */
    .steps-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        margin: 1rem 0;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        border-left: 3px solid #3b82f6;
    }
    
    .step-number {
        background: #3b82f6;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    /* Features Grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-item {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
        border-color: #3b82f6;
    }
    
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
        color: #60a5fa;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #93c5fd;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# BADDIE Header
st.markdown("""
<div class="baddie-header">
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;">
        <div class="logo-circle">B</div>
        <div>
            <h1 class="baddie-title">BADDIE - ETL</h1>
            <p class="baddie-subtitle">Bond Analytics & Data DEbt Intelligence Engine</p>
        </div>
    </div>
    <div class="funny-fullform">⚡ Making bond analysis smarter & faster!</div>
</div>
""", unsafe_allow_html=True)

# Funny full form display
st.markdown("""
<div style="text-align: center; margin: 20px 0; padding: 15px; background: rgba(30, 41, 59, 0.8); border-radius: 12px; border: 1px solid #334155; backdrop-filter: blur(10px);">
    <h4 style="color: #93c5fd; margin: 0; font-weight: 600;">🎯 BADDIE = <span style="color: #60a5fa;">B</span>ond <span style="color: #60a5fa;">A</span>nalytics & <span style="color: #60a5fa;">D</span>ata <span style="color: #60a5fa;">D</span>Ebt <span style="color: #60a5fa;">I</span>ntelligence <span style="color: #60a5fa;">E</span>ngine</h4>
</div>
""", unsafe_allow_html=True)

# NSDL Scraping Features Section - UPDATED with proper display
st.markdown("""
<div class="feature-card">
    <h3 style="color: #93c5fd; margin-bottom: 1rem; text-align: center;">🔧 NSDL Scraping Features - UPDATED</h3>
</div>
""", unsafe_allow_html=True)

# Features Grid
st.markdown('<div class="features-grid">', unsafe_allow_html=True)

features = [
    {
        "icon": "🛡️",
        "title": "Enhanced API Headers",
        "desc": "Avoid bot detection with realistic browser headers and rotating user agents"
    },
    {
        "icon": "📈",
        "title": "Complete Step Up/Down Data",
        "desc": "Extract Rate, Condition, Date for both step up and step down features"
    },
    {
        "icon": "📅",
        "title": "Complete Call/Put Options",
        "desc": "Get Dates, Prices, detailed descriptions for both call and put options"
    },
    {
        "icon": "💰",
        "title": "Redemption Type Extraction",
        "desc": "Full/Partial/Bullet classification with redemption premium"
    },
    {
        "icon": "✅",
        "title": "Smart Comparison Logic",
        "desc": "Intelligent date and percentage matching with multiple format support"
    },
    {
        "icon": "🔄",
        "title": "Multiple Redemption Installments",
        "desc": "Support for partial redemptions with dates and amounts"
    },
    {
        "icon": "🏦",
        "title": "Rating Agency Mapping",
        "desc": "Comprehensive coverage of all major rating agencies"
    },
    {
        "icon": "⚡",
        "title": "Batch Processing",
        "desc": "Process multiple ISINs simultaneously with progress tracking"
    }
]

for feature in features:
    st.markdown(f"""
    <div class="feature-item">
        <div class="feature-icon">{feature['icon']}</div>
        <div class="feature-title">{feature['title']}</div>
        <div class="feature-desc">{feature['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

class NSDLBondAnalyzer:
    def __init__(self, progress_bar=None, status_text=None):
        # Create session with retry strategy for better reliability
        self.session = requests.Session()
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rotating User-Agents - More realistic browsers
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
        ]
        
        self.rating_agency_mapping = {
            'CRISIL RATINGS LIMITED': 'CRISIL',
            'CARE RATINGS LIMITED': 'CARE', 
            'ICRA LIMITED': 'ICRA',
            'INDIA RATINGS AND RESEARCH PRIVATE LIMITED': 'IND',
            'INDIA RATING AND RESEARCH PVT. LTD': 'IND',
            'INDIA RATINGS AND RESEARCH PVT. LTD': 'IND',
            'INDIA RATING AND RESEARCH PRIVATE LIMITED': 'IND',
            'ACUITE RATINGS & RESEARCH LIMITED': 'ACUITE',
            'Acuite Ratings And Research Limited': 'ACUITE',
            'ACUITE RATINGS AND RESEARCH LIMITED': 'ACUITE',
            'BRICKWORK RATINGS INDIA PRIVATE LIMITED': 'BWR',
            'BRICKWORK RATINGS INDIA PVT LTD': 'BWR',
            'SMERA RATINGS LIMITED': 'SMERA',
            'INFOMERICS VALUATION AND RATING PRIVATE LIMITED': 'IVR',
            'Infomerics Valuation and Rating Pvt. Ltd': 'IVR',
            'CRISIL LIMITED': 'CRISIL',
            'CREDIT ANALYSIS & RESEARCH LTD': 'CARE'
        }
        self.progress_bar = progress_bar
        self.status_text = status_text
        
        # Column patterns for flexible matching - UPDATED for all required columns
        self.column_patterns = {
            'isin': ['isin', 'ISIN'],
            'issuer_name': ['issuer name', 'ISSUER NAME', 'Issuer Name', 'issuer_name', 'issuer'],
            'seniority': ['seniority', 'SENIORITY', 'Seniority'],
            'secured_or_unsecured': ['secured_or_unsecured', 'SECURED/UNSECURED', 'Secured/Unsecured', 'secured'],
            'coupon_fixed': ['coupon_fixed', 'Coupon_fixed', 'Coupon Fixed', 'coupon fixed', 'Coupon', 'coupon'],
            'issue_price': ['issue price', 'ISSUE PRICE', 'issue_price', 'Issue Price'],
            'face_value': ['face value', 'FACE VALUE', 'face_value', 'Face Value'],
            'total_issue_size_cr': ['total issue size', 'TOTAL ISSUE SIZE', 'total_issue_size', 'Total Issue Size', 'total_issue_size_cr', 'issue size'],
            'listed_or_unlisted': ['listed_or_unlisted', 'LISTED/UNLISTED', 'Listed/Unlisted', 'listed'],
            'listing_exchange': ['listing_exchange', 'LISTING EXCHANGE', 'Listing Exchange', 'exchange'],
            'redemption_date': ['redemption date', 'Redemption date', 'redemption_date', 'redemption_date_1', 'maturity date', 'maturity_date'],
            'payin_date': ['payin date', 'pay-in date', 'payin_date', 'pay_in_date_1', 'allotment date', 'allotment_date']
        }
        
        # Define comprehensive bond data columns
        self.comprehensive_columns = [
            'ISIN', 'ISSUER NAME', 'NAME OF INSTRUMENT', 'DESCRIPTION IN NSDL',
            'SENIORITY', 'SECURED/UNSECURED', 'Coupon details Coupon_fixed',
            'Coupon details coupon_floating', 'Coupon frequency', 'COUPON FREQUENCY_NUMBER',
            'Coupoun reset Rate', 'Coupoun reset Condition', 'Coupoun reset Date',
            'pay-in details pay-in date_1', 'pay-in details pay-in amt_1',
            'pay-in details pay-in date_2', 'pay-in details pay-in amt_2',
            'Redemption details Redemption date_1', 'Redemption details Redemption amt_1',
            'Redemption details Redemption date_2', 'Redemption details Redemption amt_2',
            'Redemption details Redemption type', 'Redemption_Full/ Partial',
            'Redemption details Redemption Premium', 'ISSUE PRICE', 'FACE VALUE',
            'Put option Date', 'Put option Price', 'Call option Date', 'Call option Price',
            'Step up Rate', 'Step up Condition', 'Step up Date', 'Step down Rate',
            'Step down Condition', 'Step down Date', 'Total issue size (Cr.)',
            'BASE ISSUE SIZE (CR.)', 'GREEN-SHOE (CR.)', 'RATED/UNRATED', 'RATING_1',
            'CRISIL', 'RATING_2', 'CARE', 'RATING_3', 'ICRA', 'RATING_4', 'IND',
            'RATING_5', 'ACUITE', 'RATING_6', 'BWR', 'RATING_7', 'SMERA', 'RATING_8',
            'IVR', 'MODE OF PLACEMENT', 'TAXABLE / TAXFREE', 'RECORD DATE',
            'LISTED/UNLISTED', 'LISTING EXCHANGE', 'TYPE OF INSTRUMENT', 'ISSUER INDUSTRY',
            'OWNERSHIP', 'REISSUANCE', 'Guarantee Details GUARANTEE',
            'Guarantee Details GUARANTOR', 'Guarantee Details percent_GUARANTEE',
            'CREDIT ENHANCEMENT', 'SECURITY COVER', 'NATURE OF SECURITY',
            'Description_of_Security', 'REMARKS (from IM)', 'IM present? (Y/N)', 'IM LINK',
            'CASHFLOW (Y/N)', 'REMARKS (Blanks)', 'MAKER (Y/N)', 'MAKER (DATE)',
            'DERIV (Y/N)', 'DERIV (DATE)', 'NSDL_Autocheck (Y/N)',
            'Partial Redemption / Partly Redeem', 'TOTAL ANCHOR AMT.', 'INVESTOR 1',
            'AMT 1', 'INVESTOR 2', 'AMT 2', 'INVESTOR 3', 'AMT 3', 'INVESTOR 4',
            'AMT 4', 'INVESTOR 5', 'AMT 5', 'INVESTOR 6', 'AMT 6', 'INVESTOR 7',
            'AMT 7', 'Financial Covenants _ Min NW', 'Financial Covenants _ CAD Ratio',
            'Financial Covenants _ Min PAT_PBT_EBITDA', 'Financial Covenants _ DE Ratio',
            'Financial Covenants _ GNPA_NNPA_PAR 90',
            'SHAREHOLDING CONVENANTS_SHAREHOLDER NAME',
            'SHAREHOLDING CONVENANTS_AMT%_HOLDING', 'Other Covenants', 'suspended',
            'restructured', 'IS_SAME_PUT_CALL', 'put_description', 'call_description'
        ]
    
    def update_progress(self, message, percent):
        """Update progress bar and status text"""
        if self.progress_bar:
            self.progress_bar.progress(percent)
        if self.status_text:
            self.status_text.text(f"📊 {message} ({percent*100:.0f}%)")
    
    def find_column_name(self, df_columns, patterns):
        """Find column name in dataframe that matches given patterns"""
        for col in df_columns:
            col_lower = str(col).lower().strip()
            for pattern in patterns:
                if pattern.lower() in col_lower:
                    return col
        return None
    
    def fetch_api_data(self, url, max_retries=3):
        """Fetch data from NSDL API with enhanced headers to avoid bot detection"""
        # Generate a unique session ID for each request
        session_id = str(uuid.uuid4())
        
        # More realistic headers to mimic browser behavior
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.indiabondinfo.nsdl.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://www.indiabondinfo.nsdl.com',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'TE': 'Trailers',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'X-Requested-With': 'XMLHttpRequest' if 'api' in url else None
        }
        
        # Remove None values
        headers = {k: v for k, v in headers.items() if v is not None}
        
        for attempt in range(max_retries):
            try:
                # Add random delay between retries
                if attempt > 0:
                    time.sleep(random.uniform(1, 3))
                
                # Add cookies to make it look more like a real browser session
                cookies = {
                    'session_id': session_id,
                    'visited': 'true'
                }
                
                response = self.session.get(url, headers=headers, cookies=cookies, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return data
                    except json.JSONDecodeError as e:
                        # Try to handle different JSON formats
                        text = response.text.strip()
                        
                        # Try to fix common JSON issues
                        if text.startswith('"') and text.endswith('"'):
                            text = text[1:-1]
                            text = text.replace('\\"', '"')
                        
                        # Try different JSON parsing strategies
                        try:
                            return json.loads(text)
                        except:
                            # Try to extract JSON-like structure
                            match = re.search(r'\{.*\}', text, re.DOTALL)
                            if match:
                                try:
                                    return json.loads(match.group())
                                except:
                                    return {}
                            return {}
                
                elif response.status_code == 429:  # Rate limit
                    wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 404:
                    # Bond might not exist in NSDL
                    return {'data': []}
                else:
                    return {}
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(wait_time)
                    continue
                else:
                    return {}
        
        return {}
    
    def get_basic_isin_info(self, isin):
        """Get basic ISIN info including issuer name"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/isins?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_instrument_data(self, isin):
        """Get instrument data from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_listing_data(self, isin):
        """Get listing details from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/listings?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_rating_data(self, isin):
        """Get credit rating data"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/credit-ratings?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_matured_restructured_data(self, isin):
        """Check if ISIN is matured or restructured"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/isins?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_coupon_data(self, isin):
        """Get coupon details from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/coupondetail?isin={isin}"
        return self.fetch_api_data(url)
    
    def get_redemption_data(self, isin):
        """Get redemption details from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/redemptions?isin={isin}"
        return self.fetch_api_data(url)
    
    def extract_listing_info(self, listing_data):
        """Extract listing information from API response"""
        listed_or_unlisted = 'UNLISTED'
        listing_exchange = ''
        
        if listing_data and isinstance(listing_data, dict):
            # Get listing status
            listing_status = listing_data.get('listingStatus', '')
            if listing_status and str(listing_status).strip().upper() == 'LISTED':
                listed_or_unlisted = 'LISTED'
            
            # Get listing exchanges from listingDetails (NOT from earlierListingDetails)
            listing_details = listing_data.get('listingDetails', [])
            if isinstance(listing_details, list) and listing_details:
                exchanges = set()
                for detail in listing_details:
                    exchange_name = detail.get('exchangeName', '')
                    if exchange_name and str(exchange_name).strip():
                        exchanges.add(str(exchange_name).strip().upper())
                
                # Join exchanges with colon separator
                if exchanges:
                    listing_exchange = ' : '.join(sorted(exchanges))
        
        return listed_or_unlisted, listing_exchange
    
    def compare_values(self, val1, val2, data_type='text'):
        """Compare two values and return status - FIXED for dates and percentages"""
        try:
            # Handle missing values
            if pd.isna(val1) or val1 is None or str(val1).strip() == '':
                return 'MISSING', 'File value missing'
            
            if pd.isna(val2) or val2 is None or str(val2).strip() == '':
                return 'MISSING', 'API value missing'
            
            # Convert to string and clean
            val1_str = str(val1).strip()
            val2_str = str(val2).strip()
            
            # Clean values based on type
            if data_type == 'date':
                # Try to parse dates in various formats
                date_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%d-%b-%Y', '%d-%B-%Y']
                val1_date = None
                val2_date = None
                
                # Clean val1 - remove time part if present
                if '00:00:00' in val1_str:
                    val1_str = val1_str.split(' ')[0]
                
                # Try to parse val1
                for fmt in date_formats:
                    try:
                        val1_date = datetime.strptime(val1_str, fmt)
                        break
                    except:
                        continue
                
                # Try to parse val2
                for fmt in date_formats:
                    try:
                        val2_date = datetime.strptime(val2_str, fmt)
                        break
                    except:
                        continue
                
                if val1_date and val2_date:
                    # Compare dates
                    if val1_date == val2_date:
                        return 'MATCH', ''
                    else:
                        # Format both dates for display
                        val1_display = val1_date.strftime('%d-%m-%Y')
                        val2_display = val2_date.strftime('%d-%m-%Y')
                        return 'MISMATCH', f'File: {val1_display}, API: {val2_display}'
                else:
                    # Fall back to string comparison (case-insensitive)
                    if val1_str.lower() == val2_str.lower():
                        return 'MATCH', ''
                    else:
                        return 'MISMATCH', f'File: {val1_str}, API: {val2_str}'
            
            elif data_type == 'number':
                # Handle numbers with percentage signs, commas, etc.
                # Remove percentage signs, commas, and whitespace
                val1_clean = re.sub(r'[%\s,]', '', val1_str)
                val2_clean = re.sub(r'[%\s,]', '', val2_str)
                
                # Try to convert to float
                try:
                    val1_num = float(val1_clean)
                    val2_num = float(val2_clean)
                    
                    # Compare with tolerance for floating point (0.01% tolerance)
                    tolerance = max(abs(val1_num), abs(val2_num)) * 0.0001
                    if abs(val1_num - val2_num) <= tolerance:
                        return 'MATCH', ''
                    else:
                        return 'MISMATCH', f'File: {val1_str}, API: {val2_str}'
                except:
                    # Fall back to string comparison (case-insensitive)
                    if val1_str.lower() == val2_str.lower():
                        return 'MATCH', ''
                    else:
                        return 'MISMATCH', f'File: {val1_str}, API: {val2_str}'
            
            else:  # text comparison
                # Case-insensitive comparison for text
                if val1_str.lower() == val2_str.lower():
                    return 'MATCH', ''
                else:
                    return 'MISMATCH', f'File: {val1_str}, API: {val2_str}'
        except:
            return 'ERROR', 'Comparison error'
    
    def perform_comparison(self, df, delay=0.5):
        """Perform comparison of columns with NSDL data - UPDATED"""
        results = []
        
        # Find all columns in the input file
        col_mapping = {}
        for key in self.column_patterns.keys():
            col_name = self.find_column_name(df.columns.tolist(), self.column_patterns[key])
            col_mapping[key] = col_name
        
        # Check if ISIN column exists
        isin_col = col_mapping.get('isin')
        if not isin_col:
            st.error("❌ ERROR: No ISIN column found in the file!")
            st.info("Please ensure your file has a column named 'ISIN' or 'isin'")
            return None
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            isin = str(row[isin_col]).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_rows
            self.update_progress(f"Processing ISIN {idx+1}/{total_rows}", progress_pct)
            
            # Extract file values
            file_values = {}
            for key, col_name in col_mapping.items():
                if col_name and col_name in row:
                    file_values[key] = row[col_name]
                else:
                    file_values[key] = None
            
            # Initialize API values
            api_values = {
                'isin': isin,
                'issuer_name': '',
                'seniority': '',
                'secured_or_unsecured': '',
                'coupon_fixed': '',
                'issue_price': '',
                'face_value': '',
                'total_issue_size_cr': '',
                'listed_or_unlisted': 'UNLISTED',
                'listing_exchange': '',
                'redemption_date': '',
                'payin_date': ''
            }
            
            try:
                # 1. Get basic ISIN info for issuer name - FROM CORRECT API
                basic_data = self.get_basic_isin_info(isin)
                if basic_data and isinstance(basic_data, dict):
                    if 'data' in basic_data and isinstance(basic_data['data'], list) and len(basic_data['data']) > 0:
                        bond_info = basic_data['data'][0]
                        api_values['issuer_name'] = bond_info.get('issuerName', '')
                        api_values['payin_date'] = bond_info.get('allotmentDate', '')
                        api_values['redemption_date'] = bond_info.get('maturityDate', '')
                
                # 2. Get instrument data for other fields
                instrument_data = self.get_instrument_data(isin)
                
                if instrument_data and isinstance(instrument_data, dict):
                    # Extract from different possible structures
                    if 'instrumentsVo' in instrument_data:
                        instruments_vo = instrument_data['instrumentsVo']
                        if 'instruments' in instruments_vo:
                            instrument = instruments_vo['instruments']
                            
                            if instrument:
                                # Only get issuer name if not already from basic data
                                if not api_values['issuer_name']:
                                    api_values['issuer_name'] = instrument.get('issuerName', '')
                                
                                api_values['seniority'] = instrument.get('seniorityRepayment', '')
                                api_values['secured_or_unsecured'] = instrument.get('secured', '')
                                
                                # Handle issue price
                                issue_price = instrument.get('issuePrice', '')
                                if issue_price:
                                    api_values['issue_price'] = str(issue_price)
                                
                                # Handle face value
                                face_value = instrument.get('faceValue', '')
                                if face_value:
                                    api_values['face_value'] = str(face_value)
                                
                                # Handle total issue size
                                total_issue_size = instrument.get('totalIssueSize', '')
                                if total_issue_size:
                                    api_values['total_issue_size_cr'] = str(total_issue_size)
                                
                                # Only override dates if we didn't get from basic data
                                if not api_values['payin_date']:
                                    api_values['payin_date'] = instrument.get('allotmentDate', '')
                                if not api_values['redemption_date']:
                                    api_values['redemption_date'] = instrument.get('redemptionDate', '')
                
                # 3. Get coupon data for coupon_fixed
                coupon_data = self.get_coupon_data(isin)
                if coupon_data and isinstance(coupon_data, dict):
                    # Try different response structures
                    if 'coupensVo' in coupon_data:
                        coupens_vo = coupon_data['coupensVo']
                        if 'couponDetails' in coupens_vo:
                            coupon_details = coupens_vo['couponDetails']
                            if coupon_details:
                                coupon_rate = coupon_details.get('couponRate', '')
                                # Handle percentage values
                                if coupon_rate and str(coupon_rate).strip():
                                    api_values['coupon_fixed'] = str(coupon_rate).strip()
                                    # Add % sign if not present
                                    if '%' not in api_values['coupon_fixed']:
                                        api_values['coupon_fixed'] += '%'
                
                # 4. Get listing data for listed/unlisted and exchange
                listing_data = self.get_listing_data(isin)
                if listing_data and isinstance(listing_data, dict):
                    # Try different response structures
                    if 'listingDetailVo' in listing_data:
                        listing_detail = listing_data['listingDetailVo']
                        listed_status, exchanges = self.extract_listing_info(listing_detail)
                        api_values['listed_or_unlisted'] = listed_status
                        api_values['listing_exchange'] = exchanges
                    elif 'listingStatus' in listing_data:
                        listed_status, exchanges = self.extract_listing_info(listing_data)
                        api_values['listed_or_unlisted'] = listed_status
                        api_values['listing_exchange'] = exchanges
                
            except Exception as e:
                st.warning(f"Error fetching data for {isin}: {str(e)[:100]}")
            
            # Compare each field with updated data types
            result_row = {'ISIN': isin}
            
            # Define comparison order with proper data types
            comparison_fields = [
                ('issuer_name', 'ISSUER_NAME', 'text'),
                ('seniority', 'SENIORITY', 'text'),
                ('secured_or_unsecured', 'SECURED_UNSECURED', 'text'),
                ('coupon_fixed', 'COUPON_FIXED', 'text'),
                ('issue_price', 'ISSUE_PRICE', 'number'),
                ('face_value', 'FACE_VALUE', 'number'),
                ('total_issue_size_cr', 'TOTAL_ISSUE_SIZE_CR', 'number'),
                ('listed_or_unlisted', 'LISTED_UNLISTED', 'text'),
                ('listing_exchange', 'LISTING_EXCHANGE', 'text'),
                ('redemption_date', 'REDEMPTION_DATE', 'date'),
                ('payin_date', 'PAYIN_DATE', 'date')
            ]
            
            for file_key, output_suffix, data_type in comparison_fields:
                file_val = file_values.get(file_key)
                api_val = api_values.get(file_key)
                
                # Clean file values for specific fields
                if file_key == 'coupon_fixed' and file_val:
                    # Convert to string and clean
                    file_val_str = str(file_val).strip()
                    # Remove trailing zeros and ensure consistent format
                    try:
                        if '%' in file_val_str:
                            # Already has %, just clean
                            file_val = file_val_str
                        else:
                            # Add % if it's a number
                            file_num = float(re.sub(r'[%\s,]', '', file_val_str))
                            file_val = f"{file_num}%"
                    except:
                        file_val = file_val_str
                
                # Clean API values for specific fields
                if file_key == 'coupon_fixed' and api_val:
                    # Ensure API value has % sign
                    api_val_str = str(api_val).strip()
                    if '%' not in api_val_str and api_val_str:
                        try:
                            api_num = float(re.sub(r'[%\s,]', '', api_val_str))
                            api_val = f"{api_num}%"
                        except:
                            api_val = api_val_str
                
                status, notes = self.compare_values(file_val, api_val, data_type)
                
                result_row[f'{output_suffix}_FILE'] = file_val
                result_row[f'{output_suffix}_API'] = api_val
                result_row[f'{output_suffix}_STATUS'] = status
                result_row[f'{output_suffix}_NOTES'] = notes
            
            results.append(result_row)
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        # Create DataFrame with all columns
        if results:
            # Define column order
            column_order = ['ISIN']
            for file_key, output_suffix, _ in comparison_fields:
                column_order.extend([
                    f'{output_suffix}_FILE',
                    f'{output_suffix}_API',
                    f'{output_suffix}_STATUS',
                    f'{output_suffix}_NOTES'
                ])
            
            return pd.DataFrame(results, columns=column_order)
        
        return pd.DataFrame()
    
    # ====================== RATING GENERATION ======================
    
    def clean_rating(self, rating: str) -> str:
        """Clean and format rating string"""
        if not rating or pd.isna(rating):
            return ""
        
        rating_str = str(rating).strip()
        
        # Remove PP-MLD / PPMLD / PP MLD
        rating_str = re.sub(r'^(PP[-\s]?MLD\s*)', '', rating_str, flags=re.IGNORECASE)
        
        # Add space before (CE)
        rating_str = re.sub(r'\s*\(CE\)', ' (CE)', rating_str, flags=re.IGNORECASE)
        
        # Remove double spaces
        rating_str = re.sub(r'\s+', ' ', rating_str)
        
        return rating_str.strip()
    
    def map_agency_name(self, agency_name: str) -> str:
        """Map full agency name to short code"""
        if not agency_name:
            return ""
            
        agency_upper = agency_name.upper()
        
        for full_name, short_code in self.rating_agency_mapping.items():
            if full_name.upper() in agency_upper or agency_upper in full_name.upper():
                return short_code
        
        # Check for partial matches
        if "CRISIL" in agency_upper:
            return "CRISIL"
        elif "CARE" in agency_upper:
            return "CARE"
        elif "ICRA" in agency_upper:
            return "ICRA"
        elif "IND" in agency_upper or "INDIA RATING" in agency_upper:
            return "IND"
        elif "ACUITE" in agency_upper:
            return "ACUITE"
        elif "BWR" in agency_upper or "BRICKWORK" in agency_upper:
            return "BWR"
        elif "SMERA" in agency_upper:
            return "SMERA"
        elif "IVR" in agency_upper or "INFOMERICS" in agency_upper:
            return "IVR"
        
        return ""
    
    def extract_credit_rating_info(self, rating_data: Dict, isin: str) -> Dict:
        """Extract credit rating information from API response"""
        result = {
            'ISIN': isin,
            'Outlook': '',
            'Restructured_isin': '',
            'Date_of_Verification': '',
            'pressReleaseLink': '',
            'Current_RATING_1': '',
            'Current_CRISIL': '',
            'Outlook1': '',
            'Current_RATING_2': '',
            'Current_CARE': '',
            'Outlook2': '',
            'Current_RATING_3': '',
            'Current_ICRA': '',
            'Outlook3': '',
            'Current_RATING_4': '',
            'Current_IND': '',
            'Outlook4': '',
            'Current_RATING_5': '',
            'Current_ACUITE': '',
            'Outlook5': '',
            'Current_RATING_6': '',
            'Current_BWR': '',
            'Outlook6': '',
            'Current_RATING_7': '',
            'Current_SMERA': '',
            'Outlook7': '',
            'Current_RATING_8': '',
            'Current_IVR': '',
            'Outlook8': ''
        }
        
        if not rating_data or 'data' not in rating_data:
            return result
        
        data = rating_data.get('data', {})
        instrument_rate_flag = data.get('instrumentRateFlag', '')
        if instrument_rate_flag == 'Unrated':
            return result
        
        current_ratings = data.get('currentRatings', [])
        if not current_ratings:
            return result
        
        agency_order = ["CRISIL", "CARE", "ICRA", "IND", "ACUITE", "BWR", "SMERA", "IVR"]
        agency_data = {}
        
        for rating in current_ratings:
            agency_name = rating.get('creditRatingAgencyName', '')
            agency_short = self.map_agency_name(agency_name)
            
            if not agency_short or agency_short not in agency_order:
                continue
            
            raw_rating = rating.get('currentRating', '')
            cleaned_rating = self.clean_rating(raw_rating)
            
            outlook = rating.get('outlook', '')
            if outlook in ["-", "", "null", None]:
                outlook = ""
            
            press_link = rating.get('pressReleaseLink', '')
            if press_link in ["None", "null", None, ""]:
                press_link = ""
            
            verification_date = rating.get('dateOfVerification', '')
            if verification_date in ["-", "", "null", None]:
                verification_date = ""
            
            agency_data[agency_short] = {
                'rating': cleaned_rating,
                'outlook': outlook,
                'link': press_link,
                'date': verification_date
            }
        
        for agency in agency_order:
            if agency in agency_data:
                data = agency_data[agency]
                
                if agency == "CRISIL":
                    result['Current_RATING_1'] = data['rating']
                    result['Current_CRISIL'] = "CRISIL"
                    result['Outlook1'] = data['outlook']
                elif agency == "CARE":
                    result['Current_RATING_2'] = data['rating']
                    result['Current_CARE'] = "CARE"
                    result['Outlook2'] = data['outlook']
                elif agency == "ICRA":
                    result['Current_RATING_3'] = data['rating']
                    result['Current_ICRA'] = "ICRA"
                    result['Outlook3'] = data['outlook']
                elif agency == "IND":
                    result['Current_RATING_4'] = data['rating']
                    result['Current_IND'] = "IND"
                    result['Outlook4'] = data['outlook']
                elif agency == "ACUITE":
                    result['Current_RATING_5'] = data['rating']
                    result['Current_ACUITE'] = "ACUITE"
                    result['Outlook5'] = data['outlook']
                elif agency == "BWR":
                    result['Current_RATING_6'] = data['rating']
                    result['Current_BWR'] = "BWR"
                    result['Outlook6'] = data['outlook']
                elif agency == "SMERA":
                    result['Current_RATING_7'] = data['rating']
                    result['Current_SMERA'] = "SMERA"
                    result['Outlook7'] = data['outlook']
                elif agency == "IVR":
                    result['Current_RATING_8'] = data['rating']
                    result['Current_IVR'] = "IVR"
                    result['Outlook8'] = data['outlook']
        
        return result
    
    def generate_ratings(self, df, delay=0.5):
        """Generate rating information for ISINs"""
        results = []
        
        # Find ISIN column
        isin_col = self.find_column_name(df.columns.tolist(), self.column_patterns['isin'])
        if not isin_col:
            st.error("❌ ERROR: No ISIN column found!")
            return None
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            isin = str(row[isin_col]).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_rows
            self.update_progress(f"Getting ratings {idx+1}/{total_rows}", progress_pct)
            
            # Fetch rating data
            rating_data = self.get_rating_data(isin)
            
            # Extract credit rating info
            credit_info = self.extract_credit_rating_info(rating_data, isin)
            results.append(credit_info)
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        # Define column order
        column_order = [
            'ISIN', 'Outlook', 'Restructured_isin', 'Date_of_Verification', 'pressReleaseLink',
            'Current_RATING_1', 'Current_CRISIL', 'Outlook1',
            'Current_RATING_2', 'Current_CARE', 'Outlook2',
            'Current_RATING_3', 'Current_ICRA', 'Outlook3',
            'Current_RATING_4', 'Current_IND', 'Outlook4',
            'Current_RATING_5', 'Current_ACUITE', 'Outlook5',
            'Current_RATING_6', 'Current_BWR', 'Outlook6',
            'Current_RATING_7', 'Current_SMERA', 'Outlook7',
            'Current_RATING_8', 'Current_IVR', 'Outlook8'
        ]
        
        # Create DataFrame with proper column order
        if results:
            result_df = pd.DataFrame(results)
            # Ensure all columns exist
            for col in column_order:
                if col not in result_df.columns:
                    result_df[col] = ''
            
            return result_df[column_order]
        
        return pd.DataFrame(columns=column_order)
    
    # ====================== MATURED/RESTRUCTURED CHECK ======================
    
    def generate_matured_restructured(self, df, delay=0.5):
        """Generate matured/restructured information"""
        results = []
        
        # Find ISIN column
        isin_col = self.find_column_name(df.columns.tolist(), self.column_patterns['isin'])
        if not isin_col:
            st.error("❌ ERROR: No ISIN column found!")
            return None
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            isin = str(row[isin_col]).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_rows
            self.update_progress(f"Checking status {idx+1}/{total_rows}", progress_pct)
            
            # Fetch data
            data = self.get_matured_restructured_data(isin)
            
            status = ''
            new_isin = ''
            
            if data and 'data' in data:
                bond_data = data['data']
                if isinstance(bond_data, list) and len(bond_data) > 0:
                    bond_info = bond_data[0]
                    # Check if restructured
                    if bond_info.get('restructuredStatus') == 'Y':
                        status = 'RESTRUCTURED'
                        new_isin = bond_info.get('newIsin', '')
                    else:
                        status = 'ACTIVE'
                else:
                    status = 'NOT FOUND'
            else:
                status = 'API ERROR'
            
            results.append({
                'ISIN': isin,
                'Matured/Restructured': status,
                'NewISIN': new_isin
            })
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        return pd.DataFrame(results)
    
    # ====================== COMPREHENSIVE DATA EXTRACTION ======================
    
    def extract_comprehensive_data(self, isin):
        """Extract comprehensive bond data from NSDL APIs"""
        bond_data = {col: '' for col in self.comprehensive_columns}
        bond_data['ISIN'] = isin
        bond_data['suspended'] = 'No'
        bond_data['NSDL_Autocheck (Y/N)'] = 'Y'
        
        try:
            # 1. Basic ISIN Info
            url1 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/isins?isin={isin}"
            data1 = self.fetch_api_data(url1)
            
            if data1 and isinstance(data1, dict) and 'data' in data1 and data1['data']:
                if isinstance(data1['data'], list) and len(data1['data']) > 0:
                    basic_data = data1['data'][0]
                    bond_data['ISSUER NAME'] = basic_data.get('issuerName', '')
                    bond_data['NAME OF INSTRUMENT'] = basic_data.get('secType', '')
                    bond_data['ISSUER INDUSTRY'] = basic_data.get('businessSector', '')
                    bond_data['OWNERSHIP'] = basic_data.get('issuerTypeOwner', '')
                    
                    # Check for restructured
                    if basic_data.get('restructuredStatus') == 'Y':
                        bond_data['restructured'] = 'Yes'
            
            # 2. Instrument Details - Main API
            url2 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
            data2 = self.fetch_api_data(url2)
            
            if data2 and isinstance(data2, dict):
                # Extract from different possible structures
                instruments_vo = data2.get('instrumentsVo', {})
                if instruments_vo:
                    instrument = instruments_vo.get('instruments', {})
                    
                    if instrument:
                        bond_data['DESCRIPTION IN NSDL'] = instrument.get('instrumentDesc', '')
                        bond_data['SENIORITY'] = instrument.get('seniorityRepayment', '')
                        bond_data['SECURED/UNSECURED'] = instrument.get('secured', '')
                        
                        issue_price = instrument.get('issuePrice', '')
                        bond_data['ISSUE PRICE'] = str(issue_price) if issue_price else ''
                        
                        face_value = instrument.get('faceValue', '')
                        bond_data['FACE VALUE'] = str(face_value) if face_value else ''
                        
                        bond_data['Total issue size (Cr.)'] = instrument.get('totalIssueSize', '')
                        bond_data['BASE ISSUE SIZE (CR.)'] = instrument.get('baseIssueSize', '')
                        bond_data['GREEN-SHOE (CR.)'] = instrument.get('greenShoeOption', '')
                        bond_data['MODE OF PLACEMENT'] = instrument.get('modeOfIssue', '')
                        bond_data['TAXABLE / TAXFREE'] = instrument.get('taxFree', '')
                        bond_data['TYPE OF INSTRUMENT'] = instrument.get('natureOfInstrument', '')
                        
                        # Dates
                        allotment_date = instrument.get('allotmentDate', '')
                        if allotment_date:
                            try:
                                dt = datetime.strptime(allotment_date, '%d-%m-%Y')
                                bond_data['pay-in details pay-in date_1'] = dt.strftime('%d-%b-%Y')
                            except:
                                bond_data['pay-in details pay-in date_1'] = allotment_date
                        
                        redemption_date = instrument.get('redemptionDate', '')
                        if redemption_date:
                            try:
                                dt = datetime.strptime(redemption_date, '%d-%m-%Y')
                                bond_data['Redemption details Redemption date_1'] = dt.strftime('%d-%b-%Y')
                            except:
                                bond_data['Redemption details Redemption date_1'] = redemption_date
            
            # 3. Listing Details
            url3 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/listings?isin={isin}"
            data3 = self.fetch_api_data(url3)
            
            if data3 and isinstance(data3, dict):
                # Try different response structures
                if 'listingDetailVo' in data3:
                    listing_detail = data3['listingDetailVo']
                    listed_status, exchanges = self.extract_listing_info(listing_detail)
                    bond_data['LISTED/UNLISTED'] = listed_status
                    bond_data['LISTING EXCHANGE'] = exchanges
                elif 'listingStatus' in data3:
                    listed_status, exchanges = self.extract_listing_info(data3)
                    bond_data['LISTED/UNLISTED'] = listed_status
                    bond_data['LISTING EXCHANGE'] = exchanges
            
            # 4. Credit Ratings
            url4 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/credit-ratings?isin={isin}"
            data4 = self.fetch_api_data(url4)
            
            # Get rating data using new function
            credit_info = self.extract_credit_rating_info(data4, isin)
            
            # Map new rating columns to comprehensive format
            bond_data['RATING_1'] = credit_info.get('Current_RATING_1', '')
            bond_data['CRISIL'] = credit_info.get('Current_CRISIL', '')
            bond_data['Outlook1'] = credit_info.get('Outlook1', '')
            bond_data['RATING_2'] = credit_info.get('Current_RATING_2', '')
            bond_data['CARE'] = credit_info.get('Current_CARE', '')
            bond_data['Outlook2'] = credit_info.get('Outlook2', '')
            bond_data['RATING_3'] = credit_info.get('Current_RATING_3', '')
            bond_data['ICRA'] = credit_info.get('Current_ICRA', '')
            bond_data['Outlook3'] = credit_info.get('Outlook3', '')
            bond_data['RATING_4'] = credit_info.get('Current_RATING_4', '')
            bond_data['IND'] = credit_info.get('Current_IND', '')
            bond_data['Outlook4'] = credit_info.get('Outlook4', '')
            bond_data['RATING_5'] = credit_info.get('Current_RATING_5', '')
            bond_data['ACUITE'] = credit_info.get('Current_ACUITE', '')
            bond_data['Outlook5'] = credit_info.get('Outlook5', '')
            bond_data['RATING_6'] = credit_info.get('Current_RATING_6', '')
            bond_data['BWR'] = credit_info.get('Current_BWR', '')
            bond_data['Outlook6'] = credit_info.get('Outlook6', '')
            bond_data['RATING_7'] = credit_info.get('Current_RATING_7', '')
            bond_data['SMERA'] = credit_info.get('Current_SMERA', '')
            bond_data['Outlook7'] = credit_info.get('Outlook7', '')
            bond_data['RATING_8'] = credit_info.get('Current_RATING_8', '')
            bond_data['IVR'] = credit_info.get('Current_IVR', '')
            bond_data['Outlook8'] = credit_info.get('Outlook8', '')
            
            # Set RATED/UNRATED
            if any(bond_data.get(f'RATING_{i}') for i in range(1, 9)):
                bond_data['RATED/UNRATED'] = 'RATED'
            else:
                bond_data['RATED/UNRATED'] = 'UNRATED'
            
        except Exception as e:
            bond_data['ERROR'] = str(e)[:200]
        
        return bond_data
    
    def extract_comprehensive_batch(self, df, delay=0.5):
        """Extract comprehensive data for all ISINs in batch"""
        results = []
        
        # Find ISIN column
        isin_col = self.find_column_name(df.columns.tolist(), self.column_patterns['isin'])
        if not isin_col:
            st.error("❌ ERROR: No ISIN column found!")
            return None
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            isin = str(row[isin_col]).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_rows
            self.update_progress(f"Extracting comprehensive data {idx+1}/{total_rows}", progress_pct)
            
            # Extract comprehensive data
            bond_data = self.extract_comprehensive_data(isin)
            results.append(bond_data)
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        # Create DataFrame with all columns
        if results:
            result_df = pd.DataFrame(results)
            
            # Ensure all columns exist
            for col in self.comprehensive_columns:
                if col not in result_df.columns:
                    result_df[col] = ''
            
            # Reorder columns
            return result_df[self.comprehensive_columns]
        
        return pd.DataFrame(columns=self.comprehensive_columns)

# Helper functions for file downloads
def get_download_link(df, filename, file_label="Excel file"):
    """Generate a download link for DataFrame"""
    towrite = BytesIO()
    
    if filename.endswith('.xlsx'):
        df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        df.to_csv(towrite, index=False)
        towrite.seek(0)
        mime_type = 'text/csv'
    
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a class="download-btn" href="data:{mime_type};base64,{b64}" download="{filename}">📥 {file_label}</a>'
    return href

def create_zip_file(files_dict):
    """Create a zip file from multiple DataFrames"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for sheet_name, df in files_dict.items():
            if df is not None and not df.empty:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                excel_buffer.seek(0)
                zip_file.writestr(f"{sheet_name}.xlsx", excel_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# Main Streamlit app
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        st.markdown("#### Select Operations:")
        do_comprehensive = st.checkbox("📊 Comprehensive Bond Data Extraction", value=True,
                                      help="Extract 80+ bond parameters from NSDL APIs")
        do_comparison = st.checkbox("🔍 Column Comparison", value=True, 
                                    help="Compare file data with NSDL API data")
        do_ratings = st.checkbox("⭐ Rating Generation", value=False,
                                help="Fetch credit ratings for each ISIN")
        do_matured = st.checkbox("📅 Matured/Restructured Check", value=False,
                                help="Check if bonds are matured or restructured")
        
        st.markdown("---")
        
        st.markdown("#### ⚡ Rate Limiting")
        delay = st.slider("Delay between API calls (seconds)", 
                        0.5, 5.0, 1.0, 0.1,
                        help="Increase if getting rate limited (2-3 seconds recommended for cloud)")
        
        st.markdown("---")
        
        st.markdown("#### 📋 Supported File Formats")
        st.info("""
        - **Excel**: .xlsx, .xls
        - **CSV**: .csv
        
        **Required column**: ISIN (or isin)
        
        **Optional columns for comparison**:
        - issuer_name
        - seniority
        - secured_or_unsecured
        - coupon_fixed
        - issue_price
        - face_value
        - total_issue_size_cr
        - listed_or_unlisted
        - listing_exchange
        - redemption_date
        - payin_date
        """)
        
        st.markdown("---")
        
        st.markdown("#### 🔗 NSDL APIs Used")
        st.markdown("""
        1. `/isins` - Basic ISIN info
        2. `/instruments` - Instrument details
        3. `/coupondetail` - Coupon information
        4. `/redemptions` - Redemption details
        5. `/listings` - Listing information
        6. `/credit-ratings` - Rating information
        """)
        
        st.markdown("---")
        
        st.markdown("#### 🚀 Performance Tips")
        st.markdown("""
        - **Small batches**: Process 50-100 ISINs at a time
        - **Cloud deployment**: Use 2-3 second delay
        - **Stable connection**: Ensure reliable internet
        - **Valid ISINs**: Clean your input file first
        - **Monitor progress**: Keep browser open
        """)
    
    # Main content area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload your Excel or CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="File should contain ISIN column"
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded successfully!")
                st.info(f"**Rows:** {len(df):,} | **Columns:** {len(df.columns)}")
                
                # Show preview
                with st.expander("👀 Preview first 5 rows"):
                    st.dataframe(df.head(), use_container_width=True)
                
                # Show column mapping
                with st.expander("🔍 Column Mapping"):
                    analyzer = NSDLBondAnalyzer()
                    column_mapping = {}
                    for key in analyzer.column_patterns.keys():
                        col_name = analyzer.find_column_name(df.columns.tolist(), analyzer.column_patterns[key])
                        column_mapping[key] = col_name or "NOT FOUND"
                    
                    mapping_df = pd.DataFrame(list(column_mapping.items()), columns=['Required Column', 'Found Column'])
                    st.dataframe(mapping_df, use_container_width=True)
                
                # Process button
                if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                    # Create progress elements
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Create analyzer instance
                    analyzer = NSDLBondAnalyzer(progress_bar, status_text)
                    
                    # Dictionary to store results
                    results = {}
                    
                    # Perform selected operations
                    if do_comprehensive:
                        with st.spinner("📊 Extracting comprehensive bond data..."):
                            comprehensive_df = analyzer.extract_comprehensive_batch(df, delay)
                            if comprehensive_df is not None and not comprehensive_df.empty:
                                results['Comprehensive_Bond_Data'] = comprehensive_df
                    
                    if do_comparison:
                        with st.spinner("🔍 Performing column comparison..."):
                            comparison_df = analyzer.perform_comparison(df, delay)
                            if comparison_df is not None and not comparison_df.empty:
                                results['Comparison_Report'] = comparison_df
                    
                    if do_ratings:
                        with st.spinner("⭐ Fetching credit ratings..."):
                            ratings_df = analyzer.generate_ratings(df, delay)
                            if ratings_df is not None and not ratings_df.empty:
                                results['Credit_Ratings'] = ratings_df
                    
                    if do_matured:
                        with st.spinner("📅 Checking matured/restructured status..."):
                            matured_df = analyzer.generate_matured_restructured(df, delay)
                            if matured_df is not None and not matured_df.empty:
                                results['Matured_Restructured'] = matured_df
                    
                    # Complete progress
                    progress_bar.progress(1.0)
                    status_text.text("✅ Processing complete!")
                    
                    # Display results
                    if results:
                        st.markdown("---")
                        st.markdown("## 📋 Results")
                        
                        # Display statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total ISINs Processed", len(df))
                        with col2:
                            st.metric("Operations Completed", len(results))
                        with col3:
                            st.metric("Estimated Time", f"~{len(df)*delay*len(results)/60:.1f} min")
                        
                        # Create tabs for each result
                        if len(results) > 1:
                            tabs = st.tabs(list(results.keys()))
                            for tab, (sheet_name, result_df) in zip(tabs, results.items()):
                                with tab:
                                    st.dataframe(result_df, use_container_width=True, height=300)
                                    st.markdown(f"**Rows:** {len(result_df)}")
                        else:
                            for sheet_name, result_df in results.items():
                                st.dataframe(result_df, use_container_width=True, height=400)
                        
                        # Download section
                        st.markdown("---")
                        st.markdown("## 💾 Download Results")
                        
                        # Individual downloads
                        st.markdown("### Individual Files:")
                        cols = st.columns(min(3, len(results)))
                        
                        for idx, (sheet_name, result_df) in enumerate(results.items()):
                            with cols[idx % 3]:
                                st.markdown(f"**{sheet_name}**")
                                st.markdown(get_download_link(
                                    result_df,
                                    f"BADDIE_{sheet_name}.xlsx",
                                    f"Download {sheet_name}"
                                ), unsafe_allow_html=True)
                        
                        # Combined ZIP download
                        if len(results) > 1:
                            st.markdown("### Combined Download:")
                            zip_buffer = create_zip_file(results)
                            b64 = base64.b64encode(zip_buffer.getvalue()).decode()
                            href = f'<a class="download-btn download-btn-blue" href="data:application/zip;base64,{b64}" download="BADDIE_Results.zip">📦 Download All Results (ZIP)</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        
                        # Success message
                        st.balloons()
                        st.markdown('<div class="success-box">🎉 All operations completed successfully! Your files are ready for download.</div>', unsafe_allow_html=True)
                    
                    else:
                        st.warning("⚠️ No results generated. Please check if your file contains valid ISINs.")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("Please check: 1) File format, 2) File is not corrupted, 3) Contains ISIN column")
    
    with col2:
        # Sample data and instructions
        st.markdown("### 📝 Sample Input Format for Comparison")
        
        sample_data = pd.DataFrame({
            'ISIN': ['INE225R08014', 'INE002Z08044', 'INE003L07184'],
            'issuer_name': ['HDFC ERGO GENERAL INSURANCE COMPANY LIMITED', 'Example Issuer 2', 'Example Issuer 3'],
            'seniority': ['Secured', 'Unsecured', 'Secured'],
            'secured_or_unsecured': ['Secured', 'Unsecured', 'Secured'],
            'coupon_fixed': ['7.72', 'N.A', '7.5'],
            'issue_price': [100, 100, 100],
            'face_value': [100, 100, 100],
            'total_issue_size_cr': [1000, 500, 750],
            'listed_or_unlisted': ['LISTED', 'UNLISTED', 'LISTED'],
            'listing_exchange': ['BSE', '', 'NSE : BSE'],
            'redemption_date': ['2023-11-07 00:00:00', '20-05-2028', '30-09-2035'],
            'payin_date': ['2022-01-01', '15-03-2021', '30-06-2023']
        })
        
        st.markdown('<div class="sample-table">', unsafe_allow_html=True)
        st.dataframe(sample_data, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🔄 How It Works")
        
        st.markdown('<div class="steps-container">', unsafe_allow_html=True)
        steps = [
            "**Upload** your Excel/CSV file with ISINs",
            "**Select** operations to perform",
            "**Click** Start Processing button",
            "**Wait** for progress to complete",
            "**View** results in interactive tables",
            "**Download** files as Excel or ZIP"
        ]
        
        for idx, step in enumerate(steps, 1):
            st.markdown(f'<div class="step-item"><div class="step-number">{idx}</div><div>{step}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Smart Comparison Features")
        st.markdown("""
        <div class="info-box">
            <strong>✅ Intelligent Data Matching:</strong><br>
            • **Dates**: Multiple format support (YYYY-MM-DD, DD-MM-YYYY, etc.)<br>
            • **Percentages**: 7.72 = 7.72% → MATCH<br>
            • **Numbers**: Floating point tolerance<br>
            • **Text**: Case-insensitive comparison<br><br>
            
            <strong>📊 Comparison Columns:</strong><br>
            • **issuer_name** - Issuer name comparison<br>
            • **seniority** - Seniority status<br>
            • **secured_or_unsecured** - Security type<br>
            • **coupon_fixed** - Fixed coupon rate<br>
            • **issue_price** - Issue price<br>
            • **face_value** - Face value<br>
            • **total_issue_size_cr** - Total issue size<br>
            • **listed_or_unlisted** - Listing status<br>
            • **listing_exchange** - Exchange(s) listed on<br>
            • **redemption_date** - Redemption date<br>
            • **payin_date** - Pay-in date
        </div>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
