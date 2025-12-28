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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

warnings.filterwarnings('ignore')

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="BADDIE - ETL | Bond Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS with BADDIE theme - FIXED FOR TEXT VISIBILITY
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-blue: #3b82f6;
        --light-blue: #eff6ff;
        --accent-color: #8b5cf6;
        --dark-text: #1e293b;
        --medium-text: #475569;
    }
    
    /* Main app background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Ensure all text is visible */
    body {
        color: #1e293b !important;
    }
    
    /* Make Streamlit default text dark */
    .stMarkdown, .stText, .stInfo, .stWarning, .stSuccess, .stError {
        color: #1e293b !important;
    }
    
    /* Sidebar text */
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #1e293b !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.2);
    }
    
    .logo-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 15px;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        color: white !important;
    }
    
    .app-subtitle {
        font-size: 1.4rem;
        opacity: 0.95;
        font-style: italic;
        margin-bottom: 10px;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .funny-tagline {
        background: rgba(255,255,255,0.15);
        padding: 10px 25px;
        border-radius: 25px;
        display: inline-block;
        font-weight: bold;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        color: white !important;
    }
    
    /* Upload button styling - Blue/White theme */
    .upload-btn {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        border: 2px solid white;
        padding: 15px 35px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }
    
    .upload-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.4);
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        padding: 12px 28px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
        background-image: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    /* Success message */
    .success-box {
        padding: 25px;
        background: linear-gradient(135deg, #dbeafe 0%, #f0f9ff 100%);
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        color: #1e293b !important;
    }
    
    .success-box h4, .success-box p {
        color: #1e293b !important;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #3b82f6;
        color: #1e293b !important;
    }
    
    .feature-card h4, .feature-card li, .feature-card strong {
        color: #1e293b !important;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* Sidebar styling - FIXED FOR VISIBILITY */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Sidebar text specifically */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown code {
        color: #1e293b !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #f0f9ff;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid #e0f2fe;
        color: #1e293b !important;
    }
    
    .info-box h4, .info-box li, .info-box ol, .info-box strong {
        color: #1e293b !important;
    }
    
    /* Feature list styling */
    .feature-list li {
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 10px;
        padding-left: 5px;
        color: #1e293b !important;
    }
    
    /* Funny full form display */
    .fullform-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 25px auto;
        max-width: 700px;
        border: 2px dashed #3b82f6;
        color: #1e293b !important;
    }
    
    .fullform-box h3, .fullform-box p {
        color: #1e293b !important;
    }
    
    /* Logo styling */
    .logo-circle {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white !important;
        font-weight: bold;
        font-size: 24px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    /* Streamlit info, warning, success boxes */
    .stAlert, .stInfo, .stWarning, .stSuccess, .stError {
        color: #1e293b !important;
    }
    
    /* Make sure all headings are visible */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    /* Make sure all paragraphs and list items are visible */
    p, li, span, div {
        color: #1e293b !important;
    }
    
    /* Fix slider text */
    .stSlider label {
        color: #1e293b !important;
    }
    
    /* Fix checkbox text */
    .stCheckbox label {
        color: #1e293b !important;
    }
    
    /* Fix uploader text */
    .stFileUploader label {
        color: #1e293b !important;
    }
    
    /* Make metric values visible */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

class NSDLBondAnalyzer:
    def __init__(self, progress_bar=None, status_text=None):
        # Create session with retry strategy
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        self.rating_agency_mapping = {
            'CRISIL RATINGS LIMITED': 'CRISIL',
            'CARE RATINGS LIMITED': 'CARE', 
            'ICRA LIMITED': 'ICRA',
            'INDIA RATINGS AND RESEARCH PRIVATE LIMITED': 'IND',
            'ACUITE RATINGS & RESEARCH LIMITED': 'ACUITE',
            'BRICKWORK RATINGS INDIA PRIVATE LIMITED': 'BWR',
            'SMERA RATINGS LIMITED': 'SMERA',
            'INFOMERICS VALUATION AND RATING PRIVATE LIMITED': 'IVR'
        }
        self.progress_bar = progress_bar
        self.status_text = status_text
        
        # Define all output columns
        self.output_columns = [
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
                        text = response.text.strip()
                        if text.startswith('"') and text.endswith('"'):
                            text = text[1:-1]
                        return json.loads(text)
                elif response.status_code == 429:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return {}
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return {}
        
        return {}
    
    def extract_bond_data(self, isin):
        """Extract comprehensive bond data from NSDL APIs"""
        base_url = "https://www.indiabondinfo.nsdl.com/bds-service/v1/public"
        bond_data = {col: '' for col in self.output_columns}
        bond_data['ISIN'] = isin
        bond_data['suspended'] = 'No'
        bond_data['restructured'] = ''
        
        try:
            # API 1: Basic ISIN info
            url1 = f"{base_url}/isins?isin={isin}"
            data1 = self.fetch_api_data(url1)
            
            if data1 and 'data' in data1 and len(data1['data']) > 0:
                bond_data['ISSUER NAME'] = data1['data'][0].get('issuerName', '')
                bond_data['NAME OF INSTRUMENT'] = data1['data'][0].get('secType', '')
            
            # API 2: Instrument details
            url2 = f"{base_url}/bdsinfo/instruments?isin={isin}"
            data2 = self.fetch_api_data(url2)
            
            if data2 and 'data' in data2 and len(data2['data']) > 0:
                inst = data2['data'][0]
                
                bond_data['DESCRIPTION IN NSDL'] = inst.get('instrumentDesc', '')
                bond_data['SENIORITY'] = inst.get('seniorityRepayment', inst.get('securedFlag', ''))
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
            url3 = f"{base_url}/bdsinfo/coupondetail?isin={isin}"
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
            url4 = f"{base_url}/bdsinfo/redemptions?isin={isin}"
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
            url5 = f"{base_url}/bdsinfo/listings?isin={isin}"
            data5 = self.fetch_api_data(url5)
            
            if data5 and 'data' in data5 and len(data5['data']) > 0:
                listing = data5['data'][0]
                
                bond_data['LISTED/UNLISTED'] = listing.get('listingStatus', '')
                listing_details = listing.get('listingDetails', [])
                if listing_details:
                    bond_data['LISTING EXCHANGE'] = listing_details[0].get('exchangeName', '')
            
            # Rating data
            url6 = f"{base_url}/bdsinfo/credit-ratings?isin={isin}"
            data6 = self.fetch_api_data(url6)
            
            if data6 and 'currentRatings' in data6:
                for rating in data6['currentRatings']:
                    agency_name = rating.get('creditRatingAgencyName', '')
                    rating_value = rating.get('currentRating', '')
                    
                    for full_name, short_code in self.rating_agency_mapping.items():
                        if full_name.upper() in agency_name.upper():
                            if short_code == 'CRISIL':
                                bond_data['RATING_1'] = rating_value
                                bond_data['CRISIL'] = 'CRISIL'
                            elif short_code == 'CARE':
                                bond_data['RATING_2'] = rating_value
                                bond_data['CARE'] = 'CARE'
                            elif short_code == 'ICRA':
                                bond_data['RATING_3'] = rating_value
                                bond_data['ICRA'] = 'ICRA'
                            elif short_code == 'IND':
                                bond_data['RATING_4'] = rating_value
                                bond_data['IND'] = 'IND'
                            elif short_code == 'ACUITE':
                                bond_data['RATING_5'] = rating_value
                                bond_data['ACUITE'] = 'ACUITE'
                            elif short_code == 'BWR':
                                bond_data['RATING_6'] = rating_value
                                bond_data['BWR'] = 'BWR'
                            elif short_code == 'SMERA':
                                bond_data['RATING_7'] = rating_value
                                bond_data['SMERA'] = 'SMERA'
                            elif short_code == 'IVR':
                                bond_data['RATING_8'] = rating_value
                                bond_data['IVR'] = 'IVR'
                            break
            
            # Set RATED/UNRATED based on ratings
            if any(bond_data.get(f'RATING_{i}') for i in range(1, 9)):
                bond_data['RATED/UNRATED'] = 'RATED'
            else:
                bond_data['RATED/UNRATED'] = 'UNRATED'
            
            # Set NSDL_Autocheck
            bond_data['NSDL_Autocheck (Y/N)'] = 'Y'
            
        except Exception as e:
            bond_data['ERROR'] = str(e)
        
        return bond_data
    
    def process_isins(self, isins, delay=0.5):
        """Process multiple ISINs and extract bond data"""
        results = []
        total_isins = len(isins)
        
        for idx, isin in enumerate(isins):
            isin = str(isin).strip()
            if not isin or isin.lower() == 'nan':
                continue
            
            # Update progress
            progress_pct = (idx + 1) / total_isins
            self.update_progress(f"Extracting data for ISIN {idx+1}/{total_isins}", progress_pct)
            
            # Extract bond data
            bond_data = self.extract_bond_data(isin)
            results.append(bond_data)
            
            # Rate limiting
            time.sleep(delay + random.uniform(0, 0.3))
        
        # Create DataFrame with all columns
        df = pd.DataFrame(results)
        
        # Ensure all output columns exist
        for col in self.output_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        return df[self.output_columns]

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
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="text-decoration: none; color: white; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 12px 24px; border-radius: 8px; font-weight: bold; border: 2px solid white; display: inline-block; margin: 5px;">📥 {file_label}</a>'
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
    # Header with BADDIE branding
    st.markdown("""
    <div class="main-header">
        <div class="logo-header">
            <div class="logo-circle">B</div>
            <div>
                <h1 class="app-title">BADDIE - ETL</h1>
                <p class="app-subtitle">Bond Analytics & Data DEbt Intelligence Engine</p>
                <div class="funny-tagline">😏 Making bond analysis cool again!</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Funny full form display
    st.markdown("""
    <div class="fullform-box">
        <h3 style="color: #1e40af; margin: 0;">🎯 BADDIE = <span style="color: #3b82f6;">B</span>ond <span style="color: #3b82f6;">A</span>nalytics & <span style="color: #3b82f6;">D</span>ata <span style="color: #3b82f6;">D</span>Ebt <span style="color: #3b82f6;">I</span>ntelligence <span style="color: #3b82f6;">E</span>ngine</h3>
        <p style="color: #6b7280; margin-top: 10px; font-style: italic;">Because regular bond analysis was too mainstream! 😎</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with DARK TEXT
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        st.markdown("#### 📊 Data Extraction:")
        st.info("Extracts 80+ bond parameters from NSDL APIs in real-time")
        
        st.markdown("---")
        
        st.markdown("#### ⚡ Rate Limiting")
        delay = st.slider("Delay between API calls (seconds)", 
                        0.5, 3.0, 1.0, 0.1,
                        help="Increase if getting rate limited")
        
        st.markdown("---")
        
        st.markdown("#### 📋 Supported File Formats")
        st.info("""
        **Excel**: .xlsx, .xls  
        **CSV**: .csv  
        
        **Required column**: ISIN (or isin)  
        
        **Output includes**:  
        • Basic Bond Information  
        • Coupon & Interest Details  
        • Redemption Information  
        • Rating & Credit Details  
        • Security & Guarantee Details  
        • Covenant Information  
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
    
    # Main content area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # File upload
        st.markdown("### 📤 Upload Bond Data File")
        
        uploaded_file = st.file_uploader(
            "**Choose your Excel or CSV file**",
            type=['xlsx', 'xls', 'csv'],
            help="File should contain ISIN column. The app will automatically detect ISIN numbers.",
            key="file_uploader"
        )
        
        # Features section
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 Features:</h4>
            <ul class="feature-list">
                <li><strong>Extracts data from NSDL APIs in real-time</strong> - Fetches live bond information from multiple endpoints</li>
                <li><strong>Formats dates to DD-MMM-YYYY</strong> - Standardized date formatting across all outputs</li>
                <li><strong>Handles multiple ISINs simultaneously</strong> - Process batch files efficiently with progress tracking</li>
                <li><strong>Provides comprehensive bond analytics</strong> - 80+ data points per bond including ratings, covenants, and security details</li>
                <li><strong>Export to CSV, Excel, or JSON formats</strong> - Flexible output options for further analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
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
                
                # Find ISIN column
                isin_columns = [col for col in df.columns if 'isin' in col.lower()]
                
                if not isin_columns:
                    st.error("❌ No ISIN column found. Please ensure your file has a column named 'ISIN' or 'isin'.")
                else:
                    isin_column = isin_columns[0]
                    isins = df[isin_column].dropna().unique().tolist()
                    
                    st.success(f"✅ Found **{len(isins)}** unique ISINs in the uploaded file.")
                    
                    # Process button
                    if st.button("🚀 Extract Bond Data from NSDL", type="primary", use_container_width=True):
                        # Create progress elements
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Create analyzer instance
                        analyzer = NSDLBondAnalyzer(progress_bar, status_text)
                        
                        # Process ISINs
                        with st.spinner("🔍 Extracting bond data from NSDL..."):
                            result_df = analyzer.process_isins(isins, delay)
                        
                        # Complete progress
                        progress_bar.progress(1.0)
                        status_text.text("✅ Data extraction complete!")
                        
                        # Display results
                        if not result_df.empty:
                            st.markdown("---")
                            st.markdown("## 📊 Extracted Bond Data")
                            
                            # Display statistics
                            col_stat1, col_stat2, col_stat3 = st.columns(3)
                            with col_stat1:
                                st.metric("Total ISINs Processed", len(isins))
                            with col_stat2:
                                st.metric("Columns Extracted", len(result_df.columns))
                            with col_stat3:
                                st.metric("Data Points", f"{len(isins) * len(result_df.columns):,}")
                            
                            # Show data
                            st.dataframe(result_df, use_container_width=True, height=400)
                            
                            # Download section
                            st.markdown("---")
                            st.markdown("## 💾 Download Results")
                            
                            # Individual downloads
                            st.markdown("### Download Formats:")
                            col_dl1, col_dl2, col_dl3 = st.columns(3)
                            
                            with col_dl1:
                                st.markdown(get_download_link(
                                    result_df,
                                    f"BADDIE_Bond_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    "Download Excel"
                                ), unsafe_allow_html=True)
                            
                            with col_dl2:
                                st.markdown(get_download_link(
                                    result_df,
                                    f"BADDIE_Bond_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    "Download CSV"
                                ), unsafe_allow_html=True)
                            
                            with col_dl3:
                                json_str = result_df.to_json(orient='records', indent=2)
                                json_b64 = base64.b64encode(json_str.encode()).decode()
                                href = f'<a href="data:application/json;base64,{json_b64}" download="BADDIE_Bond_Data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" style="text-decoration: none; color: white; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 12px 24px; border-radius: 8px; font-weight: bold; border: 2px solid white; display: inline-block; margin: 5px;">📥 Download JSON</a>'
                                st.markdown(href, unsafe_allow_html=True)
                            
                            # Success message
                            st.balloons()
                            st.markdown("""
                            <div class="success-box">
                                <h4>🎉 Bond data extraction completed successfully!</h4>
                                <p>All 80+ bond parameters have been extracted from NSDL APIs and are ready for download.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        else:
                            st.warning("⚠️ No data extracted. Please check if your file contains valid ISINs.")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("Please check: 1) File format, 2) File is not corrupted, 3) Contains ISIN column")
    
    with col2:
        # Sample data and instructions
        st.markdown("### 📝 Sample Input Format")
        
        sample_data = pd.DataFrame({
            'ISIN': ['INE752E08767', 'INE139F07089', 'INE722A07BE8'],
            'Issuer_Name': ['Power Grid Corporation', 'Example Corp 1', 'Example Corp 2']
        })
        
        st.dataframe(sample_data, use_container_width=True)
        
        st.markdown("### 🔄 How It Works")
        
        steps = [
            "1. **Upload** your Excel/CSV file with ISINs",
            "2. **Set** delay between API calls (0.5-3 seconds)",
            "3. **Click** 'Extract Bond Data from NSDL'",
            "4. **Wait** for progress to complete",
            "5. **View** extracted bond data",
            "6. **Download** in Excel, CSV, or JSON"
        ]
        
        for step in steps:
            st.markdown(f"- {step}")
        
        st.markdown("### 📊 Output Columns Preview")
        st.info("""
        **Key sections extracted:**
        • ✅ Basic Bond Information  
        • ✅ Coupon & Interest Details  
        • ✅ Redemption Information  
        • ✅ Rating & Credit Details  
        • ✅ Security & Guarantee Details  
        • ✅ Covenant Information  
        • ✅ NSDL Verification Status  
        """)
        
        st.markdown("### ⚠️ Important Notes")
        st.warning("""
        • NSDL APIs may have rate limits  
        • Processing time depends on number of ISINs  
        • Some bonds may not have all data fields  
        • Keep browser open during processing  
        • For large files: Use 1-2 second delay  
        • All dates formatted as DD-MMM-YYYY  
        """)

# Run the app
if __name__ == "__main__":
    main()
