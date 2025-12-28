import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import time
import os
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="BADDIE - ETL | Bond Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main theme */
    .main {
        background-color: #f0f2f6;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Funny full form styling */
    .funny-fullform {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        margin: 20px auto;
        max-width: 600px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Upload button styling */
    .upload-btn {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .upload-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(30, 58, 138, 0.3);
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Success message */
    .success-msg {
        background-color: #d1fae5;
        color: #065f46;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #10b981;
    }
    
    /* Data table */
    .dataframe {
        width: 100%;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    
    /* Custom button */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Header with logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    # You can replace this with your actual logo image
    st.image("https://img.icons8.com/color/96/000000/bonds.png", width=80)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h1 class="header-title">BADDIE - ETL</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Bond Analytics & Data DEbt Intelligence Engine 😏</p>', unsafe_allow_html=True)

# Funny full form
st.markdown('<div class="funny-fullform">BADDIE = Bond Analytics & Data DEbt Intelligence Engine 😏</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📁 Upload Files")
    st.markdown("Upload Excel or CSV files containing ISIN numbers")
    
    st.markdown("---")
    st.markdown("### 🔍 Data Sources")
    st.markdown("""
    - NSDL Bond Information API
    - IndiaBondInfo Portal
    - Real-time Bond Data
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Output Columns")
    st.markdown("""
    Extracts 80+ bond parameters including:
    - Basic Information
    - Coupon Details
    - Redemption Details
    - Rating Information
    - Covenant Details
    """)

# Main content
st.markdown("### 📤 Upload Bond Data File")

# File uploader with custom styling
uploaded_file = st.file_uploader(
    "Choose Excel or CSV file",
    type=['xlsx', 'xls', 'csv'],
    help="Upload file with ISIN column",
    key="file_uploader"
)

# Function to process ISIN and extract data
def fetch_bond_data(isin):
    """Fetch bond data from NSDL APIs"""
    
    base_url = "https://www.indiabondinfo.nsdl.com/bds-service/v1/public"
    
    # Initialize data dictionary
    bond_data = {
        'ISIN': isin,
        'ISSUER NAME': '',
        'NAME OF INSTRUMENT': '',
        'DESCRIPTION IN NSDL': '',
        'SENIORITY': '',
        'SECURED/UNSECURED': '',
        'Coupon details Coupon_fixed': '',
        'Coupon details coupon_floating': '',
        'Coupon frequency': '',
        'COUPON FREQUENCY_NUMBER': '',
        'Coupoun reset Rate': '',
        'Coupoun reset Condition': '',
        'Coupoun reset Date': '',
        'pay-in details pay-in date_1': '',
        'pay-in details pay-in amt_1': '',
        'pay-in details pay-in date_2': '',
        'pay-in details pay-in amt_2': '',
        'Redemption details Redemption date_1': '',
        'Redemption details Redemption amt_1': '',
        'Redemption details Redemption date_2': '',
        'Redemption details Redemption amt_2': '',
        'Redemption details Redemption type': '',
        'Redemption_Full/ Partial': '',
        'Redemption details Redemption Premium': '',
        'ISSUE PRICE': '',
        'FACE VALUE': '',
        'Put option Date': '',
        'Put option Price': '',
        'Call option Date': '',
        'Call option Price': '',
        'Step up Rate': '',
        'Step up Condition': '',
        'Step up Date': '',
        'Step down Rate': '',
        'Step down Condition': '',
        'Step down Date': '',
        'Total issue size (Cr.)': '',
        'BASE ISSUE SIZE (CR.)': '',
        'GREEN-SHOE (CR.)': '',
        'RATED/UNRATED': '',
        'RATING_1': '',
        'CRISIL': '',
        'RATING_2': '',
        'CARE': '',
        'RATING_3': '',
        'ICRA': '',
        'RATING_4': '',
        'IND': '',
        'RATING_5': '',
        'ACUITE': '',
        'RATING_6': '',
        'BWR': '',
        'RATING_7': '',
        'SMERA': '',
        'RATING_8': '',
        'IVR': '',
        'MODE OF PLACEMENT': '',
        'TAXABLE / TAXFREE': '',
        'RECORD DATE': '',
        'LISTED/UNLISTED': '',
        'LISTING EXCHANGE': '',
        'TYPE OF INSTRUMENT': '',
        'ISSUER INDUSTRY': '',
        'OWNERSHIP': '',
        'REISSUANCE': '',
        'Guarantee Details GUARANTEE': '',
        'Guarantee Details GUARANTOR': '',
        'Guarantee Details percent_GUARANTEE': '',
        'CREDIT ENHANCEMENT': '',
        'SECURITY COVER': '',
        'NATURE OF SECURITY': '',
        'REMARKS (from IM)': '',
        'IM present? (Y/N)': '',
        'IM LINK': '',
        'CASHFLOW (Y/N)': '',
        'REMARKS (Blanks)': '',
        'MAKER (Y/N)': '',
        'MAKER (DATE)': '',
        'DERIV (Y/N)': '',
        'DERIV (DATE)': '',
        'NSDL_Autocheck (Y/N)': '',
        'Partial Redemption / Partly Redeem': '',
        'TOTAL ANCHOR AMT.': '',
        'INVESTOR 1': '',
        'AMT 1': '',
        'INVESTOR 2': '',
        'AMT 2': '',
        'INVESTOR 3': '',
        'AMT 3': '',
        'INVESTOR 4': '',
        'AMT 4': '',
        'INVESTOR 5': '',
        'AMT 5': '',
        'INVESTOR 6': '',
        'AMT 6': '',
        'INVESTOR 7': '',
        'AMT 7': '',
        'Financial Covenants _ Min NW': '',
        'Financial Covenants _ CAD Ratio': '',
        'Financial Covenants _ Min PAT_PBT_EBITDA': '',
        'Financial Covenants _ DE Ratio': '',
        'Financial Covenants _ GNPA_NNPA_PAR 90': '',
        'SHAREHOLDING CONVENANTS_SHAREHOLDER NAME': '',
        'SHAREHOLDING CONVENANTS_AMT%_HOLDING': '',
        'Other Covenants': '',
        'suspended': 'No',  # Default to No
        'restructured': '',
        'IS_SAME_PUT_CALL': '',
        'Description_of_Security': '',  # New column
        'put_description': '',  # New column
        'call_description': ''  # New column
    }
    
    try:
        # API 1: Basic ISIN info
        url1 = f"{base_url}/isins?isin={isin}"
        response1 = requests.get(url1, timeout=10)
        
        if response1.status_code == 200:
            data1 = response1.json()
            if 'data' in data1 and len(data1['data']) > 0:
                bond_data['ISSUER NAME'] = data1['data'][0].get('issuerName', '')
                bond_data['NAME OF INSTRUMENT'] = data1['data'][0].get('secType', '')
        
        # API 2: Instrument details
        url2 = f"{base_url}/bdsinfo/instruments?isin={isin}"
        response2 = requests.get(url2, timeout=10)
        
        if response2.status_code == 200:
            data2 = response2.json()
            if 'data' in data2 and len(data2['data']) > 0:
                instrument_data = data2['data'][0]
                
                # Extract data from API 2
                bond_data['DESCRIPTION IN NSDL'] = instrument_data.get('instrumentDesc', '')
                bond_data['SENIORITY'] = instrument_data.get('seniorityRepayment', '')
                bond_data['SECURED/UNSECURED'] = instrument_data.get('secured', '')
                bond_data['ISSUE PRICE'] = instrument_data.get('issuePrice', '')
                bond_data['FACE VALUE'] = instrument_data.get('faceValue', '')
                bond_data['Total issue size (Cr.)'] = instrument_data.get('totalIssueSize', '')
                bond_data['GREEN-SHOE (CR.)'] = instrument_data.get('greenShoeOption', '')
                
                # Format dates
                allotment_date = instrument_data.get('allotmentDate', '')
                if allotment_date:
                    try:
                        dt = datetime.strptime(allotment_date, '%d-%m-%Y')
                        bond_data['pay-in details pay-in date_1'] = dt.strftime('%d-%b-%Y')
                    except:
                        bond_data['pay-in details pay-in date_1'] = allotment_date
                
                redemption_date = instrument_data.get('redemptionDate', '')
                if redemption_date:
                    try:
                        dt = datetime.strptime(redemption_date, '%d-%m-%Y')
                        bond_data['Redemption details Redemption date_1'] = dt.strftime('%d-%b-%Y')
                    except:
                        bond_data['Redemption details Redemption date_1'] = redemption_date
                
                bond_data['MODE OF PLACEMENT'] = instrument_data.get('modeOfIssue', '')
                bond_data['Guarantee Details GUARANTEE'] = instrument_data.get('guarantee', '')
                
                # Guarantor details
                guarantee_details = instrument_data.get('guaranteeDetails', [])
                if guarantee_details:
                    bond_data['Guarantee Details GUARANTOR'] = guarantee_details[0].get('guaranteedBy', '')
                    bond_data['Guarantee Details percent_GUARANTEE'] = guarantee_details[0].get('guaranteePercent', '')
                
                # Credit enhancement
                credit_enhance = instrument_data.get('creditEnhanceDetails', [])
                if credit_enhance:
                    enh = credit_enhance[0]
                    if enh.get('creditEnhancementDetails') and enh['creditEnhancementDetails'] != '-':
                        bond_data['CREDIT ENHANCEMENT'] = 'Yes'
                
                # Security details
                bond_data['NATURE OF SECURITY'] = instrument_data.get('securedDetails', '')
                bond_data['SECURITY COVER'] = instrument_data.get('assetCvrPercent', '')
                
                # Asset cover details for Description_of_Security
                asset_cover = instrument_data.get('assetCover', {})
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
        response3 = requests.get(url3, timeout=10)
        
        if response3.status_code == 200:
            data3 = response3.json()
            if 'data' in data3 and len(data3['data']) > 0:
                coupon_data = data3['data'][0]
                
                bond_data['Coupon details Coupon_fixed'] = coupon_data.get('couponRate', '')
                
                # Map frequency
                freq = coupon_data.get('interestPaymentFrequency', '').upper()
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
                step_up = coupon_data.get('stepUp', [])
                if step_up:
                    for step in step_up:
                        bond_data['Step up Condition'] = step.get('otherDetailsStepUp', '')
                        bond_data['Step up Date'] = step.get('resetDateStepUp', '')
                        bond_data['Step up Rate'] = step.get('resetRateStepUp', '')
                
                step_down = coupon_data.get('stepDown', [])
                if step_down:
                    for step in step_down:
                        bond_data['Step down Condition'] = step.get('otherDetailsStepDown', '')
                        bond_data['Step down Date'] = step.get('resetDateStepDown', '')
                        bond_data['Step down Rate'] = step.get('resetRateStepDown', '')
        
        # API 4: Redemption details
        url4 = f"{base_url}/bdsinfo/redemptions?isin={isin}"
        response4 = requests.get(url4, timeout=10)
        
        if response4.status_code == 200:
            data4 = response4.json()
            if 'data' in data4 and len(data4['data']) > 0:
                redemption_data = data4['data'][0]
                
                bond_data['Redemption details Redemption type'] = redemption_data.get('redemptionType', '')
                bond_data['Redemption_Full/ Partial'] = 'Partial' if 'Partial' in str(redemption_data.get('redemptionType', '')) else 'Bullet'
                
                # Put option details
                put_option = redemption_data.get('putOption', {})
                if put_option:
                    bond_data['Put option Date'] = put_option.get('specifiedDates', '')
                    bond_data['Put option Price'] = bond_data.get('FACE_VALUE', '')
                    
                    # Create put description
                    put_desc_parts = []
                    if put_option.get('deadlineDate'):
                        put_desc_parts.append(f"Deadline: {put_option['deadlineDate']}")
                    if put_option.get('notificationTime'):
                        put_desc_parts.append(f"Notification Time: {put_option['notificationTime']}")
                    bond_data['put_description'] = ' | '.join(put_desc_parts)
                
                # Call option details
                call_option = redemption_data.get('callOption', {})
                if call_option:
                    bond_data['Call option Date'] = call_option.get('specifiedDates', '')
                    bond_data['Call option Price'] = bond_data.get('FACE_VALUE', '')
                    
                    # Create call description
                    call_desc_parts = []
                    if call_option.get('deadlineDate'):
                        call_desc_parts.append(f"Deadline: {call_option['deadlineDate']}")
                    if call_option.get('notificationTime'):
                        call_desc_parts.append(f"Notification Time: {call_option['notificationTime']}")
                    bond_data['call_description'] = ' | '.join(call_desc_parts)
        
        # API 5: Listing details
        url5 = f"{base_url}/bdsinfo/listings?isin={isin}"
        response5 = requests.get(url5, timeout=10)
        
        if response5.status_code == 200:
            data5 = response5.json()
            if 'data' in data5 and len(data5['data']) > 0:
                listing_data = data5['data'][0]
                
                bond_data['LISTED/UNLISTED'] = listing_data.get('listingStatus', '')
                listing_details = listing_data.get('listingDetails', [])
                if listing_details:
                    bond_data['LISTING EXCHANGE'] = listing_details[0].get('exchangeName', '')
        
    except Exception as e:
        st.error(f"Error fetching data for ISIN {isin}: {str(e)}")
    
    return bond_data

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Find ISIN column (case insensitive)
        isin_columns = [col for col in df.columns if 'isin' in col.lower()]
        
        if not isin_columns:
            st.error("No ISIN column found in the uploaded file. Please ensure your file has a column named 'ISIN' or 'isin'.")
        else:
            isin_column = isin_columns[0]
            isins = df[isin_column].dropna().unique().tolist()
            
            st.success(f"Found {len(isins)} unique ISINs in the uploaded file.")
            
            if st.button("🚀 Extract Bond Data", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                all_bond_data = []
                
                for i, isin in enumerate(isins):
                    status_text.text(f"Processing ISIN {i+1}/{len(isins)}: {isin}")
                    
                    # Fetch data for each ISIN
                    bond_data = fetch_bond_data(str(isin).strip())
                    all_bond_data.append(bond_data)
                    
                    # Update progress
                    progress = (i + 1) / len(isins)
                    progress_bar.progress(progress)
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                
                # Create DataFrame
                result_df = pd.DataFrame(all_bond_data)
                
                # Reorder columns to match specified order
                columns_order = [
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
                
                # Ensure all columns exist
                for col in columns_order:
                    if col not in result_df.columns:
                        result_df[col] = ''
                
                result_df = result_df[columns_order]
                
                # Display results
                st.markdown("### 📊 Extracted Bond Data")
                st.dataframe(result_df, use_container_width=True)
                
                # Download buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"bond_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    excel_buffer = BytesIO()
                    result_df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_buffer,
                        file_name=f"bond_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col3:
                    json_str = result_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"bond_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                st.markdown('<div class="success-msg">✅ Data extraction completed successfully!</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    <div class="card">
        <h4>📋 Instructions:</h4>
        <ol>
            <li>Upload an Excel or CSV file containing ISIN numbers</li>
            <li>Ensure your file has a column named <strong>ISIN</strong> (case insensitive)</li>
            <li>Click the "Extract Bond Data" button to process</li>
            <li>Download the extracted data in your preferred format</li>
        </ol>
        
        <h4>🔧 Features:</h4>
        <ul>
            <li>Extracts data from NSDL APIs in real-time</li>
            <li>Formats dates to DD-MMM-YYYY</li>
            <li>Handles multiple ISINs simultaneously</li>
            <li>Provides comprehensive bond analytics</li>
            <li>Export to CSV, Excel, or JSON formats</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Example data
    st.markdown("### 📝 Example Input Format")
    example_data = pd.DataFrame({
        'ISIN': ['INE752E08767', 'INE139F07089', 'INE722A07BE8'],
        'Issuer': ['Example Issuer 1', 'Example Issuer 2', 'Example Issuer 3']
    })
    st.dataframe(example_data, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280;'>"
    "BADDIE - ETL | Bond Analytics & Data DEbt Intelligence Engine 😏 | Powered by NSDL APIs"
    "</div>",
    unsafe_allow_html=True
)
