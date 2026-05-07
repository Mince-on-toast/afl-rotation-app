import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- INITIAL SQUAD SETUP ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Unit": "A", "Group": 1, "Active": True},
        {"Name": "Eli", "Unit": "A", "Group": 2, "Active": True},
        {"Name": "Jagger", "Unit": "A", "Group": 3, "Active": True},
        {"Name": "Max", "Unit": "A", "Group": 4, "Active": True},
        {"Name": "Josh", "Unit": "A", "Group": 5, "Active": True},
        {"Name": "Carmelo", "Unit": "B", "Group": 1, "Active": True},
        {"Name": "Buddy", "Unit": "B", "Group": 2, "Active": True},
        {"Name": "Jaxon F", "Unit": "B", "Group": 3, "Active": True},
        {"Name": "Harry", "Unit": "B", "Group": 4, "Active": True},
        {"Name": "Tyler", "Unit": "B", "Group": 5, "Active": True},
        {"Name": "Michael", "Unit": "C", "Group": 1, "Active": True},
        {"Name": "Ernest", "Unit": "C", "Group": 2, "Active": True},
        {"Name": "Leyton", "Unit": "C", "Group": 3, "Active": True},
        {"Name": "Jaxon J", "Unit": "C", "Group": 4, "Active": True},
        {"Name": "Xavier", "Unit": "C", "Group": 5, "Active": True},
    ]

# --- LINE ROTATION SETTINGS ---
if 'line_plan' not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Mid", "B": "Forward", "C": "Back"},
        3: {"A": "Forward", "B": "Back", "C": "Mid"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- SIDEBAR: ATTENDANCE & STRATEGY ---
with st.sidebar:
    st.header("⚙️ Game Setup")
    
    # Select who starts on bench
    start_grp = st.radio("Who starts on bench?", [1, 2, 3, 4, 5], horizontal=True, index=0)
    
    with st.expander("🔄 Set Line Rotations"):
        for q in [1, 2, 3, 4]:
            st.write(f"**Quarter {q} Plan**")
            cols = st.columns(3)
            st.session_state.line_plan[q]["A"] = cols[0].selectbox(f"A", ["Back", "Mid", "Fwd"], index=0, key=f"q{q}a", label_visibility="collapsed")
            st.session_state.line_plan[q]["B"] = cols[1].selectbox(f"B", ["Back", "Mid", "Fwd"], index=1, key=f"q{q}b", label_visibility="collapsed")
            st.session_state.line_plan[q]["C"] = cols[2].selectbox(f"C", ["Back", "Mid", "Fwd"], index=2, key=f"q{q}c", label_visibility="collapsed")

    st.header("📋 Attendance")
    for i, p in enumerate(st.session_state.players):
        col_n, col_a = st.columns([3, 1])
        p['Name'] = col_n.text_input(f"Name {i}", value=p['Name'], key=f"n_{i}", label_visibility="collapsed")
        p['Active'] = col_a.checkbox("In", value=p['Active'], key=f"p_{i}")

# --- MAIN INTERFACE ---
st.title("🏉 AFL Rotation Pro")

# --- MOBILE CONTROLS ---
q_selected = st.radio("Quarter", [1, 2, 3, 4], horizontal=True)
phase_toggle = st.radio("Rotation", ["Start (0-7.5m)", "Mid (7.5-15m)"], horizontal=True)

# --- LOGIC ENGINE ---
raw_phase = ((q_selected - 1) * 2) + (1 if phase_toggle == "Start (0-7.5m)" else 2)
# Apply offset based on the starting group choice
group_sequence = [1, 2, 3, 4, 5, 1, 2, 3]
offset = start_grp - 1
current_off_group = group_sequence[(raw_phase - 1 + offset) % 5]
next_off_group = group_sequence[(raw_phase + offset) % 5]

# Update positions based on tactical line plan
for p in st.session_state.players:
    p['Line'] = st.session_state.line_plan[q_selected][p['Unit']]

df = pd.DataFrame(st.session_state.players)
df_active = df[df['Active'] == True]

st.divider()

# --- FIELD VIEW ---
col_field, col_bench = st.columns([2.5, 1.5])

with col_field:
    f1, f2, f3 = st.columns(3)
    lines = [("Back", "🔵 BACKS", f1), ("Mid", "🟢 MIDS", f2), ("Forward", "🟠 FWDS", f3)]
    
    for line_key, label, col in lines:
        with col:
            st.markdown(f"**{label}**")
            players_on = df_active[(df_active['Line'].str.contains(line_key)) & (df_active['Group'] != current_off_group)]
            for _, p in players_on.iterrows():
                st.success(f"**{p['Name']}** `G{p['Group']}`")

with col_bench:
    st.markdown("**🪑 CURRENT BENCH**")
    bench = df_active[df_active['Group'] == current_off_group]
    if bench.empty:
        st.write("No one resting")
    for _, p in bench.iterrows():
        st.error(f"**OFF: {p['Name']}**")
    
    st.markdown("---")
    st.markdown("**🚨 UPCOMING SUBS**")
    upcoming = df_active[df_active['Group'] == next_off_group]
    for _, p in upcoming.iterrows():
        st.warning(f"👉 **{p['Name']}** ({p['Line']})")
