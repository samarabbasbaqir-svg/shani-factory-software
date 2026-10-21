import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Shani Industrial", layout="wide")

# 2. Secure Login System
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    st.title("🔐 Shani Industrial ERP Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "maputo2026":
            st.session_state['logged_in'] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

if not st.session_state['logged_in']:
    login_page()
else:
    st.title("🏭 SHANI INDUSTRIAL LIMITADA")
    st.write("---")
    
    # Navigation Menu
    menu = ["📊 Executive Dashboard", "📦 Raw Materials Management", "🧼 Production & Finished Goods", "💰 Sales & Billing", "📉 Factory Expenses", "🚪 Logout"]
    choice = st.sidebar.selectbox("Factory Navigation", menu)
    
    if choice == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()

    # --- DATA FILES SETUPS ---
    file_raw = "raw_materials_ledger.csv"
    file_prod = "production_finished_goods.csv"
    file_sales = "sales_ledger.csv"
    file_exp = "expenses_ledger.csv"

    # Columns definitions
    cols_raw = ["Date", "Material ID", "Material Name", "Type", "Quantity", "Rate", "Total Amount", "Supplier", "YearMonth", "Year"]
    cols_prod = ["Date", "Product ID", "Product Name", "Type", "Quantity", "Batch Cost", "Selling Price", "YearMonth", "Year"]
    cols_sales = ["Date", "Invoice No", "Customer Name", "Product ID", "Product Name", "Quantity Sold", "Price Per Unit", "Total Amount", "YearMonth", "Year"]
    cols_exp = ["Date", "Category", "Description", "Amount Paid", "YearMonth", "Year"]

    # Load DataFrames safely
    df_raw = pd.read_csv(file_raw) if os.path.exists(file_raw) else pd.DataFrame(columns=cols_raw)
    df_prod = pd.read_csv(file_prod) if os.path.exists(file_prod) else pd.DataFrame(columns=cols_prod)
    df_sales = pd.read_csv(file_sales) if os.path.exists(file_sales) else pd.DataFrame(columns=cols_sales)
    df_exp = pd.read_csv(file_exp) if os.path.exists(file_exp) else pd.DataFrame(columns=cols_exp)

    # Helper function to inject YearMonth and Year safely to data rows
    def sync_date_features(df):
        if not df.empty:
            df["Date"] = df["Date"].astype(str)
            df["YearMonth"] = df["Date"].apply(lambda x: str(x)[:7]) # YYYY-MM
            df["Year"] = df["Date"].apply(lambda x: str(x)[:4]) # YYYY
        return df

    df_raw = sync_date_features(df_raw)
    df_prod = sync_date_features(df_prod)
    df_sales = sync_date_features(df_sales)
    df_exp = sync_date_features(df_exp)

    # ==========================================
    # 📊 PAGE 0: EXECUTIVE ANALYTICS DASHBOARD
    # ==========================================
    if choice == "📊 Executive Dashboard":
        st.subheader("📈 Real-Time Business Performance Dashboard")
        
        filter_type = st.radio("Filter Dashboard By:", ["Cumulative (Total)", "Monthly View", "Yearly View"], horizontal=True)
        
        selected_month = None
        selected_year = None
        
        # Safe extraction of unique months/years
        list_m = sorted(list(set(df_raw["YearMonth"].tolist() + df_prod["YearMonth"].tolist() + df_sales["YearMonth"].tolist() + df_exp["YearMonth"].tolist())))
        list_y = sorted(list(set(df_raw["Year"].tolist() + df_prod["Year"].tolist() + df_sales["Year"].tolist() + df_exp["Year"].tolist())))
        
        if filter_type == "Monthly View":
            selected_month = st.selectbox("Select Month (YYYY-MM):", list_m if list_m else [datetime.today().strftime('%Y-%m')])
        elif filter_type == "Yearly View":
            selected_year = st.selectbox("Select Year (YYYY):", list_y if list_y else [datetime.today().strftime('%Y')])

        f_raw, f_prod, f_sales, f_exp = df_raw.copy(), df_prod.copy(), df_sales.copy(), df_exp.copy()

        if filter_type == "Monthly View" and selected_month:
            f_raw = f_raw[f_raw["YearMonth"] == selected_month] if not f_raw.empty else f_raw
            f_prod = f_prod[f_prod["YearMonth"] == selected_month] if not f_prod.empty else f_prod
            f_sales = f_sales[f_sales["YearMonth"] == selected_month] if not f_sales.empty else f_sales
            f_exp = f_exp[f_exp["YearMonth"] == selected_month] if not f_exp.empty else f_exp
        elif filter_type == "Yearly View" and selected_year:
            f_raw = f_raw[f_raw["Year"] == selected_year] if not f_raw.empty else f_raw
            f_prod = f_prod[f_prod["Year"] == selected_year] if not f_prod.empty else f_prod
            f_sales = f_sales[f_sales["Year"] == selected_year] if not f_sales.empty else f_sales
            f_exp = f_exp[f_exp["Year"] == selected_year] if not f_exp.empty else f_exp

        # Dashboard Logic Calculations
        raw_purchased_amt = pd.to_numeric(f_raw[f_raw["Type"] == "PURCHASE"]["Total Amount"], errors='coerce').sum() if not f_raw.empty else 0.0
        raw_consumed_amt = pd.to_numeric(f_raw[f_raw["Type"] == "CONSUME"]["Total Amount"], errors='coerce').sum() if not f_raw.empty else 0.0
        
        net_raw_val = 0.0
        if not df_raw.empty:
            for mat in df_raw["Material ID"].unique():
                m_data = df_raw[df_raw["Material ID"] == mat]
                p_qty = pd.to_numeric(m_data[m_data["Type"] == "PURCHASE"]["Quantity"], errors='coerce').sum()
                c_qty = pd.to_numeric(m_data[m_data["Type"] == "CONSUME"]["Quantity"], errors='coerce').sum()
                current_qty = p_qty - c_qty
                avg_rate = pd.to_numeric(m_data[m_data["Type"] == "PURCHASE"]["Rate"], errors='coerce').mean() if not m_data[m_data["Type"] == "PURCHASE"].empty else 0.0
                net_raw_val += (current_qty * avg_rate)

        total_prod_qty = pd.to_numeric(f_prod[f_prod["Type"] == "PRODUCTION"]["Quantity"], errors='coerce').sum() if not f_prod.empty else 0
        total_prod_cost = pd.to_numeric(f_prod[f_prod["Type"] == "PRODUCTION"]["Batch Cost"], errors='coerce').sum() if not f_prod.empty else 0.0
        total_sales_revenue = pd.to_numeric(f_sales["Total Amount"], errors='coerce').sum() if not f_sales.empty else 0.0
        
        net_fg_val = 0.0
        if not df_prod.empty:
            for pid in df_prod["Product ID"].unique():
                p_data = df_prod[df_prod["Product ID"] == pid]
                prod_qty = pd.to_numeric(p_data[p_data["Type"] == "PRODUCTION"]["Quantity"], errors='coerce').sum()
                sold_qty = pd.to_numeric(df_sales[df_sales["Product ID"] == pid]["Quantity Sold"], errors='coerce').sum() if not df_sales.empty else 0
                current_fg_stock = prod_qty - sold_qty
                latest_price = pd.to_numeric(p_data["Selling Price"], errors='coerce').iloc[-1] if not p_data.empty else 0.0
                net_fg_val += (current_fg_stock * latest_price)

        # UI Boxes
        st.write("### 📦 Raw Materials Summary")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Raw Materials Purchased Amount", f"{raw_purchased_amt:,.2f} MT")
        kpi2.metric("Total Raw Materials Consumed (Used) Amount", f"{raw_consumed_amt:,.2f} MT")
        kpi3.metric("CURRENT Live Raw Material Stock Value", f"{net_raw_val:,.2f} MT")

        st.write("### 🧼 Manufacturing & Production Summary")
        kpi4, kpi5 = st.columns(2)
        kpi4.metric("Total Production Output", f"{total_prod_qty:,} Units")
        kpi5.metric("Total Production Cost", f"{total_prod_cost:,.2f} MT")

        st.write("### 💰 Sales & Inventory Valuation")
        kpi6, kpi7 = st.columns(2)
        kpi6.metric("Total Sales Revenue Amount", f"{total_sales_revenue:,.2f} MT")
        kpi7.metric("CURRENT Finished Goods Stock Value", f"{net_fg_val:,.2f} MT")

    # ==========================================
    # 📦 PAGE 1: RAW MATERIALS MANAGEMENT
    # ==========================================
    elif choice == "📦 Raw Materials Management":
        st.subheader("Raw Material Inventory Ledger")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("raw_purchase_form", clear_on_submit=True):
                st.write("### ➕ Purchase Raw Material (Stock In)")
                r_date = st.date_input("Purchase Date", datetime.today())
                r_id = st.text_input("Material ID (e.g., MAT-OIL)")
                r_name = st.text_input("Material Name")
                r_qty = st.number_input("Quantity Purchased", min_value=0.0)
                r_rate = st.number_input("Rate Per Unit", min_value=0.0)
                r_supp = st.text_input("Supplier Details")
                
                if st.form_submit_button("Log Purchase / Add Stock"):
                    if r_id and r_name and r_qty > 0:
                        dt_str = str(r_date)
                        tot_amt = r_qty * r_rate
                        ym = dt_str[:7]
                        y = dt_str[:4]
                        new_row = pd.DataFrame([[dt_str, r_id, r_name, "PURCHASE", r_qty, r_rate, tot_amt, r_supp, ym, y]], columns=cols_raw)
                        df_raw = pd.concat([df_raw, new_row], ignore_index=True)
                        df_raw.to_csv(file_raw, index=False)
                        st.success("Purchase Logged Successfully!")
                        st.rerun()

        with col2:
            with st.form("raw_consume_form", clear_on_submit=True):
                st.write("### ➖ Issue Material for Production (Stock Out)")
                c_date = st.date_input("Issue Date", datetime.today())
                if not df_raw.empty:
                    mat_list = df_raw[df_raw["Type"] == "PURCHASE"]["Material ID"].unique().tolist()
