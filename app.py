import streamlit as st
import pandas as pd

st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# --- INITIAL SQUAD DATA ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {"Name": "Joel", "Cell": "A", "Grp": 1, "Active": True},
        {"Name": "Eli", "Cell": "A", "Grp": 2, "Active": True},
        {"Name": "Jagger", "Cell": "A", "Grp": 3, "Active": True},
        {"Name": "Max", "Cell": "A", "Grp": 4, "Active": True},
        {"Name": "Josh", "Cell": "A", "Grp": 5, "Active": True},
        {"Name": "Carmelo", "Cell": "B", "Grp": 1, "Active": True},
        {"Name": "Buddy", "Cell": "B", "Grp": 2, "Active": True},
        {"Name": "Jaxon F", "Cell": "B", "Grp": 3, "Active": True},
        {"Name": "Harry", "Cell": "B", "Grp": 4, "Active": True},
        {"Name": "Tyler", "Cell": "B", "Grp": 5, "Active": True},
        {"Name": "Michael", "Cell": "C", "Grp": 1, "Active": True},
        {"Name": "Ernest", "Cell": "C", "Grp": 2, "Active": True},
        {"Name": "Leyton", "Cell": "C", "Grp": 3, "Active": True},
        {"Name": "Jaxon J", "Cell": "C", "Grp": 4, "Active": True},
        {"Name": "Xavier", "Cell": "C", "Grp": 5, "Active": True},
    ]

if 'cell_plan' not in st.session_state:
    st.session_state.cell_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Forward", "B": "Back", "C": "Mid"},
        3: {"A": "Mid", "B": "Forward", "C": "Back"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"}
    }

# --- NAVIGATION ---
page = st.sidebar.radio("Navigation", ["📋 Setup Squad", "🖍 Whiteboard Plan", "🏟 LIVE OVAL"])

# --- PAGE 1: SETUP SQUAD ---
if page == "📋 Setup Squad":
    st.header("Step 1: Attendance")
    st.write("Mark who is playing today.")
    for p in st.session_state.players:
        col1, col2 = st.columns([3, 1])
        p['Name'] = col1.text_input(f"Player", value=p['Name'], key=f"n_{p['Name']}")
        p['Active'] = col2.checkbox("Playing", value=p['Active'], key=f"act_{p['Name']}")

# --- PAGE 2: WHITEBOARD PLAN ---
elif page == "🖍 Whiteboard Plan":
    st.header("Step 2: Set the Tone")
    st.info("Assign players to Cells (A/B/C) and Rotation Groups (1-5).")
    
    # 1. Starting Bench Selector
    st.session_state.start_grp = st.pills("Which Group starts on the bench?", [1, 2, 3, 4, 5], default=1)
    
    # 2. Line Movement
    st.subheader("Quarterly Line Moves")
    for q in [1, 2, 3, 4]:
        with st.expander(f"Quarter {q} Plan"):
            c1, c2, c3 = st.columns(3)
            st.session_state.cell_plan[q]["A"] = c1.selectbox(f"Cell A", ["Back", "Mid", "Forward"], index=0, key=f"ca{q}")
            st.session_state.cell_plan[q]["B"] = c2.selectbox(f"Cell B", ["Back", "Mid", "Forward"], index=1, key=f"cb{q}")
            st.session_state.cell_plan[q]["C"] = c3.selectbox(f"Cell C", ["Back", "Mid", "Forward"], index=2, key=f"cc{q}")

    # 3. Cell Assignment
    st.subheader("Cell & Group Assignment")
    for p in st.session_state.players:
        if p['Active']:
            with st.expander(f"Assign {p['Name']}"):
                p['Cell'] = st.selectbox("Cell", ["A", "B", "C"], index=["A", "B", "C"].index(p['Cell']), key=f"c_{p['Name']}")
                p['Grp'] = st.selectbox("Group #", [1, 2, 3, 4, 5], index=p['Grp']-1, key=f"g_{p['Name']}")

# --- PAGE 3: LIVE OVAL ---
elif page == "🏟 LIVE OVAL":
    # Logic
    q_selected = st.pills("Quarter", [1, 2, 3, 4], default=1)
    timing = st.pills("Sub Timing", ["Starting Rotation", "Mid-Quarter Rotation"], default="Starting Rotation")
    
    # Rotation Index
    raw_phase = ((q_selected - 1) * 2) + (1 if timing == "Starting Rotation" else 2)
    start_offset = st.session_state.get('start_grp', 1) - 1
    group_seq = [1, 2, 3, 4, 5, 1, 2, 3]
    off_grp = group_seq[(raw_phase - 1 + start_offset) % 5]
    next_off_grp = group_seq[(raw_phase + start_offset) % 5]

    # Map names to zones
    for p in st.session_state.players:
        p['Zone'] = st.session_state.cell_plan[q_selected][p['Cell']]
    
    df = pd.DataFrame(st.session_state.players)
    df_active = df[df['Active'] == True]

    # Visual Oval
    st.markdown("""<style>.zone{border:2px solid #333; border-radius:20px; padding:10px; margin:5px; text-align:center; background:#f0f2f6;}</style>""", unsafe_allow_html=True)
    
    # FORWARDS
    st.markdown("<div class='zone'><strong>🟠 FORWARDS</strong></div>", unsafe_allow_html=True)
    f_on = df_active[(df_active['Zone'] == 'Forward') & (df_active['Grp'] != off_grp)]
    st.columns(len(f_on) if not f_on.empty else 1)[0].write(" ".join([f"**{p['Name']}** [G{p['Grp']}]" for _, p in f_on.iterrows()]))

    # MIDS
    st.markdown("<div class='zone'><strong>🟢 MIDFIELD</strong></div>", unsafe_allow_html=True)
    m_on = df_active[(df_active['Zone'] == 'Mid') & (df_active['Grp'] != off_grp)]
    st.columns(len(m_on) if not m_on.empty else 1)[0].write(" ".join([f"**{p['Name']}** [G{p['Grp']}]" for _, p in m_on.iterrows()]))

    # BACKS
    st.markdown("<div class='zone'><strong>🔵 BACKS</strong></div>", unsafe_allow_html=True)
    b_on = df_active[(df_active['Zone'] == 'Back') & (df_active['Grp'] != off_grp)]
    st.columns(len(b_on) if not b_on.empty else 1)[0].write(" ".join([f"**{p['Name']}** [G{p['Grp']}]" for _, p in b_on.iterrows()]))

    st.divider()
    # BENCH
    col_off, col_next = st.columns(2)
    with col_off:
        st.error("**OFF FIELD**")
        for _, p in df_active[df_active['Grp'] == off_grp].iterrows():
            st.write(f"{p['Name']} ({p['Zone']} Sub)")
    with col_next:
        st.warning("**NEXT SUB**")
        for _, p in df_active[df_active['Grp'] == next_off_grp].iterrows():
            st.write(f"{p['Name']} (Field) ↔ {df_active[(df_active['Cell']==p['Cell']) & (df_active['Grp']==off_grp)]['Name'].values[0]} (Bench)")
