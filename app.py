import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- INITIAL SQUAD SETUP ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Line": "Back", "Group": 1, "Active": True},
        {"Name": "Eli", "Line": "Back", "Group": 2, "Active": True},
        {"Name": "Jagger", "Line": "Back", "Group": 3, "Active": True},
        {"Name": "Max", "Line": "Back", "Group": 4, "Active": True},
        {"Name": "Josh", "Line": "Back", "Group": 5, "Active": True},
        {"Name": "Carmelo", "Line": "Mid", "Group": 1, "Active": True},
        {"Name": "Buddy", "Line": "Mid", "Group": 2, "Active": True},
        {"Name": "Jaxon F", "Line": "Mid", "Group": 3, "Active": True},
        {"Name": "Harry", "Line": "Mid", "Group": 4, "Active": True},
        {"Name": "Tyler", "Line": "Mid", "Group": 5, "Active": True},
        {"Name": "Michael", "Line": "Forward", "Group": 1, "Active": True},
        {"Name": "Ernest", "Line": "Forward", "Group": 2, "Active": True},
        {"Name": "Leyton", "Line": "Forward", "Group": 3, "Active": True},
        {"Name": "Jaxon J", "Line": "Forward", "Group": 4, "Active": True},
        {"Name": "Xavier", "Line": "Forward", "Group": 5, "Active": True},
    ]

# --- TIMER LOGIC ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'running' not in st.session_state:
    st.session_state.running = False

# --- SIDEBAR: POSITION EDITOR & SQUAD ---
with st.sidebar:
    st.header("📋 Lineup Editor")
    st.write("Set positions before the game.")
    for i, p in enumerate(st.session_state.players):
        col1, col2, col3 = st.columns([2, 2, 1])
        p['Name'] = col1.text_input(f"Name", value=p['Name'], key=f"name_{i}", label_visibility="collapsed")
        p['Line'] = col2.selectbox(f"Line", ["Back", "Mid", "Forward"], index=["Back", "Mid", "Forward"].index(p['Line']), key=f"line_{i}", label_visibility="collapsed")
        p['Active'] = col3.checkbox("In", value=p['Active'], key=f"act_{i}")

# --- MAIN INTERFACE ---
st.title("🏉 AFL Rotation Pro")

# --- TIMER & QUARTER CONTROL ---
t_col1, t_col2 = st.columns([2, 1])

with t_col1:
    q_selected = st.radio("Current Quarter", [1, 2, 3, 4], horizontal=True)
    
    # Simple Manual Rotation Phase Toggle (replacing slider)
    phase_toggle = st.radio("Rotation Timing", ["Start (0-7.5m)", "Mid (7.5-15m)"], horizontal=True)
    
    # Calculate Phase (1-8)
    phase = ((q_selected - 1) * 2) + (1 if phase_toggle == "Start (0-7.5m)" else 2)

with t_col2:
    st.metric("Current Rotation Phase", f"Phase {phase}")
    st.caption(f"Target Sub: {'Start of Qtr' if phase_toggle == 'Start (0-7.5m)' else 'Mid-Quarter'}")

st.divider()

# --- ROTATION ENGINE ---
mapping = {1:1, 2:2, 3:3, 4:4, 5:5, 6:1, 7:2, 8:3}
next_mapping = {1:2, 2:3, 3:4, 4:5, 5:1, 6:2, 7:3, 8:4}

current_group = mapping[phase]
next_group = next_mapping[phase]

df = pd.DataFrame(st.session_state.players)
df_active = df[df['Active'] == True]

# --- FIELD VIEW ---
col_field, col_bench = st.columns([3, 1])

with col_field:
    f1, f2, f3 = st.columns(3)
    
    lines = [("Back", "🔵 BACKS", f1), ("Mid", "🟢 MIDFIELD", f2), ("Forward", "🟠 FORWARDS", f3)]
    
    for line_key, label, col in lines:
        with col:
            st.subheader(label)
            players_on = df_active[(df_active['Line'] == line_key) & (df_active['Group'] != current_group)]
            for _, p in players_on.iterrows():
                st.info(f"**{p['Name']}** `G{p['Group']}`")

with col_bench:
    st.subheader("🪑 Bench")
    bench = df_active[df_active['Group'] == current_group]
    for _, p in bench.iterrows():
        st.error(f"**OFF: {p['Name']}**")
    
    st.divider()
    st.write("🕒 **On Deck (Next Up):**")
    on_deck = df_active[df_active['Group'] == next_group]
    for _, p in on_deck.iterrows():
        st.write(f"👉 {p['Name']} (Group {p['Group']})")

# --- AUTO-REFRESH SCRIPT (Optional for Timer feel) ---
st.caption("Instructions: At the 7.5 minute mark of the quarter, tap 'Mid (7.5-15m)' to cycle the players.")
