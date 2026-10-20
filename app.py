import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Shani Industrial Software", layout="wide")

# 2. Secure Login System
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    st.title("🔐 Factory Software Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # You can change your username and password here
        if username == "admin" and password == "maputo2026":
            st.session_state['logged_in'] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# If not logged in, show login screen and stop
if not st.session_state['logged_in']:
    login_page()
else:
    # 3. Main Application after Login
    st.title("🏭 Shani Industrial Software, Maputo")
    
    # Sidebar Navigation
    menu = ["📦 Raw Materials", "🧼 Finished Goods", "💰 Sales & Invoices", "🚪 Logout"]
    choice = st.sidebar.selectbox("Factory Menu", menu)
    
    if choice == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()
        
    # --- PAGE 1: RAW MATERIALS ---
    elif choice == "📦 Raw Materials":
        st.subheader("Raw Materials Stock Manager")
        file_raw = "raw_materials.csv"
        df_raw = pd.read_csv(file_raw) if os.path.exists(file_raw) else pd.DataFrame(columns=["Material ID", "Material Name", "Stock (KG/Liters)", "Supplier"])
        
        # Form to add
        with st.form("raw_form", clear_on_submit=True):
            st.write("### Add Raw Material")
            m_id = st.text_input("Material ID")
            m_name = st.text_input("Material Name")
            m_stock = st.number_input("Quantity", min_value=0.0)
            m_supp = st.text_input("Supplier")
            if st.form_submit_button("Save Material"):
                if m_id and m_name:
                    new_row = pd.DataFrame([[m_id, m_name, m_stock, m_supp]], columns=df_raw.columns)
                    df_raw = pd.concat([df_raw, new_row], ignore_index=True)
                    df_raw.to_csv(file_raw, index=False)
                    st.success(f"{m_name} Saved!")
                    st.rerun()
        
        st.write("### Current Inventory")
        st.dataframe(df_raw, use_container_width=True)

    # --- PAGE 2: FINISHED GOODS ---
    elif choice == "🧼 Finished Goods":
        st.subheader("Finished Products Stock (Soap & Oil)")
        file_prod = "finished_goods.csv"
        df_prod = pd.read_csv(file_prod) if os.path.exists(file_prod) else pd.DataFrame(columns=["Product ID", "Product Name", "Available Stock (Boxes/Pcs)", "Price per Unit"])
        
        with st.form("prod_form", clear_on_submit=True):
            st.write("### Add Finished Product")
            p_id = st.text_input("Product ID")
            p_name = st.text_input("Product Name (e.g., Laundry Soap, Cooking Oil)")
            p_stock = st.number_input("Current Stock", min_value=0)
            p_price = st.number_input("Selling Price (Metical/USD)", min_value=0.0)
            if st.form_submit_button("Save Product"):
                if p_id and p_name:
                    new_row = pd.DataFrame([[p_id, p_name, p_stock, p_price]], columns=df_prod.columns)
                    df_prod = pd.concat([df_prod, new_row], ignore_index=True)
                    df_prod.to_csv(file_prod, index=False)
                    st.success(f"{p_name} Added!")
                    st.rerun()
                    
        st.write("### Ready Stock List")
        st.dataframe(df_prod, use_container_width=True)

    # --- PAGE 3: SALES & INVOICES ---
    elif choice == "💰 Sales & Invoices":
        st.subheader("Sales Tracker & Billing")
        file_sales = "sales.csv"
        df_sales = pd.read_csv(file_sales) if os.path.exists(file_sales) else pd.DataFrame(columns=["Invoice No", "Customer Name", "Product", "Quantity Sold", "Total Amount"])
        
        with st.form("sales_form", clear_on_submit=True):
            st.write("### New Sale Entry")
            inv_no = st.text_input("Invoice Number")
            cust_name = st.text_input("Customer Name")
            prod_sold = st.text_input("Product Sold")
            qty_sold = st.number_input("Quantity", min_value=1)
            total_amt = st.number_input("Total Bill Amount", min_value=0.0)
            if st.form_submit_button("Log Sale"):
                if inv_no and cust_name:
                    new_row = pd.DataFrame([[inv_no, cust_name, prod_sold, qty_sold, total_amt]], columns=df_sales.columns)
                    df_sales = pd.concat([df_sales, new_row], ignore_index=True)
                    df_sales.to_csv(file_sales, index=False)
                    st.success("Sale Recorded!")
                    st.rerun()
                    
        st.write("### Sales History")
        st.dataframe(df_sales, use_container_width=True)
