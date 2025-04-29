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

# Load data
stock_df = load_stock_data()
numerology_df = load_numerology_data()

st.title("📊 Stock Screener - IPO & Numerology Insight")

# === Toggle between filtering methods ===
filter_mode = st.radio("Choose Filter Mode:", ["Filter by Sector/Symbol", "Filter by Numerology"])

if filter_mode == "Filter by Sector/Symbol":
    # === Sector Filter ===
    sectors = stock_df['SECTOR'].dropna().unique()
    selected_sector = st.selectbox("Select Sector:", ["All"] + sorted(sectors))

    show_all_in_sector = st.checkbox("Show all companies in this sector", value=True)

    if selected_sector != "All":
        sector_filtered_df = stock_df[stock_df['SECTOR'] == selected_sector]
    else:
        sector_filtered_df = stock_df.copy()

    if not show_all_in_sector:
        filtered_symbols = sector_filtered_df['Symbol'].dropna().unique()
        selected_symbol = st.selectbox("Select Symbol:", sorted(filtered_symbols))
        company_data = sector_filtered_df[sector_filtered_df['Symbol'] == selected_symbol]
    else:
        company_data = sector_filtered_df

    # === Display Company Data ===
    if not company_data.empty:
        st.write("### Company Info")
        display_cols = company_data.drop(columns=['Series', 'Company Name', 'ISIN Code', 'IPO TIMING ON NSE'], errors='ignore')
        for col in ['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']:
            if col in display_cols.columns:
                display_cols[col] = display_cols[col].dt.strftime('%Y-%m-%d')
        st.dataframe(display_cols, use_container_width=True)

        if len(company_data) == 1:
            date_choice = st.radio("Select Listing Date Source for Numerology:", ("NSE LISTING DATE", "BSE LISTING DATE", "DATE OF INCORPORATION"))
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
            st.info("Select a single symbol (uncheck the box) to see numerology data.")
    else:
        st.warning("No matching data found.")

else:
    st.markdown("### 🔢 Filter by Numerology Values (Live & Horizontal Layout)")


    # Step 1: Start with full data
    filtered_numerology = numerology_df.copy()

    # Prepare layout
    col1, col2, col3, col4, col5 = st.columns(5)

    # === BN Filter ===
    with col1:
        bn_options = ["All"] + sorted(numerology_df['BN'].dropna().unique())
        selected_bn = st.selectbox("BN", bn_options)
        if selected_bn != "All":
            filtered_numerology = filtered_numerology[filtered_numerology['BN'] == selected_bn]

    # === DN Filter ===
    with col2:
        dn_options = ["All"] + sorted(filtered_numerology['DN'].dropna().unique())
        selected_dn = st.selectbox("DN", dn_options)
        if selected_dn != "All":
            filtered_numerology = filtered_numerology[filtered_numerology['DN'] == selected_dn]

    # === SN Filter ===
    with col3:
        sn_options = ["All"] + sorted(filtered_numerology['SN'].dropna().unique())
        selected_sn = st.selectbox("SN", sn_options)
        if selected_sn != "All":
            filtered_numerology = filtered_numerology[filtered_numerology['SN'] == selected_sn]

    # === HP Filter ===
    with col4:
        hp_options = ["All"] + sorted(filtered_numerology['HP'].dropna().unique())
        selected_hp = st.selectbox("HP", hp_options)
        if selected_hp != "All":
            filtered_numerology = filtered_numerology[filtered_numerology['HP'] == selected_hp]

    # === Day Number Filter ===
    with col5:
        dayn_options = ["All"] + sorted(filtered_numerology['Day Number'].dropna().unique())
        selected_dayn = st.selectbox("Day Number", dayn_options)
        if selected_dayn != "All":
            filtered_numerology = filtered_numerology[filtered_numerology['Day Number'] == selected_dayn]

    # === Show Filtered Numerology Table ===
    st.markdown("### 🔮 Filtered Numerology Table")
    if not filtered_numerology.empty:
        st.dataframe(filtered_numerology, use_container_width=True)
    else:
        st.warning("No matching numerology records found.")

    # === Match Dates to Stock Data ===
    matching_numerology_dates = filtered_numerology['date'].dropna().unique()

    matching_stocks = stock_df[
        stock_df['NSE LISTING DATE'].isin(matching_numerology_dates) |
        stock_df['BSE LISTING DATE'].isin(matching_numerology_dates) |
        stock_df['DATE OF INCORPORATION'].isin(matching_numerology_dates)
    ]

    st.markdown("### 🎯 Matching Companies")

if not matching_stocks.empty:
    highlight_dates = set(pd.to_datetime(matching_numerology_dates))

    display_cols = matching_stocks.drop(columns=['Series', 'Company Name', 'ISIN Code', 'IPO TIMING ON NSE'], errors='ignore')

    # Keep original datetime for comparison
    original_dates = display_cols[['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']].copy()

    # Format for display
    for col in ['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']:
        if col in display_cols.columns:
            display_cols[col] = display_cols[col].dt.strftime('%Y-%m-%d')

    # Define highlight function
    def highlight_matching_dates(row):
        styles = []
        for col in ['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION']:
            date_val = original_dates.at[row.name, col]
            if pd.notnull(date_val) and date_val in highlight_dates:
                styles.append('background-color: yellow')
            else:
                styles.append('')
        return styles

    styled_df = display_cols.style.apply(highlight_matching_dates, axis=1, subset=['NSE LISTING DATE', 'BSE LISTING DATE', 'DATE OF INCORPORATION'])

    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("No companies found with matching numerology dates.")
    

