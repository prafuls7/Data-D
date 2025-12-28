import streamlit as st
import pandas as pd
import requests
import time
import base64
from io import BytesIO

# Page config
st.set_page_config(page_title="NSDL Bond Analyzer", layout="wide")

st.title("📊 NSDL Bond Data Analyzer")
st.markdown("Upload Excel/CSV with ISINs")

# File upload
uploaded_file = st.file_uploader("Choose file", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File loaded: {len(df)} rows")
        
        # Check for ISIN column
        isin_col = None
        for col in df.columns:
            if 'isin' in str(col).lower():
                isin_col = col
                break
        
        if not isin_col:
            st.error("❌ No ISIN column found!")
        else:
            st.info(f"Found ISIN column: '{isin_col}'")
            
            if st.button("🚀 Process ISINs"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                isins = df[isin_col].dropna().unique()
                
                for idx, isin in enumerate(isins):
                    isin = str(isin).strip()
                    if not isin:
                        continue
                    
                    # Update progress
                    progress = (idx + 1) / len(isins)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx+1}/{len(isins)}: {isin}")
                    
                    try:
                        # Fetch data from NSDL
                        url = f"https://www.indiabondinfo.nsdl.com/bds-service/v1/public/bdsinfo/instruments?isin={isin}"
                        response = requests.get(url, timeout=10)
                        
                        result = {'ISIN': isin}
                        if response.status_code == 200:
                            data = response.json()
                            result['Status'] = 'FOUND'
                            
                            # Extract some data
                            if 'instrumentsVo' in data and 'instruments' in data['instrumentsVo']:
                                inst = data['instrumentsVo']['instruments']
                                result['Face_Value'] = inst.get('faceValue')
                                result['Seniority'] = inst.get('secured')
                                result['Redemption_Date'] = inst.get('redemptionDate')
                        else:
                            result['Status'] = 'NOT_FOUND'
                        
                        results.append(result)
                        
                    except Exception as e:
                        results.append({'ISIN': isin, 'Status': f'ERROR: {str(e)}'})
                    
                    # Small delay
                    time.sleep(0.5)
                
                # Complete
                progress_bar.progress(1.0)
                status_text.text("✅ Processing complete!")
                
                # Show results
                if results:
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)
                    
                    # Download
                    csv = results_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="nsdl_results.csv">📥 Download Results</a>'
                    st.markdown(href, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Upload a file to begin. File should contain ISIN column.")

st.markdown("---")
st.markdown("Made with ❤️ | Live 24/7 on Render")
