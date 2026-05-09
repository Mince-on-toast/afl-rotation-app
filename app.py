import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AFL Rotation Pro", layout="wide")

# -------------------------------------------------
# SESSION STATE SETUP
# -------------------------------------------------
if "squad" not in st.session_state:
    st.session_state.squad = [
        "Joel", "Eli", "Jagger", "Max", "Josh",
        "Carmelo", "Buddy", "Jaxon F", "Harry", "Tyler",
        "Michael", "Ernest", "Leyton", "Jaxon J", "Xavier"
    ]

if "assignments" not in st.session_state:
    st.session_state.assignments = (
        [{"Name": "Select Player...", "Unit": "A", "Group": i % 5 + 1} for i in range(5)] +
        [{"Name": "Select Player...", "Unit": "B", "Group": i % 5 + 1} for i in range(5)] +
        [{"Name": "Select Player...", "Unit": "C", "Group": i % 5 + 1} for i in range(5)]
    )

if "line_plan" not in st.session_state:
    st.session_state.line_plan = {
        1: {"A": "Back", "B": "Mid", "C": "Forward"},
        2: {"A": "Forward", "B": "Back", "C": "Mid"},
        3: {"A": "Mid", "B": "Forward", "C": "Back"},
        4: {"A": "Back", "B": "Mid", "C": "Forward"},
    }

if "start_grp" not in st.session_state:
    st.session_state.start_grp = 1

if "prev_q" not in st.session_state:
    st.session_state.prev_q = 1

if "timing_choice" not in st.session_state:
    st.session_state.timing_choice = "Starting Rotation"

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["📋 Setup Squad", "🖍 Whiteboard Plan", "🏟 LIVE OVAL"]
)

# -------------------------------------------------
# PAGE 1 — SETUP SQUAD
# -------------------------------------------------
if page == "📋 Setup Squad":

    st.header("Step 1: Squad Names")

    for i in range(15):
        st.session_state.squad[i] = st.text_input(
            f"Player {i+1}",
            value=st.session_state.squad[i],
            key=f"squad_{i}"
        )

# -------------------------------------------------
# PAGE 2 — WHITEBOARD PLAN
# -------------------------------------------------
elif page == "🖍 Whiteboard Plan":

    st.header("Step 2: Set the Tone")

    st.session_state.start_grp = st.radio(
        "Which Group starts on the bench?",
        [1, 2, 3, 4, 5],
        horizontal=True,
        index=0
    )

    # -------------------------------------------------
    # STYLES
    # -------------------------------------------------
    st.markdown("""
    <style>
    .unit-box {
        border: 3px solid #333;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .back-box {
        border-color: #1565C0;
        background-color: #E3F2FD;
    }

    .mid-box {
        border-color: #2E7D32;
        background-color: #E8F5E9;
    }

    .fwd-box {
        border-color: #EF6C00;
        background-color: #FFF3E0;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)

    unit_data = [
        ("A", "Unit A (Backline)", "back-box"),
        ("B", "Unit B (Midfield)", "mid-box"),
        ("C", "Unit C (Forward Line)", "fwd-box")
    ]

    for col, (unit_id, label, css_class) in zip(cols, unit_data):

        with col:

            st.markdown(
                f"""
                <div class="unit-box {css_class}">
                <h3>{label}</h3>
                """,
                unsafe_allow_html=True
            )

            for i in range(len(st.session_state.assignments)):

                assignment = st.session_state.assignments[i]

                if assignment["Unit"] == unit_id:

                    options = ["Select Player..."] + sorted(st.session_state.squad)

                    current_name = assignment["Name"]

                    current_index = (
                        options.index(current_name)
                        if current_name in options
                        else 0
                    )

                    selected = st.selectbox(
                        f"Group {assignment['Group']}",
                        options,
                        index=current_index,
                        key=f"player_select_{i}"
                    )

                    st.session_state.assignments[i]["Name"] = selected

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # DUPLICATE CHECK
    # -------------------------------------------------
    selected_players = [
        p["Name"]
        for p in st.session_state.assignments
        if p["Name"] != "Select Player..."
    ]

    duplicates = sorted(
        set(
            name
            for name in selected_players
            if selected_players.count(name) > 1
        )
    )

    if duplicates:
        st.error(f"Duplicate players selected: {', '.join(duplicates)}")
    else:
        st.success("No duplicate players detected.")

    # -------------------------------------------------
    # TACTICAL PLAN
    # -------------------------------------------------
    with st.expander("🔄 Tactical Line Moves (By Unit)", expanded=True):

        zones = ["Back", "Mid", "Forward"]

        for q in [1, 2, 3, 4]:

            st.subheader(f"Quarter {q}")

            c1, c2, c3 = st.columns(3)

            st.session_state.line_plan[q]["A"] = c1.selectbox(
                f"Unit A",
                zones,
                index=zones.index(st.session_state.line_plan[q]["A"]),
                key=f"qa_{q}"
            )

            st.session_state.line_plan[q]["B"] = c2.selectbox(
                f"Unit B",
                zones,
                index=zones.index(st.session_state.line_plan[q]["B"]),
                key=f"qb_{q}"
            )

            st.session_state.line_plan[q]["C"] = c3.selectbox(
                f"Unit C",
                zones,
                index=zones.index(st.session_state.line_plan[q]["C"]),
                key=f"qc_{q}"
            )

# -------------------------------------------------
# PAGE 3 — LIVE OVAL
# -------------------------------------------------
elif page == "🏟 LIVE OVAL":

    st.header("LIVE GAME VIEW")

    quarter = st.radio(
        "Quarter",
        [1, 2, 3, 4],
        horizontal=True,
        index=0
    )

    # Reset timing if quarter changes
    if quarter != st.session_state.prev_q:
        st.session_state.timing_choice = "Starting Rotation"
        st.session_state.prev_q = quarter
        st.rerun()

    timing = st.radio(
        "Rotation Timing",
        ["Starting Rotation", "Mid-Quarter Rotation"],
        horizontal=True,
        key="timing_choice"
    )

    # -------------------------------------------------
    # ROTATION LOGIC
    # -------------------------------------------------
    phase = ((quarter - 1) * 2) + (
        1 if timing == "Starting Rotation" else 2
    )

    start_offset = st.session_state.start_grp - 1

    group_sequence = [1, 2, 3, 4, 5, 1, 2, 3]

    off_group = group_sequence[(phase - 1 + start_offset) % 5]

    next_off_group = group_sequence[(phase + start_offset) % 5]

    # -------------------------------------------------
    # DATAFRAME
    # -------------------------------------------------
    df = pd.DataFrame(st.session_state.assignments)

    df["Zone"] = df["Unit"].map(
        lambda u: st.session_state.line_plan[quarter][u]
    )

    df_ready = df[df["Name"] != "Select Player..."]

    # -------------------------------------------------
    # OVAL STYLES
    # -------------------------------------------------
    st.markdown("""
    <style>

    .zone {
        border: 2px solid #333;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        background: #f0f2f6;
        text-align: center;
    }

    .player {
        display: block;
        padding: 8px;
        margin: 4px;
        background: white;
        border-radius: 5px;
        border-left: 8px solid #1F4E78;
        font-weight: bold;
        font-size: 1.05em;
    }

    </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------
    # DISPLAY ZONES
    # -------------------------------------------------
    zone_layout = [
        ("Forward", "🟠", "FORWARDS"),
        ("Mid", "🟢", "MIDFIELD"),
        ("Back", "🔵", "BACKS")
    ]

    for zone, emoji, label in zone_layout:

        st.markdown(
            f"<div class='zone'>{emoji} <strong>{label}</strong></div>",
            unsafe_allow_html=True
        )

        zone_players = df_ready[
            (df_ready["Zone"] == zone) &
            (df_ready["Group"] != off_group)
        ]

        for _, player in zone_players.iterrows():

            st.markdown(
                f"<div class='player'>{player['Name']} [G{player['Group']}]</div>",
                unsafe_allow_html=True
            )

    # -------------------------------------------------
    # BENCH + UPCOMING SWAPS
    # -------------------------------------------------
    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.error("OFF FIELD")

        off_players = df_ready[df_ready["Group"] == off_group]

        for _, p in off_players.iterrows():
            st.write(f"❌ {p['Name']} ({p['Zone']})")

    with col2:

        st.warning("UPCOMING SWAP")

        upcoming = df_ready[df_ready["Group"] == next_off_group]

        for _, off_p in upcoming.iterrows():

            on_p = df_ready[
                (df_ready["Unit"] == off_p["Unit"]) &
                (df_ready["Group"] == off_group)
            ]

            on_name = (
                on_p["Name"].values[0]
                if not on_p.empty
                else "No Sub"
            )

            st.write(f"**{off_p['Name']}** ↔ **{on_name}**")
