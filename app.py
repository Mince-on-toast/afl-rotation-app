import streamlit as st
import pandas as pd

# 1. App Configuration & Title
st.set_page_config(page_title="AFL Rotation Manager", layout="wide")
st.title("🏉 AFL Junior 8-Rotation Manager")

# 2. Initial Squad Data (The Master Roster)
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

# 3. Sidebar: Management & Injuries
st.sidebar.header("📋 Squad Management")
for i, player in enumerate(st.session_state.players):
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"{player['Name']} ({player['Line'][0]})")
    # Toggle to "Remove" player if injured or absent
    player['Active'] = col2.checkbox("In", value=player['Active'], key=f"p_{i}")

# 4. Main Dashboard Controls
st.header("⏱ Game Controls")
phase = st.select_slider("Current Rotation Phase", options=list(range(1, 9)), value=1)

# Logic to map 1-8 phases to Group IDs (1,2,3,4,5, 1,2,3)
mapping = {1:1, 2:2, 3:3, 4:4, 5:5, 6:1, 7:2, 8:3}
next_mapping = {1:2, 2:3, 3:4, 4:5, 5:1, 6:2, 7:3, 8:4} # Preview of next bench

current_group = mapping[phase]
next_group = next_mapping[phase]

# 5. The Field View (Filter Data)
df = pd.DataFrame(st.session_state.players)
df_active = df[df['Active'] == True]

bench = df_active[df_active['Group'] == current_group]['Name'].tolist()
on_deck = df_active[df_active['Group'] == next_group]['Name'].tolist()

# Display Columns
col_field, col_bench = st.columns([3, 1])

with col_field:
    st.subheader("🏃 On the Field")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.info("**BACKS**")
        for p in df_active[(df_active['Line'] == 'Back') & (df_active['Group'] != current_group)]['Name']:
            st.write(p)
            
    with f2:
        st.success("**MIDFIELD**")
        for p in df_active[(df_active['Line'] == 'Mid') & (df_active['Group'] != current_group)]['Name']:
            st.write(p)
            
    with f3:
        st.warning("**FORWARDS**")
        for p in df_active[(df_active['Line'] == 'Forward') & (df_active['Group'] != current_group)]['Name']:
            st.write(p)

with col_bench:
    st.subheader("🪑 Bench")
    for p in bench:
        st.error(f"**OFF: {p}**")
    
    st.divider()
    st.write("🕒 **On Deck (Next Up):**")
    for p in on_deck:
        st.write(f"- {p}")

# 6. Schedule Reference
with st.expander("📅 View Full 8-Rotation Schedule"):
    sched_data = {
        "Phase": [1, 2, 3, 4, 5, 6, 7, 8],
        "Timing": ["Q1 Start", "Q1 Mid", "Q2 Start", "Q2 Mid", "Q3 Start", "Q3 Mid", "Q4 Start", "Q4 Mid"],
        "Resting Group": ["Group 1", "Group 2", "Group 3", "Group 4", "Group 5", "Group 1", "Group 2", "Group 3"]
    }
    st.table(pd.DataFrame(sched_data))
