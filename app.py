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
from typing import Dict  # Add this import

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
        
        # Rotating User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
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
        
        # Column patterns for flexible matching
        self.column_patterns = {
            'isin': ['isin', 'ISIN'],
            'seniority': ['seniority', 'SENIORITY', 'Seniority'],
            'coupon_fixed': ['coupon_fixed', 'Coupon_fixed', 'Coupon Fixed', 'coupon fixed', 'Coupon'],
            'secured_or_unsecured' : ['secured_or_unsecured'],
            'pay_in_date_1': ['pay-in date_1', 'pay in date_1', 'payin date_1', 'pay_in_date_1', 'payin date'],
            'redemption_date_1': ['redemption date_1', 'Redemption date_1', 'redemption_date_1', 'redemption date'],
            'issue_price': ['issue price', 'ISSUE PRICE', 'issue_price', 'Issue Price'],
            'face_value': ['face value', 'FACE VALUE', 'face_value', 'Face Value'],
            'total_issue_size': ['total issue size', 'TOTAL ISSUE SIZE', 'total_issue_size', 'Total Issue Size']
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
        """Fetch data from NSDL API with enhanced error handling"""
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
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        # Try to fix common JSON issues
                        text = response.text.strip()
                        if text.startswith('"') and text.endswith('"'):
                            text = text[1:-1]
                        return json.loads(text)
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    st.warning(f"API returned status {response.status_code} for {url}")
                    return {}
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    st.warning(f"Error fetching {url}: {str(e)}")
                    return {}
        
        return {}
    
    def get_instrument_data(self, isin):
        """Get instrument data from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
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
    
    def get_listing_data(self, isin):
        """Get listing details from NSDL"""
        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/listings?isin={isin}"
        return self.fetch_api_data(url)
    
    # ====================== CURRENT RATING FUNCTIONS ======================
    
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
        
        if not rating_data:
            return result
        
        instrument_rate_flag = rating_data.get('instrumentRateFlag', '')
        if instrument_rate_flag == 'Unrated':
            return result
        
        current_ratings = rating_data.get('currentRatings', [])
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
        
        ordered_outlooks = []
        ordered_links = []
        ordered_dates = []
        
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
                
                if data['outlook']:
                    ordered_outlooks.append(data['outlook'])
                if data['link']:
                    ordered_links.append(data['link'])
                if data['date']:
                    ordered_dates.append(data['date'])
        
        valid_outlooks = [str(o).strip() for o in ordered_outlooks if str(o).strip()]
        valid_links = [str(l).strip() for l in ordered_links if str(l).strip()]
        valid_dates = [str(d).strip() for d in ordered_dates if str(d).strip()]
        
        result['Outlook'] = ', '.join(valid_outlooks)
        result['pressReleaseLink'] = ', '.join(valid_links)
        
        if valid_dates:
            try:
                date_objs = []
                for date_str in valid_dates:
                    try:
                        date_objs.append(datetime.strptime(date_str, '%d-%m-%Y'))
                    except:
                        try:
                            date_objs.append(datetime.strptime(date_str, '%Y-%m-%d'))
                        except:
                            continue
                
                if date_objs:
                    latest_date = max(date_objs)
                    result['Date_of_Verification'] = latest_date.strftime('%d-%m-%Y')
                else:
                    result['Date_of_Verification'] = valid_dates[0]
            except:
                result['Date_of_Verification'] = valid_dates[0]
        
        return result
    
    # ====================== RECORD DATE FUNCTIONS ======================
    
    def calculate_date_diff(self, record_date, due_date):
        """Calculate difference between due date and record date in days"""
        try:
            record_dt = datetime.strptime(record_date, '%d-%m-%Y')
            due_dt = datetime.strptime(due_date, '%d-%m-%Y')
            diff = (due_dt - record_dt).days
            return diff
        except Exception as e:
            return None
    
    def extract_interest_payments(self, data):
        """Extract interest payment rows from cashFlowSchedule"""
        interest_payments = []
        
        try:
            cashflow_data = data.get('coupensVo', {}).get('cashFlowScheduleDetails', {}).get('cashFlowSchedule', [])
            
            for item in cashflow_data:
                if item.get('cashFlowsEvent') == 'Interest':
                    record_date = item.get('recordDate', '')
                    due_date = item.get('dueDate', '')
                    
                    if record_date and due_date and record_date != '-' and due_date != '-':
                        interest_payments.append({
                            'record_date': record_date,
                            'due_date': due_date,
                            'full_data': item
                        })
            
            return interest_payments
            
        except Exception as e:
            return []
    
    def select_interest_rows(self, interest_payments):
        """Select interest rows based on the logic"""
        selected_rows = []
        total_rows = len(interest_payments)
        
        if total_rows == 0:
            return selected_rows
        
        if total_rows <= 5:
            for i in range(total_rows):
                selected_rows.append({
                    'position': i + 1,
                    'data': interest_payments[i]
                })
        else:
            positions = [
                (1, interest_payments[0]),
                (2, interest_payments[1]),
                (3, interest_payments[-3]),
                (4, interest_payments[-2]),
                (5, interest_payments[-1])
            ]
            
            for pos, data in positions:
                selected_rows.append({
                    'position': pos,
                    'data': data
                })
        
        return selected_rows
    
    # ====================== MAIN PROCESSING FUNCTIONS ======================
    
    def extract_comprehensive_data(self, isin):
        """Extract comprehensive bond data from NSDL APIs"""
        bond_data = {col: '' for col in self.comprehensive_columns}
        bond_data['ISIN'] = isin
        bond_data['suspended'] = 'No'
        bond_data['NSDL_Autocheck (Y/N)'] = 'Y'
        
        try:
            # API 1: Basic ISIN info
            url1 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/isins?isin={isin}"
            data1 = self.fetch_api_data(url1)
            
            if data1 and 'data' in data1 and len(data1['data']) > 0:
                bond_data['ISSUER NAME'] = data1['data'][0].get('issuerName', '')
                bond_data['NAME OF INSTRUMENT'] = data1['data'][0].get('secType', '')
            
            # API 2: Instrument details
            url2 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
            data2 = self.fetch_api_data(url2)
            
            if data2 and 'data' in data2 and len(data2['data']) > 0:
                inst = data2['data'][0]
                
                bond_data['DESCRIPTION IN NSDL'] = inst.get('instrumentDesc', '')
                bond_data['SENIORITY'] = inst.get('seniorityRepayment', '')
                bond_data['SECURED/UNSECURED'] = inst.get('secured', '')
                bond_data['ISSUE PRICE'] = inst.get('issuePrice', '')
                bond_data['FACE VALUE'] = inst.get('faceValue', '')
                bond_data['Total issue size (Cr.)'] = inst.get('totalIssueSize', '')
                bond_data['GREEN-SHOE (CR.)'] = inst.get('greenShoeOption', '')
                
                # Format dates to DD-MMM-YYYY
                allotment_date = inst.get('allotmentDate', '')
                if allotment_date:
                    try:
                        dt = datetime.strptime(allotment_date, '%d-%m-%Y')
                        bond_data['pay-in details pay-in date_1'] = dt.strftime('%d-%b-%Y')
                    except:
                        bond_data['pay-in details pay-in date_1'] = allotment_date
                
                redemption_date = inst.get('redemptionDate', '')
                if redemption_date:
                    try:
                        dt = datetime.strptime(redemption_date, '%d-%m-%Y')
                        bond_data['Redemption details Redemption date_1'] = dt.strftime('%d-%b-%Y')
                    except:
                        bond_data['Redemption details Redemption date_1'] = redemption_date
                
                bond_data['MODE OF PLACEMENT'] = inst.get('modeOfIssue', '')
                bond_data['Guarantee Details GUARANTEE'] = inst.get('guarantee', '')
                
                # Guarantor details
                guarantee_details = inst.get('guaranteeDetails', [])
                if guarantee_details:
                    bond_data['Guarantee Details GUARANTOR'] = guarantee_details[0].get('guaranteedBy', '')
                    bond_data['Guarantee Details percent_GUARANTEE'] = guarantee_details[0].get('guaranteePercent', '')
                
                # Credit enhancement
                credit_enhance = inst.get('creditEnhanceDetails', [])
                if credit_enhance:
                    enh = credit_enhance[0]
                    if enh.get('creditEnhancementDetails') and enh['creditEnhancementDetails'] != '-':
                        bond_data['CREDIT ENHANCEMENT'] = 'Yes'
                
                # Security details
                bond_data['NATURE OF SECURITY'] = inst.get('securedDetails', '')
                bond_data['SECURITY COVER'] = inst.get('assetCvrPercent', '')
                
                # Asset cover details for Description_of_Security
                asset_cover = inst.get('assetCover', {})
                if asset_cover:
                    desc_parts = []
                    if asset_cover.get('securedFlag'):
                        desc_parts.append(f"Secured Flag: {asset_cover['securedFlag']}")
                    if asset_cover.get('assetCvge'):
                        desc_parts.append(f"Asset Coverage: {asset_cover['assetCvge']}")
                    if asset_cover.get('assetCvrPercent'):
                        desc_parts.append(f"Coverage Percent: {asset_cover['assetCvrPercent']}%")
                    
                    asset_list = asset_cover.get('assetList', [])
                    if asset_list:
                        for asset in asset_list:
                            if asset.get('assetType'):
                                desc_parts.append(f"Asset Type: {asset['assetType']}")
                            if asset.get('securityDetails'):
                                desc_parts.append(f"Security Details: {asset['securityDetails']}")
                    
                    bond_data['Description_of_Security'] = ' | '.join(desc_parts)
            
            # API 3: Coupon details
            url3 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/coupondetail?isin={isin}"
            data3 = self.fetch_api_data(url3)
            
            if data3 and 'data' in data3 and len(data3['data']) > 0:
                coupon = data3['data'][0]
                
                bond_data['Coupon details Coupon_fixed'] = coupon.get('couponRate', '')
                
                # Map frequency
                freq = coupon.get('interestPaymentFrequency', '').upper()
                if 'ANNUAL' in freq:
                    bond_data['Coupon frequency'] = 'Annual'
                    bond_data['COUPON FREQUENCY_NUMBER'] = 1
                elif 'SEMI' in freq:
                    bond_data['Coupon frequency'] = 'Semi-Annual'
                    bond_data['COUPON FREQUENCY_NUMBER'] = 2
                elif 'QUARTER' in freq:
                    bond_data['Coupon frequency'] = 'Quarterly'
                    bond_data['COUPON FREQUENCY_NUMBER'] = 4
                elif 'MONTH' in freq:
                    bond_data['Coupon frequency'] = 'Monthly'
                    bond_data['COUPON FREQUENCY_NUMBER'] = 12
                else:
                    bond_data['Coupon frequency'] = 'On Maturity'
                    bond_data['COUPON FREQUENCY_NUMBER'] = 0
                
                # Step up/down conditions
                step_up = coupon.get('stepUp', [])
                if step_up:
                    for step in step_up:
                        bond_data['Step up Condition'] = step.get('otherDetailsStepUp', '')
                        bond_data['Step up Date'] = step.get('resetDateStepUp', '')
                        bond_data['Step up Rate'] = step.get('resetRateStepUp', '')
                
                step_down = coupon.get('stepDown', [])
                if step_down:
                    for step in step_down:
                        bond_data['Step down Condition'] = step.get('otherDetailsStepDown', '')
                        bond_data['Step down Date'] = step.get('resetDateStepDown', '')
                        bond_data['Step down Rate'] = step.get('resetRateStepDown', '')
            
            # API 4: Redemption details
            url4 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/redemptions?isin={isin}"
            data4 = self.fetch_api_data(url4)
            
            if data4 and 'data' in data4 and len(data4['data']) > 0:
                redemption = data4['data'][0]
                
                bond_data['Redemption details Redemption type'] = redemption.get('redemptionType', '')
                bond_data['Redemption_Full/ Partial'] = 'Partial' if 'Partial' in str(redemption.get('redemptionType', '')) else 'Bullet'
                
                # Put option details
                put_option = redemption.get('putOption', {})
                if put_option:
                    bond_data['Put option Date'] = put_option.get('specifiedDates', '')
                    bond_data['Put option Price'] = bond_data.get('FACE VALUE', '')
                    
                    put_desc_parts = []
                    if put_option.get('deadlineDate'):
                        put_desc_parts.append(f"Deadline: {put_option['deadlineDate']}")
                    if put_option.get('notificationTime'):
                        put_desc_parts.append(f"Notification Time: {put_option['notificationTime']}")
                    bond_data['put_description'] = ' | '.join(put_desc_parts)
                
                # Call option details
                call_option = redemption.get('callOption', {})
                if call_option:
                    bond_data['Call option Date'] = call_option.get('specifiedDates', '')
                    bond_data['Call option Price'] = bond_data.get('FACE VALUE', '')
                    
                    call_desc_parts = []
                    if call_option.get('deadlineDate'):
                        call_desc_parts.append(f"Deadline: {call_option['deadlineDate']}")
                    if call_option.get('notificationTime'):
                        call_desc_parts.append(f"Notification Time: {call_option['notificationTime']}")
                    bond_data['call_description'] = ' | '.join(call_desc_parts)
            
            # API 5: Listing details
            url5 = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/listings?isin={isin}"
            data5 = self.fetch_api_data(url5)
            
            if data5 and 'data' in data5 and len(data5['data']) > 0:
                listing = data5['data'][0]
                
                bond_data['LISTED/UNLISTED'] = listing.get('listingStatus', '')
                listing_details = listing.get('listingDetails', [])
                if listing_details:
                    bond_data['LISTING EXCHANGE'] = listing_details[0].get('exchangeName', '')
            
            # Get rating data - using new function
            rating_data = self.get_rating_data(isin)
            credit_info = self.extract_credit_rating_info(rating_data, isin)
            
            # Map new rating columns to comprehensive format
            bond_data['RATING_1'] = credit_info.get('Current_RATING_1', '')
            bond_data['CRISIL'] = credit_info.get('Current_CRISIL', '')
            bond_data['RATING_2'] = credit_info.get('Current_RATING_2', '')
            bond_data['CARE'] = credit_info.get('Current_CARE', '')
            bond_data['RATING_3'] = credit_info.get('Current_RATING_3', '')
            bond_data['ICRA'] = credit_info.get('Current_ICRA', '')
            bond_data['RATING_4'] = credit_info.get('Current_RATING_4', '')
            bond_data['IND'] = credit_info.get('Current_IND', '')
            bond_data['RATING_5'] = credit_info.get('Current_RATING_5', '')
            bond_data['ACUITE'] = credit_info.get('Current_ACUITE', '')
            bond_data['RATING_6'] = credit_info.get('Current_RATING_6', '')
            bond_data['BWR'] = credit_info.get('Current_BWR', '')
            bond_data['RATING_7'] = credit_info.get('Current_RATING_7', '')
            bond_data['SMERA'] = credit_info.get('Current_SMERA', '')
            bond_data['RATING_8'] = credit_info.get('Current_RATING_8', '')
            bond_data['IVR'] = credit_info.get('Current_IVR', '')
            
            # Check matured/restructured
            matured_data = self.get_matured_restructured_data(isin)
            if matured_data:
                if matured_data.get('isin') is None:
                    bond_data['suspended'] = 'Yes'
                elif matured_data.get('restructuredStatus') == 'Y':
                    bond_data['restructured'] = 'Yes'
                    bond_data['suspended'] = 'Yes'
            
            # Set RATED/UNRATED
            if any(bond_data.get(f'RATING_{i}') for i in range(1, 9)):
                bond_data['RATED/UNRATED'] = 'RATED'
            else:
                bond_data['RATED/UNRATED'] = 'UNRATED'
            
        except Exception as e:
            bond_data['ERROR'] = str(e)
        
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
        result_df = pd.DataFrame(results)
        
        # Ensure all columns exist
        for col in self.comprehensive_columns:
            if col not in result_df.columns:
                result_df[col] = ''
        
        return result_df[self.comprehensive_columns]
    
    # Keep all original methods below...
    def compare_values(self, val1, val2, data_type='text'):
        """Compare two values and return status"""
        try:
            # Handle missing values
            if pd.isna(val1) or val1 is None or str(val1).strip() == '':
                return 'MISSING', 'File value missing'
            
            if pd.isna(val2) or val2 is None or str(val2).strip() == '':
                return 'MISSING', 'API value missing'
            
            # Clean values based on type
            if data_type == 'date':
                # Try to parse dates
                try:
                    val1_clean = pd.to_datetime(val1).strftime('%d-%m-%Y')
                    val2_clean = pd.to_datetime(val2).strftime('%d-%m-%Y')
                except:
                    val1_clean = str(val1).strip()
                    val2_clean = str(val2).strip()
            elif data_type in ['number', 'float']:
                try:
                    val1_clean = float(str(val1).replace(',', ''))
                    val2_clean = float(str(val2).replace(',', ''))
                except:
                    val1_clean = str(val1).strip()
                    val2_clean = str(val2).strip()
            else:
                val1_clean = str(val1).strip().lower()
                val2_clean = str(val2).strip().lower()
            
            # Compare
            if val1_clean == val2_clean:
                return 'MATCH', ''
            else:
                return 'MISMATCH', f'File: {val1}, API: {val2}'
        except:
            return 'ERROR', 'Comparison error'
    
    def perform_comparison(self, df, delay=0.5):
        """Perform comparison of columns with NSDL data"""
        results = []
        
        # Find ISIN column
        isin_col = self.find_column_name(df.columns.tolist(), self.column_patterns['isin'])
        if not isin_col:
            st.error("❌ ERROR: No ISIN column found in the file!")
            st.info("Please ensure your file has a column named 'ISIN' or 'isin'")
            return None
        
        # Map other columns
        col_mapping = {}
        for key, patterns in self.column_patterns.items():
            if key != 'isin':
                col_name = self.find_column_name(df.columns.tolist(), patterns)
                col_mapping[key] = col_name
        
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            isin = str(row[isin_col]).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_rows
            self.update_progress(f"Processing ISIN {idx+1}/{total_rows}", progress_pct)
            
            # Fetch data from API
            instrument_data = self.get_instrument_data(isin)
            
            # Extract file values
            file_values = {}
            for key, col_name in col_mapping.items():
                if col_name and col_name in row:
                    file_values[key] = row[col_name]
                else:
                    file_values[key] = None
            
            # Extract API values
            api_values = {}
            if instrument_data and 'instrumentsVo' in instrument_data:
                if 'instruments' in instrument_data['instrumentsVo']:
                    inst = instrument_data['instrumentsVo']['instruments']
                    
                    # Seniority from secured field
                    secured = inst.get('secured')
                    seniority_api = secured if secured else None
                    
                    api_values = {
                        'seniority': seniority_api,
                        'pay_in_date_1': inst.get('allotmentDate'),
                        'redemption_date_1': inst.get('redemptionDate'),
                        'issue_price': inst.get('issuePrice'),
                        'face_value': inst.get('faceValue'),
                        'total_issue_size': inst.get('totalIssueSize'),
                        'coupon_fixed': 'N.A'  # Default
                    }
            
            # Get coupon data separately (from coupon endpoint)
            coupon_url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
            coupon_data = self.fetch_api_data(coupon_url)
            if coupon_data and 'coupensVo' in coupon_data:
                if 'couponDetails' in coupon_data['coupensVo']:
                    api_values['coupon_fixed'] = coupon_data['coupensVo']['couponDetails'].get('couponRate', 'N.A')
            
            # Compare each field
            result_row = {'ISIN': isin}
            
            for key in ['seniority', 'coupon_fixed', 'pay_in_date_1', 'redemption_date_1', 
                       'issue_price', 'face_value', 'total_issue_size']:
                
                file_val = file_values.get(key)
                api_val = api_values.get(key)
                
                # Determine data type for comparison
                if key in ['pay_in_date_1', 'redemption_date_1']:
                    data_type = 'date'
                elif key in ['issue_price', 'face_value', 'total_issue_size']:
                    data_type = 'float'
                else:
                    data_type = 'text'
                
                status, notes = self.compare_values(file_val, api_val, data_type)
                
                result_row[f'{key.upper()}_FILE'] = file_val
                result_row[f'{key.upper()}_API'] = api_val
                result_row[f'{key.upper()}_STATUS'] = status
                result_row[f'{key.upper()}_NOTES'] = notes
            
            results.append(result_row)
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        return pd.DataFrame(results)
    
    def generate_ratings(self, df, delay=0.5):
        """Generate rating information for ISINs using new logic"""
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
            
            # Extract credit rating info using new function
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
        result_df = pd.DataFrame(results)
        
        # Ensure all columns exist
        for col in column_order:
            if col not in result_df.columns:
                result_df[col] = ''
        
        return result_df[column_order]
    
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
            
            if data:
                # Check if ISIN is null (matured)
                if data.get('isin') is None:
                    status = 'MATURED'
                # Check if restructured
                elif data.get('restructuredStatus') == 'Y':
                    status = 'RESTRUCTURED'
                    new_isin = data.get('newIsin', '')
                else:
                    status = 'ACTIVE'
            
            results.append({
                'ISIN': isin,
                'Matured/Restructured': status,
                'NewISIN': new_isin
            })
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        return pd.DataFrame(results)
    
    def generate_record_dates(self, df, delay=0.5):
        """Generate record dates for ISINs"""
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
            self.update_progress(f"Getting record dates {idx+1}/{total_rows}", progress_pct)
            
            result = {'ISIN': isin, 'Status': 'Failed'}
            
            for j in range(1, 6):
                result[f'record_date{j}'] = ''
                result[f'due_date{j}'] = ''
                result[f'Diff{j}'] = ''
            
            try:
                # Get coupon data
                coupon_data = self.get_coupon_data(isin)
                if not coupon_data:
                    result['Status'] = 'API Error'
                    results.append(result)
                    continue
                
                interest_payments = self.extract_interest_payments(coupon_data)
                
                if not interest_payments:
                    result['Status'] = 'No Interest Payments'
                    results.append(result)
                    continue
                
                selected_rows = self.select_interest_rows(interest_payments)
                
                for row_data in selected_rows:
                    position = row_data['position']
                    data = row_data['data']
                    
                    record_date = data['record_date']
                    due_date = data['due_date']
                    
                    result[f'record_date{position}'] = record_date
                    result[f'due_date{position}'] = due_date
                    
                    diff = self.calculate_date_diff(record_date, due_date)
                    if diff is not None:
                        result[f'Diff{position}'] = diff
                    else:
                        result[f'Diff{position}'] = 'Error'
                
                result['Status'] = 'Success'
                result['Total_Interest_Rows'] = len(interest_payments)
                result['Selected_Rows'] = len(selected_rows)
                
            except Exception as e:
                result['Status'] = f'Error: {str(e)[:50]}'
            
            results.append(result)
            time.sleep(delay + random.uniform(0, 0.3))
        
        return pd.DataFrame(results)

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
    # NSDL Scraping Features Section
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: #93c5fd; margin-bottom: 1rem;">🔧 NSDL Scraping Features:</h4>
        <ul style="font-size: 16px; line-height: 1.6; color: #cbd5e1;">
            <li><strong>Extracts data from NSDL APIs in real-time</strong> - Fetches live bond information</li>
            <li><strong>Formats dates to DD-MMM-YYYY</strong> - Standardized date formatting</li>
            <li><strong>Handles multiple ISINs simultaneously</strong> - Process batch files efficiently</li>
            <li><strong>Provides comprehensive bond analytics</strong> - 80+ data points per bond</li>
            <li><strong>Export to CSV, Excel, or JSON formats</strong> - Flexible output options</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        st.markdown("#### Select Operations:")
        do_comprehensive = st.checkbox("📊 Comprehensive Bond Data Extraction", value=True,
                                      help="Extract 80+ bond parameters from NSDL APIs")
        do_comparison = st.checkbox("🔍 Column Comparison", value=False, 
                                    help="Compare file data with NSDL API data")
        do_ratings = st.checkbox("⭐ Rating Generation (New Logic)", value=False,
                                help="Fetch credit ratings for each ISIN with Outlook1-8")
        do_matured = st.checkbox("📅 Matured/Restructured Check", value=False,
                                help="Check if bonds are matured or restructured")
        do_record_dates = st.checkbox("📅 Record Date Generation", value=False,
                                     help="Generate record dates with date differences")
        
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
        
        **Comprehensive extraction includes**:
        - Basic Bond Information
        - Coupon & Interest Details
        - Redemption Information
        - Rating & Credit Details
        - Security & Guarantee Details
        - Covenant Information
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
                                results['Comparison'] = comparison_df
                    
                    if do_ratings:
                        with st.spinner("⭐ Fetching credit ratings (New Logic)..."):
                            ratings_df = analyzer.generate_ratings(df, delay)
                            if ratings_df is not None and not ratings_df.empty:
                                results['CurrentRating_New'] = ratings_df
                    
                    if do_matured:
                        with st.spinner("📅 Checking matured/restructured status..."):
                            matured_df = analyzer.generate_matured_restructured(df, delay)
                            if matured_df is not None and not matured_df.empty:
                                results['MaturedRestructured'] = matured_df
                    
                    if do_record_dates:
                        with st.spinner("📅 Generating record dates..."):
                            record_dates_df = analyzer.generate_record_dates(df, delay)
                            if record_dates_df is not None and not record_dates_df.empty:
                                results['RecordDates'] = record_dates_df
                    
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
        st.markdown("### 📝 Sample Input Format")
        
        sample_data = pd.DataFrame({
            'ISIN': ['INE002A08567', 'INE002Z08044', 'INE003L07184'],
            'SENIORITY': ['Secured', 'Unsecured', 'Secured'],
            'Coupon_fixed': ['8.65', 'N.A', '7.5'],
            'Issue Price': [100, 100, 100],
            'Face Value': [100, 100, 100]
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
        
        st.markdown("### 📊 New Features")
        st.markdown("""
        <div class="info-box">
            <strong>Enhanced Rating Generation:</strong><br>
            • Individual Outlook columns (Outlook1-8)<br>
            • Better agency name mapping<br>
            • Cleaned rating formatting<br>
            • Proper press release links<br><br>
            
            <strong>Record Date Generation:</strong><br>
            • Extract record dates from NSDL<br>
            • Calculate days difference<br>
            • Smart row selection logic<br>
            • Status tracking for each ISIN
        </div>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()

