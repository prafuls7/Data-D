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
    page_title="NSDL Bond Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #388E3C, #1B5E20);
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
</style>
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
            'ACUITE RATINGS & RESEARCH LIMITED': 'ACUITE',
            'BRICKWORK RATINGS INDIA PRIVATE LIMITED': 'BWR',
            'SMERA RATINGS LIMITED': 'SMERA',
            'INFOMERICS VALUATION AND RATING PRIVATE LIMITED': 'IVR'
        }
        self.progress_bar = progress_bar
        self.status_text = status_text
        
        # Column patterns for flexible matching
        self.column_patterns = {
            'isin': ['isin', 'ISIN'],
            'seniority': ['seniority', 'SENIORITY', 'Seniority'],
            'coupon_fixed': ['coupon_fixed', 'Coupon_fixed', 'Coupon Fixed', 'coupon fixed', 'Coupon'],
            'pay_in_date_1': ['pay-in date_1', 'pay in date_1', 'payin date_1', 'pay_in_date_1', 'payin date'],
            'redemption_date_1': ['redemption date_1', 'Redemption date_1', 'redemption_date_1', 'redemption date'],
            'issue_price': ['issue price', 'ISSUE PRICE', 'issue_price', 'Issue Price'],
            'face_value': ['face value', 'FACE VALUE', 'face_value', 'Face Value'],
            'total_issue_size': ['total issue size', 'TOTAL ISSUE SIZE', 'total_issue_size', 'Total Issue Size']
        }
    
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
            
            # Initialize result row with all columns
            result_row = {'ISIN': isin}
            
            # Rating columns
            rating_cols = [
                'RATING_1', 'CRISIL', 'RATING_2', 'CARE', 'RATING_3', 'ICRA',
                'RATING_4', 'IND', 'RATING_5', 'ACUITE', 'RATING_6', 'BWR',
                'RATING_7', 'SMERA', 'RATING_8', 'IVR'
            ]
            
            # Outlook columns
            outlook_cols = [f'Outlook{i}' for i in range(1, 9)]
            
            # Initialize all columns
            for col in rating_cols + outlook_cols + ['pressReleaseLink', 'dateOfVerification']:
                result_row[col] = ''
            
            press_links = []
            
            # Process current ratings
            if rating_data and 'currentRatings' in rating_data:
                for rating in rating_data['currentRatings']:
                    agency_name = rating.get('creditRatingAgencyName', '')
                    rating_value = rating.get('currentRating', '')
                    outlook_value = rating.get('outlook', '')
                    press_link = rating.get('pressReleaseLink', '')
                    
                    # Map agency name to short code
                    short_code = None
                    for full_name, short_name in self.rating_agency_mapping.items():
                        if full_name.upper() in agency_name.upper():
                            short_code = short_name
                            break
                    
                    if short_code and rating_value:
                        # Assign to appropriate columns
                        if short_code == 'CRISIL':
                            result_row['RATING_1'] = rating_value
                            result_row['CRISIL'] = 'CRISIL'
                            result_row['Outlook1'] = outlook_value
                        elif short_code == 'CARE':
                            result_row['RATING_2'] = rating_value
                            result_row['CARE'] = 'CARE'
                            result_row['Outlook2'] = outlook_value
                        elif short_code == 'ICRA':
                            result_row['RATING_3'] = rating_value
                            result_row['ICRA'] = 'ICRA'
                            result_row['Outlook3'] = outlook_value
                        elif short_code == 'IND':
                            result_row['RATING_4'] = rating_value
                            result_row['IND'] = 'IND'
                            result_row['Outlook4'] = outlook_value
                        elif short_code == 'ACUITE':
                            result_row['RATING_5'] = rating_value
                            result_row['ACUITE'] = 'ACUITE'
                            result_row['Outlook5'] = outlook_value
                        elif short_code == 'BWR':
                            result_row['RATING_6'] = rating_value
                            result_row['BWR'] = 'BWR'
                            result_row['Outlook6'] = outlook_value
                        elif short_code == 'SMERA':
                            result_row['RATING_7'] = rating_value
                            result_row['SMERA'] = 'SMERA'
                            result_row['Outlook7'] = outlook_value
                        elif short_code == 'IVR':
                            result_row['RATING_8'] = rating_value
                            result_row['IVR'] = 'IVR'
                            result_row['Outlook8'] = outlook_value
                        
                        # Add press release link
                        if press_link and press_link not in press_links:
                            press_links.append(press_link)
            
            # Combine press release links
            if press_links:
                result_row['pressReleaseLink'] = '; '.join(press_links)
            
            results.append(result_row)
            
            # Rate limiting with random delay
            time.sleep(delay + random.uniform(0, 0.3))
        
        # Create DataFrame with proper column order
        column_order = ['ISIN'] + rating_cols + outlook_cols + ['pressReleaseLink', 'dateOfVerification']
        return pd.DataFrame(results, columns=column_order)
    
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
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="text-decoration: none; color: white; background: #4CAF50; padding: 10px 20px; border-radius: 5px; font-weight: bold;">📥 {file_label}</a>'
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
    # Title
    st.title("📊 NSDL Bond Data Analyzer")
    st.markdown("Upload your Excel/CSV file with ISINs to analyze bond data from NSDL")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        st.markdown("#### Select Operations:")
        do_comparison = st.checkbox("🔍 Column Comparison", value=True, 
                                    help="Compare file data with NSDL API data")
        do_ratings = st.checkbox("⭐ Rating Generation", value=True,
                                help="Fetch credit ratings for each ISIN")
        do_matured = st.checkbox("📅 Matured/Restructured Check", value=True,
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
        
        **Optional columns** for comparison:
        - Seniority
        - Coupon_fixed
        - Pay-in date
        - Redemption date
        - Issue Price
        - Face Value
        - Total Issue Size
        """)
        
        st.markdown("---")
        
        st.markdown("#### ⏱️ Processing Time")
        st.warning("""
        Processing time depends on:
        - Number of ISINs (≈2-3 seconds each for cloud)
        - Selected operations
        - Internet speed
        
        **Example**: 100 ISINs ≈ 5-10 minutes
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
                    if do_comparison:
                        with st.spinner("🔍 Performing column comparison..."):
                            comparison_df = analyzer.perform_comparison(df, delay)
                            if comparison_df is not None and not comparison_df.empty:
                                results['Comparison'] = comparison_df
                    
                    if do_ratings:
                        with st.spinner("⭐ Fetching credit ratings..."):
                            ratings_df = analyzer.generate_ratings(df, delay)
                            if ratings_df is not None and not ratings_df.empty:
                                results['CurrentRating'] = ratings_df
                    
                    if do_matured:
                        with st.spinner("📅 Checking matured/restructured status..."):
                            matured_df = analyzer.generate_matured_restructured(df, delay)
                            if matured_df is not None and not matured_df.empty:
                                results['MaturedRestructured'] = matured_df
                    
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
                            st.metric("Total Time", f"~{len(df)*delay*len(results)/60:.1f} min")
                        
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
                                    f"NSDL_{sheet_name}.xlsx",
                                    f"Download {sheet_name}"
                                ), unsafe_allow_html=True)
                        
                        # Combined ZIP download
                        if len(results) > 1:
                            st.markdown("### Combined Download:")
                            zip_buffer = create_zip_file(results)
                            b64 = base64.b64encode(zip_buffer.getvalue()).decode()
                            href = f'<a href="data:application/zip;base64,{b64}" download="NSDL_Results.zip" style="text-decoration: none; color: white; background: #2196F3; padding: 12px 24px; border-radius: 5px; font-weight: bold;">📦 Download All Results (ZIP)</a>'
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
        st.markdown("### 📝 Sample Data Format")
        
        sample_data = pd.DataFrame({
            'ISIN': ['INE002A08567', 'INE002Z08044', 'INE003L07184'],
            'SENIORITY': ['Secured', 'Unsecured', 'Secured'],
            'Coupon_fixed': ['8.65', 'N.A', '7.5'],
            'Issue Price': [100, 100, 100],
            'Face Value': [100, 100, 100]
        })
        
        st.dataframe(sample_data, use_container_width=True)
        
        st.markdown("### 🔄 How It Works")
        
        steps = [
            "1. **Upload** your Excel/CSV file",
            "2. **Select** operations to perform",
            "3. **Click** Start Processing",
            "4. **Wait** for progress to complete",
            "5. **View** results in browser",
            "6. **Download** files as needed"
        ]
        
        for step in steps:
            st.markdown(f"- {step}")
        
        st.markdown("### ⚠️ Important Notes")
        st.warning("""
        - NSDL API may block cloud IPs (use Railway for better results)
        - Some ISINs might not be found in NSDL
        - Processing large files may take time
        - Keep browser open during processing
        - For cloud: Use 2-3 second delay between calls
        """)

# Run the app
if __name__ == "__main__":
    main()
