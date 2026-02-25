import streamlit as st
import mysql.connector
import config
import pandas as pd

# Page setup
st.set_page_config(page_title="Poker Analytics Dashboard", layout="wide")
st.title("🃏 Poker Hand Explorer")

# Database connection
def get_data(query):
    db = mysql.connector.connect(**config.DB_CONFIG)
    df = pd.read_sql(query, db)
    db.close()
    return df

# Sidebar filters
st.sidebar.header("Filters")
game_type = st.sidebar.selectbox("Select Game Type", ["All", "Freeroll", "Mystery"])
search_query = st.sidebar.text_input("Search in Raw Text (e.g., 'Hero: raises')")

# Build SQL query
query = "SELECT hand_id, hand_date, game_type, level_info, hero_cards, board, pot_size, raw_text FROM tournament_hands WHERE 1=1"
if game_type != "All":
    query += f" AND game_type = '{game_type}'"
if search_query:
    query += f" AND raw_text LIKE '%{search_query}%'"

query += " ORDER BY hand_date DESC"

# Load data
try:
    df = get_data(query)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hands", len(df))
    col2.metric("Avg Pot Size", int(df['pot_size'].mean()) if not df.empty else 0)
    col3.metric("Biggest Pot", df['pot_size'].max() if not df.empty else 0)

    # Data Table
    st.subheader("Hand History")
    # Display table but hide the long raw_text by default
    st.dataframe(df.drop(columns=['raw_text']), use_container_width=True)

    # Inspection area
    if not df.empty:
        st.subheader("Inspect Specific Hand")
        selected_hand = st.selectbox("Select Hand ID to see full log", df['hand_id'])
        full_text = df[df['hand_id'] == selected_hand]['raw_text'].values[0]
        st.text_area("Raw Hand Log", full_text, height=300)

except Exception as e:
    st.error(f"Error connecting to database: {e}")