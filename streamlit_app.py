import streamlit as st
import pandas as pd

# Set wide layout
st.set_page_config(page_title="Stock Screener - IPO & Numerology", layout="wide")

# Load stock data
@st.cache_data
def load_stock_data():
    df = pd.read_excel("doc.xlsx")
    df['NSE LISTING DATE'] = pd.to_datetime(df['NSE LISTING DATE'], errors='coerce')
    df['BSE LISTING DATE'] = pd.to_datetime(df['BSE LISTING DATE'], errors='coerce')
    df['DATE OF INCORPORATION'] = pd.to_datetime(df['DATE OF INCORPORATION'], errors='coerce')
    return df

# Load numerology data
@st.cache_data
def load_numerology_data():
    df = pd.read_excel("numerology.xlsx")
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    return df

stock_df = load_stock_data()
numerology_df = load_numerology_data()

st.title("📊 Stock Screener - IPO & Numerology Insight")

# === Sector Filter ===
sectors = stock_df['SECTOR'].dropna().unique()
selected_sector = st.selectbox("Select Sector (optional):", ["All"] + sorted(sectors))

# === Symbol Filter (based on selected sector) ===
if selected_sector != "All":
    filtered_symbols = stock_df[stock_df['SECTOR'] == selected_sector]['Symbol'].dropna().unique()
else:
    filtered_symbols = stock_df['Symbol'].dropna().unique()

selected_symbol = st.selectbox("Select Symbol:", sorted(filtered_symbols))

# === Filter Stock Data ===
company_data = stock_df[stock_df['Symbol'] == selected_symbol]
if selected_sector != "All":
    company_data = company_data[company_data['SECTOR'] == selected_sector]

if not company_data.empty:
    st.write("### Company Info")

    # Drop unnecessary columns
    display_cols = company_data.drop(columns=['Series', 'Company Name', 'ISIN Code', 'IPO TIMING ON NSE'], errors='ignore')

    # Format date columns
    for col in ['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']:
        if col in display_cols.columns:
            display_cols[col] = display_cols[col].dt.strftime('%Y-%m-%d')

    st.dataframe(display_cols, use_container_width=True)

    # === Date Source Selection ===
    date_choice = st.radio("Select Listing Date Source for Numerology:", ("NSE LISTING DATE", "BSE LISTING DATE",  "DATE OF INCORPORATION"))

    # Extract and parse listing date
    listing_date = pd.to_datetime(company_data[date_choice].values[0])

    if pd.notnull(listing_date):
        st.write(f"### Numerology Data for {listing_date.strftime('%Y-%m-%d')}")

        matched_numerology = numerology_df[numerology_df['date'] == listing_date]

        if not matched_numerology.empty:
            st.dataframe(matched_numerology, use_container_width=True)
        else:
            st.warning("No numerology data found for this date.")
    else:
        st.warning(f"{date_choice} is not available for this company.")
else:
    st.warning("No matching data found.")

