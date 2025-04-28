import streamlit as st
import pandas as pd

# Set page to wide layout
st.set_page_config(page_title="Stock Screener", layout="wide")

# Load data from Excel
@st.cache_data
def load_data():
    df = pd.read_excel("doc.xlsx")
    df['NSE LISTING DATE'] = pd.to_datetime(df['NSE LISTING DATE'], errors='coerce')
    df['BSE LISTING DATE'] = pd.to_datetime(df['BSE LISTING DATE'], errors='coerce')
    df['DATE OF INCORPORATION'] = pd.to_datetime(df['DATE OF INCORPORATION'], errors='coerce')
    return df

df = load_data()

st.title("📊 Stock Screener - IPO & Listing Info")

# Sidebar filters
st.sidebar.header("Filter Options")

# Symbol filter
symbols = df['Symbol'].dropna().unique()
selected_symbols = st.sidebar.multiselect("Select Symbol(s):", symbols)

# Sector filter
sectors = df['SECTOR'].dropna().unique()
selected_sectors = st.sidebar.multiselect("Select Sector(s):", sectors)

# Sub-sector filter
sub_sectors = df['SUB SECTOR'].dropna().unique()
selected_sub_sectors = st.sidebar.multiselect("Select Sub-Sector(s):", sub_sectors)

# Apply filters
filtered_df = df.copy()

if selected_symbols:
    filtered_df = filtered_df[filtered_df['Symbol'].isin(selected_symbols)]

if selected_sectors:
    filtered_df = filtered_df[filtered_df['SECTOR'].isin(selected_sectors)]

if selected_sub_sectors:
    filtered_df = filtered_df[filtered_df['SUB SECTOR'].isin(selected_sub_sectors)]

# Drop unwanted columns
columns_to_exclude = ['Series', 'Company Name', 'ISIN Code', 'IPO TIMING ON NSE']
display_df = filtered_df.drop(columns=columns_to_exclude, errors='ignore')

# Format date columns
date_cols = ['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']
for col in date_cols:
    if col in display_df.columns:
        display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')

# Show filtered table
st.write(f"### Filtered Companies ({len(display_df)} result(s))")
st.dataframe(display_df, use_container_width=True)

# CSV Download
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(display_df)

st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_companies.csv',
    mime='text/csv'
)
