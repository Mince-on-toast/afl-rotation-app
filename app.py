import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- DATA INITIALIZATION ---
# We store the 'Master Pool' and the 'Assignments' separately for validation
if 'squad' not in st.session_state:
    st.session_state.squad = ["Joel", "Eli", "Jagger", "Max", "Josh", "Carmelo", "Buddy", "Jaxon F", "Harry", "Tyler", "Michael", "Ernest", "Leyton", "Jaxon J", "Xavier"]

if 'assignments' not in st.session_state:
    # 15 slots, all starting blank
    st.session_state.assignments = [{"Name": "Select Player...", "Unit": "A", "Group": i%5+1} for i in range(5)] + \
                                   [{"Name": "Select Player...", "Unit": "B", "Group": i%5+1} for i in range(5)] + \
                                   [{"Name": "Select Player...", "Unit": "C", "Group": i%5+1} for i in range(5)]

if 'line_plan' not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Forward", "B": "Back", "C": "Mid"},
        3: {"A": "Mid", "B": "Forward", "C": "Back"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- NAVIGATION ---
page = st.sidebar.radio("Navigation", ["📋 Setup Squad", "🖍 Whiteboard Plan", "🏟 LIVE OVAL"])

# --- PAGE 1: SETUP SQUAD ---
if page == "📋 Setup Squad":
    st.header("Step 1: Squad Names")
    for i in range(15):
        st.session_state.squad[i] = st.text_input(f"Player {i+1}", value=st.session_state.squad[i], key=f"sq_{i}")

# --- PAGE 2: WHITEBOARD PLAN ---
elif page == "🖍 Whiteboard Plan":
    st.header("Step 2: Set the Tone")
    st.session_state.start_grp = st.pills("Which Group starts on the bench?", [1, 2, 3, 4, 5], default=1)
    
    # Visual Grouping Styles
    st.markdown("""
        <style>
        .unit-box { border: 3px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .back-box { border-color: #1565C0; background-color: #E3F2FD; }
        .mid-box { border-color: #2E7D32; background-color: #E8F5E9; }
        .fwd-box { border-color: #EF6C00; background-color: #FFF3E0; }
        </style>
    """, unsafe_allow_html=True)

    u_cols = st.columns(3)
    unit_info = [
        (0, "A", "Unit A (Backline)", "back-box"),
        (1, "B", "Unit B (Midfield)", "mid-box"),
        (2, "C", "Unit C (Forward Line)", "fwd-box")
    ]

    for col_idx, unit_id, label, css_class in unit_info:
        with u_cols[col_idx]:
            st.markdown(f"<div class='unit-box {css_class}'><h3>{label}</h3>", unsafe_allow_html=True)
            for i in range(15):
                if st.session_state.assignments[i]["Unit"] == unit_id:
                    # Dropdown selection from master squad
                    options = ["Select Player..."] + sorted(st.session_state.squad)
                    current_val = st.session_state.assignments[i]["Name"]
                    idx = options.index(current_val) if current_val in options else 0
                    
                    st.session_state.assignments[i]["Name"] = st.selectbox(
                        f"Group {st.session_state.assignments[i]['Group']}", 
                        options, index=idx, key=f"sel_{i}"
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    # Tactical Plan
    with st.expander("🔄 Tactical Line Moves (By Unit)"):
        for q in [1, 2, 3, 4]:
            c1, c2, c3 = st.columns(3)
            st.session_state.line_plan[q]["A"] = c1.selectbox(f"Unit A Q{q}", ["Back", "Mid", "Forward"], index=0, key=f"pa{q}")
            st.session_state.line_plan[q]["B"] = c2.selectbox(f"Unit B Q{q}", ["Back", "Mid", "Forward"], index=1, key=f"pb{q}")
            st.session_state.line_plan[q]["C"] = c3.selectbox(f"Unit C Q{q}", ["Back", "Mid", "Forward"], index=2, key=f"pc{q}")

# --- PAGE 3: LIVE OVAL ---
elif page == "🏟 LIVE OVAL":
    if "prev_q" not in st.session_state: st.session_state.prev_q = 1
    q_selected = st.pills("Quarter", [1, 2, 3, 4], default=1)
    
    if q_selected != st.session_state.prev_q:
        st.session_state.timing_choice = "Starting Rotation"
        st.session_state.prev_q = q_selected
        st.rerun()

    timing = st.pills("Rotation Timing", ["Starting Rotation", "Mid-Quarter Rotation"], key="timing_choice")
    
    # Logic
    phase = ((q_selected - 1) * 2) + (1 if timing == "Starting Rotation" else 2)
    start_offset = st.session_state.get('start_grp', 1) - 1
    group_seq = [1, 2, 3, 4, 5, 1, 2, 3]
    off_grp = group_seq[(phase - 1 + start_offset) % 5]
    next_off_grp = group_seq[(phase + start_offset) % 5]

    for p in st.session_state.assignments:
        p['Zone'] = st.session_state.line_plan[q_selected][p['Unit']]
    
    df = pd.DataFrame(st.session_state.assignments)
    # Only show players who aren't 'Select Player...'
    df_ready = df[df['Name'] != "Select Player..."]

    # STYLED OVAL
    st.markdown("""<style>.zone{border:2px solid #333; border-radius:15px; padding:10px; margin-bottom:10px; background:#f0f2f6; text-align:center;} .player{display:block; padding:8px; margin:4px; background:white; border-radius:5px; border-left:8px solid #1F4E78; font-weight:bold; font-size:1.1em;}</style>""", unsafe_allow_html=True)
    
    for zone, color, label in [("Forward", "🟠", "FORWARDS"), ("Mid", "🟢", "MIDFIELD"), ("Back", "🔵", "BACKS")]:
        st.markdown(f"<div class='zone'>{color} <strong>{label}</strong></div>", unsafe_allow_html=True)
        z_players = df_ready[(df_ready['Zone'] == zone) & (df_ready['Group'] != off_grp)]
        for _, p in z_players.iterrows():
            st.markdown(f"<div class='player'>{p['Name']} [G{p['Group']}]</div>", unsafe_allow_html=True)

    st.divider()
    c_off, c_next = st.columns(2)
    with c_off:
        st.error("**OFF FIELD**")
        for _, p in df_ready[df_ready['Group'] == off_grp].iterrows():
            st.write(f"❌ {p['Name']} ({p['Zone']})")
    with c_next:
        st.warning("**UPCOMING SWAP**")
        up_off = df_ready[df_ready['Group'] == next_off_grp]
        for _, off_p in up_off.iterrows():
            on_p = df_ready[(df_ready['Unit'] == off_p['Unit']) & (df_ready['Group'] == off_grp)]
            on_name = on_p['Name'].values[0] if not on_p.empty else "No Sub"
            st.write(f"**{off_p['Name']}** ↔ **{on_name}**")
