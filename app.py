import streamlit as st
import pandas as pd
import pickle

# 1. Page Configuration
st.set_page_config(page_title="EcoKitchen | AI System", layout="wide", initial_sidebar_state="expanded")

# Updated Custom CSS for button interaction colors
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Standard Button State */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #ff4b4b; 
        color: white; 
        border: none;
        transition: all 0.2s ease;
    }

    /* CLICKING STATE: Changes text to black and background to a slightly lighter red/grey */
    .stButton>button:active, .stButton>button:focus, .stButton>button:hover { 
        color: black !important; 
        background-color: #e0e0e0 !important; 
        border: 1px solid black !important;
    }

    .recipe-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #ff4b4b; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Resources
@st.cache_data
def load_data():
    df = pd.read_csv('recipes.csv')
    df['Category'] = df['Category'].str.strip()
    return df

try:
    recipes_df = load_data()
except FileNotFoundError:
    st.error("⚠️ Database Error: 'recipes.csv' not found.")

# 3. Sidebar & Session State Initialization
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_recipe_trigger' not in st.session_state:
    st.session_state.show_recipe_trigger = False
if 'display_recipes' not in st.session_state:
    st.session_state.display_recipes = False

st.sidebar.title("📜 Prediction History")
if st.session_state.history:
    for item in reversed(st.session_state.history):
        st.sidebar.info(f"{item['item']} - {item['status']}")
    if st.sidebar.button("Clear History"):
        st.session_state.history = []
        st.rerun()
else:
    st.sidebar.write("No recent activity.")

# 4. Main UI Header
st.title("🥗 Food Waste Risk Prediction and Recipe Recommendation System")
st.markdown("---")

# 5. User Input Form
with st.container():
    st.markdown("### 🛒 Inventory Input")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox("Category", ["Bakery", "Grains/Legumes", "Dairy", "Protein", "Produce"])
        quantity = st.number_input("Quantity (grams)", min_value=0, step=10, value=500)
    with col2:
        storage = st.selectbox("Storage Condition", ["Refrigerated", "Ambient"])
        price = st.number_input("Cost (INR)", min_value=0, step=1, value=150)
    with col3:
        shelf_life = st.number_input("Total Shelf Life (Days)", min_value=1, step=1, value=7)
        days_left = st.number_input("Days Left until Expiry", min_value=-30, step=1, value=1)

# 6. Prediction Logic
if st.button("🚀 Predict"):
    st.session_state.show_recipe_trigger = False
    st.session_state.display_recipes = False
    
    status_label = ""

    if days_left < 0:
        status_label = "Expired"
        st.error(f"### 🚨 ALREADY EXPIRED: {abs(days_left)} Days Overdue")
        st.warning("⚠️ **Recommendation:** This item is unsafe for consumption.")
        
    elif days_left == 0:
        status_label = "Expires Today"
        st.error("### 🚨 CRITICAL: Expires Today")
        st.session_state.show_recipe_trigger = True
        
    elif days_left <= 2:
        status_label = "High Risk"
        st.warning(f"### ⚠️ HIGH WASTE RISK: {days_left} Days Remaining")
        st.session_state.show_recipe_trigger = True
        
    else:
        status_label = "Low Risk"
        st.success("### ✅ STATUS: Fresh & Low Risk")

    st.session_state.history.append({"item": category, "status": status_label})

# 7. Conditional Recipe Button & Display
if st.session_state.show_recipe_trigger:
    st.markdown("---")
    st.subheader("👨‍🍳 Resource Optimization")
    
    if st.button("✨ Show Recommended Recipes"):
        st.session_state.display_recipes = True
    
    if st.session_state.display_recipes:
        matched_recipes = recipes_df[recipes_df['Category'] == category]
        
        if not matched_recipes.empty:
            recs = matched_recipes.sample(min(10, len(matched_recipes)))
            for idx, row in recs.iterrows():
                st.markdown(f"""
                <div class="recipe-card">
                    <h4>🍴 {row['Recipe_Name']}</h4>
                    <p><b>Ingredients:</b> {row['Ingredients']}</p>
                    <p>🏷️ <b>Cuisine:</b> {row['Cuisine']} | ⏲️ <b>Prep:</b> {row['Preparation_Time_Min']}m | 🔥 <b>Calories:</b> {row['Calories_kcal']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Searching for local alternatives...")