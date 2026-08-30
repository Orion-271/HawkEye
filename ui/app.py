import streamlit as st
import pandas as pd
import numpy as np
import folium
import json
import os
from datetime import datetime

from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Disaster-Resilient Infrastructure Assessment",
    page_icon="◆",
    layout="wide"
)


# ============================================================
# GLOBAL STYLE (operational / command-center dashboard look)
# ============================================================

st.markdown(
    """
    <style>

    :root {
        --accent: #1e3a5f;
        --accent-dark: #14293f;
        --danger: #dc2626;
        --warn: #d97706;
        --ok: #16a34a;
        --info: #2563eb;
        --border: #e2e4e9;
        --border-strong: #d1d5db;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --surface: #ffffff;
        --app-bg: #f5f6f8;
        --sidebar-bg: #fafafa;
    }

    /* Application background */
    .stApp {
        background: var(--app-bg);
    }
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1440px;
    }

    /* Bordered containers: flat, thin border, minimal radius, no shadow */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        box-shadow: none !important;
        background: var(--surface) !important;
    }

    /* Buttons: restrained, small radius */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid var(--border-strong);
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.35rem 0.7rem;
        box-shadow: none;
        background: #ffffff;
        color: #27272a;
    }
    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
        box-shadow: none;
    }
    .stButton > button:active {
        transform: none;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        border-radius: 6px !important;
        border-color: var(--border-strong) !important;
        box-shadow: none !important;
    }

    /* Slider: neutral gray track, single restrained accent handle */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(30,58,95,0.12) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        background: var(--accent) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child {
        background: #e5e7eb !important;
    }
    div[data-testid="stTickBar"] { display: none; }
    div[data-testid="stSlider"] label p {
        font-size: 0.8rem !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* Metric styling: restrained hierarchy */
    div[data-testid="stMetric"] {
        background: transparent;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.68rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    h1 {
        font-size: 1.55rem !important;
        font-weight: 650 !important;
        color: #0f172a;
        letter-spacing: -0.01em;
    }
    h2 {
        font-size: 1.15rem !important;
        font-weight: 650 !important;
        color: #1f2937;
    }
    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #1f2937;
    }
    p, .stCaption, div[data-testid="stCaptionContainer"] {
        color: var(--text-secondary);
    }

    /* Section eyebrow labels */
    .section-eyebrow {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 2px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        box-shadow: none;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    .sidebar-group-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #6b7280;
        margin: 4px 0 2px 0;
    }
    .sidebar-group-caption {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-bottom: 10px;
    }

    /* Stats bar: flat white strip, thin border, no accent top bar */
    .st-key-stats_bar,
    .st-key-response_overview_bar,
    .st-key-priority_distribution_bar {
        background: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.9rem 1.1rem !important;
        box-shadow: none !important;
    }

    /* Damage-tinted detail cards: subtle left border + very pale tint */
    .st-key-card_destroyed { background: #fdf5f5 !important; border: 1px solid #f1dede !important; border-left: 3px solid var(--danger) !important; }
    .st-key-card_major     { background: #fdf8f0 !important; border: 1px solid #f0e3cc !important; border-left: 3px solid var(--warn) !important; }
    .st-key-card_minor     { background: #f3f7fb !important; border: 1px solid #d9e5f0 !important; border-left: 3px solid var(--info) !important; }
    .st-key-card_none      { background: #f3f9f4 !important; border: 1px solid #d7ead9 !important; border-left: 3px solid var(--ok) !important; }
    .st-key-card_unknown   { background: #f8f8f9 !important; border: 1px solid var(--border) !important; border-left: 3px solid #9ca3af !important; }

    .tag-critical {
        display:inline-flex;
        align-items:center;
        gap:4px;
        background: #fdeaea;
        color: var(--danger);
        border:1px solid #f3c6c6;
        padding:2px 8px;
        border-radius:4px;
        font-size:0.68rem;
        font-weight:700;
        letter-spacing: 0.03em;
        box-shadow: none;
    }

    /* Folium map + dataframes: minimal radius, thin border, no shadow */
    div[data-testid="stCustomComponentV1"],
    div[data-testid="stIFrame"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: none !important;
        border: 1px solid var(--border) !important;
    }
    div[data-testid="stCustomComponentV1"] iframe,
    div[data-testid="stIFrame"] iframe {
        border-radius: 8px !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 6px !important;
        overflow: hidden !important;
        box-shadow: none !important;
        border: 1px solid var(--border);
    }

    div[data-testid="stAlert"] {
        border-radius: 6px !important;
        box-shadow: none !important;
        border: 1px solid var(--border) !important;
    }

    div[data-testid="stProgress"] > div > div > div {
        background-color: var(--accent) !important;
        border-radius: 4px !important;
    }
    div[data-testid="stProgress"] > div > div {
        border-radius: 4px !important;
        background-color: #e5e7eb !important;
    }

    hr {
        margin: 1.5rem 0 !important;
        border-color: var(--border) !important;
    }

    /* Compact operational team status cards */
    .team-card {
        border: 1px solid var(--border);
        border-radius: 6px;
        background: #ffffff;
        padding: 10px 12px;
        min-height: 62px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 4px;
    }
    .team-card .team-name {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .team-card .team-status {
        font-size: 0.76rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .dot { display:inline-block; width:7px; height:7px; border-radius:50%; }
    .dot-green { background: var(--ok); }
    .dot-orange { background: var(--warn); }
    .dot-red { background: var(--danger); }
    .dot-gray { background: #9ca3af; }
    .dot-blue { background: var(--info); }

    /* Restrained stat strip cells (Emergency Response Overview / Priority Distribution) */
    .flat-metric-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
        display:flex;
        align-items:center;
        gap:6px;
    }
    .flat-metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

POPULATION_FILE = os.path.join(
    BASE_DIR,
    "population_module",
    "enriched_buildings.json"
)


# ============================================================
# LOAD BUILDING DATA
# ============================================================

@st.cache_data
def load_buildings():

    if not os.path.exists(POPULATION_FILE):
        return pd.DataFrame()

    try:

        with open(
            POPULATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)

    except Exception as error:

        st.error(
            f"Could not read enriched_buildings.json: {error}"
        )

        return pd.DataFrame()


raw_df = load_buildings()


# ============================================================
# CHECK DATA
# ============================================================

if raw_df.empty:

    st.error(
        "No building data found."
    )

    st.info(
        "Make sure population_module/enriched_buildings.json exists."
    )

    st.stop()


df = raw_df.copy()


# ============================================================
# BUILDING ID
# ============================================================

if "id" not in df.columns:

    df["id"] = [
        f"B{i:03d}"
        for i in range(
            1,
            len(df) + 1
        )
    ]

else:

    df["id"] = df["id"].astype(str)


# ============================================================
# GPS
# ============================================================

if (
    "latitude" not in df.columns
    or
    "longitude" not in df.columns
):

    st.error(
        "Latitude/longitude are missing from enriched_buildings.json."
    )

    st.stop()

df["lat"] = pd.to_numeric(

    df["latitude"],
    errors="coerce"
)

df["lon"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)


# ============================================================
# AREA
# ============================================================

if "area_m2" in df.columns:

    df["area"] = pd.to_numeric(
        df["area_m2"],
        errors="coerce"
    )

elif "area" in df.columns:

    df["area"] = pd.to_numeric(
        df["area"],
        errors="coerce"
    )

else:

    df["area"] = 0.0


df["area"] = df["area"].fillna(0)


# ============================================================
# POPULATION DENSITY
# ============================================================

if "population_density" in df.columns:

    df["population_density"] = pd.to_numeric(
        df["population_density"],
        errors="coerce"
    ).fillna(0)

else:

    df["population_density"] = 0.0


# ============================================================
# ESTIMATED POPULATION
# ============================================================

if "estimated_population" in df.columns:

    df["estimated_population"] = pd.to_numeric(
        df["estimated_population"],
        errors="coerce"
    ).fillna(0)

else:

    df["estimated_population"] = 0.0


# ============================================================
# DAMAGE
# ============================================================

if "damage" not in df.columns:

    if "damage_level" in df.columns:

        df["damage"] = df["damage_level"]

    else:

        df["damage"] = "Unknown"


def normalize_damage(value):

    value = str(value).strip().lower()

    if "destroy" in value:
        return "Destroyed"

    if "major" in value:
        return "Major"

    if "minor" in value:
        return "Minor"

    if "no damage" in value:
        return "No Damage"

    if value in [
        "none",
        "safe"
    ]:
        return "No Damage"

    return "Unknown"


df["damage_level"] = (
    df["damage"]
    .apply(normalize_damage)
)


# ============================================================
# BUILDING TYPE
# ============================================================

if "building_type" not in df.columns:

    df["building_type"] = "Residential"

else:

    df["building_type"] = (
        df["building_type"]
        .fillna("Residential")
        .astype(str)
    )


# ============================================================
# ROAD REDUNDANCY
# ============================================================

if "road_redundancy" not in df.columns:

    df["road_redundancy"] = 0.5

else:

    df["road_redundancy"] = pd.to_numeric(
        df["road_redundancy"],
        errors="coerce"
    ).fillna(0.5)


# ============================================================
# REMOVE INVALID GPS
# ============================================================

df = df.dropna(
    subset=[
        "lat",
        "lon"
    ]
).reset_index(
    drop=True
)


# ============================================================
# DAMAGE WEIGHTS
# ============================================================

DAMAGE_WEIGHT = {

    "No Damage": 0.0,

    "Minor": 0.3,

    "Major": 0.7,

    "Destroyed": 1.0,

    "Unknown": 0.0

}


# ============================================================
# CRITICALITY WEIGHTS
# ============================================================

CRITICALITY_WEIGHT = {

    "Hospital": 1.0,

    "School": 0.8,

    "Government": 0.7,

    "Commercial": 0.4,

    "Residential": 0.3

}


# ============================================================
# PRIORITY LEVELS
# ============================================================

def get_priority_level(score):

    if score >= 0.70:
        return "CRITICAL"

    elif score >= 0.50:
        return "HIGH"

    elif score >= 0.30:
        return "MEDIUM"

    else:
        return "LOW"


# Small monochrome-friendly colored dot per priority level (used instead
# of emoji throughout the UI).
PRIORITY_DOT = {

    "CRITICAL": "dot-red",

    "HIGH": "dot-orange",

    "MEDIUM": "#d4a017",  # handled inline where needed

    "LOW": "dot-green"

}

PRIORITY_TEXT_COLOR = {

    "CRITICAL": "#dc2626",

    "HIGH": "#d97706",

    "MEDIUM": "#b8860b",

    "LOW": "#16a34a",

}


# ============================================================
# INSPECTION STATUS
# ============================================================

STATUS_NOT_ASSIGNED = "Not Assigned"

STATUS_WAITING = "Waiting for Team"

STATUS_IN_PROGRESS = "Inspection Ongoing"

STATUS_DONE_SAFE = "Completed - Safe"

STATUS_DONE_UNSAFE = "Completed - Unsafe"


STATUS_OPTIONS = [

    STATUS_NOT_ASSIGNED,

    STATUS_WAITING,

    STATUS_IN_PROGRESS,

    STATUS_DONE_SAFE,

    STATUS_DONE_UNSAFE

]


STATUS_DOT = {

    STATUS_NOT_ASSIGNED: "dot-gray",

    STATUS_WAITING: "dot-orange",

    STATUS_IN_PROGRESS: "dot-blue",

    STATUS_DONE_SAFE: "dot-green",

    STATUS_DONE_UNSAFE: "dot-red"

}


# ============================================================
# INSPECTION TEAMS
# ============================================================

INSPECTION_TEAMS = [

    "Team 01",

    "Team 02",

    "Team 03",

    "Team 04",

    "Team 05"

]


# ============================================================
# SESSION STATE
# ============================================================

if "selected_id" not in st.session_state:

    st.session_state.selected_id = None


if "inspection_queue" not in st.session_state:

    st.session_state.inspection_queue = []


# ============================================================
# STATE HELPERS
# ============================================================

def status_key(building_id):

    return (
        "status_"
        +
        str(building_id)
    )


def team_key(building_id):

    return (
        "team_"
        +
        str(building_id)
    )


def time_key(building_id):

    return (
        "time_"
        +
        str(building_id)
    )


def get_status(building_id):

    return st.session_state.get(

        status_key(building_id),

        STATUS_NOT_ASSIGNED

    )


def get_team(building_id):

    return st.session_state.get(

        team_key(building_id),

        None

    )


def get_time(building_id):

    return st.session_state.get(

        time_key(building_id),

        ""

    )


# ============================================================
# TEAM MANAGEMENT
# ============================================================

def get_busy_teams():

    busy = set()

    for building_id in df["id"]:

        status = get_status(
            building_id
        )

        team = get_team(
            building_id
        )

        if (

            team is not None

            and

            status == STATUS_IN_PROGRESS

        ):

            busy.add(team)


    return busy


def get_available_teams():

    busy = get_busy_teams()

    return [

        team

        for team in INSPECTION_TEAMS

        if team not in busy

    ]


def add_to_queue(building_id):

    building_id = str(
        building_id
    )


    if building_id not in st.session_state.inspection_queue:

        st.session_state.inspection_queue.append(
            building_id
        )


    st.session_state[
        status_key(building_id)
    ] = STATUS_WAITING


    st.session_state[
        team_key(building_id)
    ] = None


def assign_team_to_building(
    building_id,
    selected_team
):

    building_id = str(
        building_id
    )


    available_teams = get_available_teams()


    # --------------------------------------------------------
    # TEAM IS AVAILABLE
    # --------------------------------------------------------

    if (

        selected_team in available_teams

    ):

        st.session_state[
            team_key(building_id)
        ] = selected_team


        st.session_state[
            status_key(building_id)
        ] = STATUS_IN_PROGRESS


        st.session_state[
            time_key(building_id)
        ] = datetime.now().strftime(
            "%I:%M %p"
        )


        # Remove from waiting queue

        if building_id in st.session_state.inspection_queue:

            st.session_state.inspection_queue.remove(
                building_id
            )


    # --------------------------------------------------------
    # TEAM IS NOT AVAILABLE
    # --------------------------------------------------------

    else:

        add_to_queue(
            building_id
        )


def complete_inspection(
    building_id,
    result
):

    building_id = str(
        building_id
    )


    old_team = get_team(
        building_id
    )


    # --------------------------------------------------------
    # COMPLETE CURRENT BUILDING
    # --------------------------------------------------------

    st.session_state[
        status_key(building_id)
    ] = result


    # Team is no longer actively assigned

    st.session_state[
        team_key(building_id)
    ] = old_team


    # --------------------------------------------------------
    # FIND NEXT WAITING BUILDING
    # --------------------------------------------------------

    next_building = None


    for queued_id in list(
        st.session_state.inspection_queue
    ):

        if get_status(
            queued_id
        ) == STATUS_WAITING:

            next_building = queued_id

            break


    # --------------------------------------------------------
    # AUTOMATICALLY ASSIGN FREED TEAM
    # --------------------------------------------------------

    if (

        old_team is not None

        and

        next_building is not None

    ):

        st.session_state[
            team_key(next_building)
        ] = old_team


        st.session_state[
            status_key(next_building)
        ] = STATUS_IN_PROGRESS


        st.session_state[
            time_key(next_building)
        ] = datetime.now().strftime(
            "%I:%M %p"
        )


        st.session_state.inspection_queue.remove(
            next_building
        )


def clear_selection():

    st.session_state.selected_id = None


def select_building(
    building_id
):

    st.session_state.selected_id = str(
        building_id
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Infrastructure Assessment"
)

st.sidebar.markdown(
    '<div class="sidebar-group-title">Priority Model</div>'
    '<div class="sidebar-group-caption">Adjust factors used to calculate inspection priority.</div>',
    unsafe_allow_html=True
)


w_severity = st.sidebar.slider(

    "Damage Severity",

    0.0,
    1.0,

    0.4,

    0.05

)


w_population = st.sidebar.slider(

    "Population Exposure",

    0.0,
    1.0,

    0.3,

    0.05

)


w_criticality = st.sidebar.slider(

    "Infrastructure Criticality",

    0.0,
    1.0,

    0.2,

    0.05

)


w_redundancy = st.sidebar.slider(

    "Access Redundancy Risk",

    0.0,
    1.0,

    0.1,

    0.05

)


st.sidebar.markdown("---")


st.sidebar.markdown(
    '<div class="sidebar-group-title">Map Display</div>',
    unsafe_allow_html=True
)


grid_size_m = st.sidebar.selectbox(

    "Grid cell size",

    options=[
        50,
        100,
        250
    ],

    index=1,

    format_func=lambda value:
        f"{value} m"

)


show_grid = st.sidebar.checkbox(

    "Show grid overlay",

    value=True

)


building_box_size_m = st.sidebar.slider(

    "Marker size",

    min_value=3,

    max_value=30,

    value=8,

    step=1

)


st.sidebar.markdown("---")


st.sidebar.markdown(
    '<div class="sidebar-group-title">Filters</div>',
    unsafe_allow_html=True
)


available_damage = [

    damage

    for damage in [
        "No Damage",
        "Minor",
        "Major",
        "Destroyed",
        "Unknown"
    ]

    if damage in
    df["damage_level"].unique()

]


damage_filter = st.sidebar.multiselect(

    "Damage Level",

    options=available_damage,

    default=available_damage

)


available_types = sorted(
    df["building_type"]
    .dropna()
    .unique()
    .tolist()
)


type_filter = st.sidebar.multiselect(

    "Building Type",

    options=available_types,

    default=available_types

)


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def compute_priority(

    row,

    w_severity,

    w_population,

    w_criticality,

    w_redundancy

):

    severity = DAMAGE_WEIGHT.get(

        row["damage_level"],

        0.0

    )


    population_exposure = min(

        float(
            row["estimated_population"]
        )
        /
        20.0,

        1.0

    )


    criticality = CRITICALITY_WEIGHT.get(

        row["building_type"],

        0.3

    )


    redundancy_risk = (

        1.0

        -

        float(
            row["road_redundancy"]
        )

    )


    raw_score = (

        w_severity *
        severity

        +

        w_population *
        population_exposure

        +

        w_criticality *
        criticality

        +

        w_redundancy *
        redundancy_risk

    )


    total_weight = (

        w_severity

        +

        w_population

        +

        w_criticality

        +

        w_redundancy

    )


    if total_weight > 0:

        score = (
            raw_score
            /
            total_weight
        )

    else:

        score = 0


    return round(
        score,
        3
    )


df["priority_score"] = df.apply(

    lambda row:

        compute_priority(

            row,

            w_severity,

            w_population,

            w_criticality,

            w_redundancy

        ),

    axis=1

)


df["priority_level"] = (

    df["priority_score"]

    .apply(
        get_priority_level
    )

)


# ============================================================
# FILTER
# ============================================================

filtered = df[

    df["damage_level"].isin(
        damage_filter
    )

    &

    df["building_type"].isin(
        type_filter
    )

].sort_values(

    [
        "priority_score",
        "estimated_population"
    ],

    ascending=False

).reset_index(
    drop=True
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "AI-Powered Disaster-Resilient Infrastructure Assessment"
)

st.caption(
    "AI-assisted infrastructure damage detection, "
    "population exposure estimation and emergency inspection prioritization."
)


st.markdown(
    f"""
    <div style="
        background:#f3f9f4;
        border:1px solid #d7ead9;
        border-radius:6px;
        padding:8px 14px;
        font-size:0.82rem;
        color:#1f2937;
        margin-bottom:14px;
    ">
        <span style="color:#16a34a; font-weight:700;">&#10003;</span>
        &nbsp;Real building data connected &mdash; {len(df)} georeferenced buildings with WorldPop population estimates
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TOP METRICS
# ============================================================

STAT_COLORS = {

    "neutral": "#111827",

    "danger": "#dc2626",

    "warn": "#d97706",

    "accent": "#1e3a5f",

}


def render_stat(label, value, color_key="neutral"):

    color = STAT_COLORS.get(color_key, STAT_COLORS["neutral"])

    st.markdown(
        f"""
        <div style="line-height:1.25;">
            <div class="flat-metric-label">{label}</div>
            <div class="flat-metric-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with st.container(border=True, key="stats_bar"):

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        render_stat(
            "Sites Analyzed",
            len(df),
            "neutral"
        )


    with col2:

        render_stat(

            "Critical Sites",

            int(

                (
                    df["priority_level"]
                    ==
                    "CRITICAL"
                ).sum()

            ),

            "danger"

        )


    with col3:

        render_stat(

            "Destroyed",

            int(

                (
                    df["damage_level"]
                    ==
                    "Destroyed"
                ).sum()

            ),

            "danger"

        )


    with col4:

        render_stat(

            "Major Damage",

            int(

                (
                    df["damage_level"]
                    ==
                    "Major"
                ).sum()

            ),

            "warn"

        )


    with col5:

        total_exposure = int(

            round(

                df[
                    "estimated_population"
                ].sum()

            )

        )


        render_stat(

            "People Affected",

            f"{total_exposure:,}",

            "accent"

        )


st.markdown("")


# ============================================================
# MAP HELPERS
# ============================================================

def build_grid(

    df_points,

    cell_size_m

):

    if df_points.empty:

        return []


    lat_deg_per_m = (
        1 / 111320.0
    )


    avg_lat = (
        df_points["lat"].mean()
    )


    lon_deg_per_m = (

        1

        /

        (

            111320.0

            *

            np.cos(
                np.radians(
                    avg_lat
                )
            )

        )

    )


    cell_h = (
        cell_size_m
        *
        lat_deg_per_m
    )


    cell_w = (
        cell_size_m
        *
        lon_deg_per_m
    )


    lat_min = (
        df_points["lat"].min()
    )

    lat_max = (
        df_points["lat"].max()
    )

    lon_min = (
        df_points["lon"].min()
    )

    lon_max = (
        df_points["lon"].max()
    )


    lat_min -= cell_h
    lat_max += cell_h

    lon_min -= cell_w
    lon_max += cell_w


    n_rows = int(

        np.ceil(

            (
                lat_max
                -
                lat_min
            )
            /
            cell_h

        )

    )


    n_cols = int(

        np.ceil(

            (
                lon_max
                -
                lon_min
            )
            /
            cell_w

        )

    )


    cells = []


    for r in range(
        n_rows
    ):

        for c in range(
            n_cols
        ):

            cell_lat_min = (

                lat_min
                +
                r * cell_h

            )


            cell_lat_max = (

                cell_lat_min
                +
                cell_h

            )


            cell_lon_min = (

                lon_min
                +
                c * cell_w

            )


            cell_lon_max = (

                cell_lon_min
                +
                cell_w

            )


            mask = (

                (
                    df_points["lat"]
                    >=
                    cell_lat_min
                )

                &

                (
                    df_points["lat"]
                    <
                    cell_lat_max
                )

                &

                (
                    df_points["lon"]
                    >=
                    cell_lon_min
                )

                &

                (
                    df_points["lon"]
                    <
                    cell_lon_max
                )

            )


            cell_buildings = (
                df_points[mask]
            )


            if cell_buildings.empty:

                continue


            avg_severity = (

                cell_buildings[
                    "damage_level"
                ]

                .map(
                    DAMAGE_WEIGHT
                )

                .fillna(0)

                .mean()

            )


            cells.append({

                "bounds": [

                    [
                        cell_lat_min,
                        cell_lon_min
                    ],

                    [
                        cell_lat_max,
                        cell_lon_max
                    ]

                ],

                "avg_severity":

                    round(
                        avg_severity,
                        3
                    ),

                "building_count":

                    len(
                        cell_buildings
                    )

            })


    return cells


def severity_to_color(
    severity
):

    if severity < 0.15:

        return "#2ecc71"

    elif severity < 0.4:

        return "#f1c40f"

    elif severity < 0.7:

        return "#e67e22"

    else:

        return "#e74c3c"


def building_box_bounds(

    lat,

    lon,

    size_m

):

    lat_deg_per_m = (
        1 / 111320.0
    )


    lon_deg_per_m = (

        1

        /

        (

            111320.0

            *

            np.cos(
                np.radians(lat)
            )

        )

    )


    half_h = (
        size_m / 2
    ) * lat_deg_per_m


    half_w = (
        size_m / 2
    ) * lon_deg_per_m


    return [

        [
            lat - half_h,
            lon - half_w
        ],

        [
            lat + half_h,
            lon + half_w
        ]

    ]


DAMAGE_COLOR = {

    "No Damage": "green",

    "Minor": "blue",

    "Major": "orange",

    "Destroyed": "red",

    "Unknown": "gray"

}


# Very light tint pairs (background, border) matching each map-marker color,
# used for the inspection queue cards and the site-detail panel.
DAMAGE_TINT = {

    "Destroyed":  {"bg": "#fdf5f5", "border": "#f1dede"},

    "Major":      {"bg": "#fdf8f0", "border": "#f0e3cc"},

    "Minor":      {"bg": "#f3f7fb", "border": "#d9e5f0"},

    "No Damage":  {"bg": "#f3f9f4", "border": "#d7ead9"},

    "Unknown":    {"bg": "#f8f8f9", "border": "#e4e4e7"},

}


def inject_card_tint(unique_key, damage_level):
    """Injects a small CSS rule tinting the bordered container with the
    given Streamlit `key` so it matches the map-marker color for that
    damage level, via a subtle background tint and a colored left border."""

    tint = DAMAGE_TINT.get(
        damage_level,
        DAMAGE_TINT["Unknown"]
    )

    st.markdown(
        f"""
        <style>
        .st-key-{unique_key} {{
            background: {tint['bg']} !important;
            border: 1px solid {tint['border']} !important;
            border-radius: 6px !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAP + PRIORITY QUEUE
# ============================================================

map_col, list_col = st.columns(
    [2.1, 1]
)


# ============================================================
# MAP
# ============================================================

with map_col:

    st.subheader(
        "Infrastructure Damage Map"
    )

    st.caption(
        f"{len(filtered)} sites in view &middot; sorted by inspection priority",
        unsafe_allow_html=True
    )


    selected_row = None


    if (
        st.session_state.selected_id
        is not None
    ):

        selected_match = df[

            df["id"]
            ==
            str(
                st.session_state.selected_id
            )

        ]


        if not selected_match.empty:

            selected_row = (
                selected_match.iloc[0]
            )


    # --------------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------------

    if selected_row is not None:

        map_center = [

            selected_row["lat"],

            selected_row["lon"]

        ]

        zoom = 19

    else:

        map_center = [

            df["lat"].mean(),

            df["lon"].mean()

        ]

        zoom = 17


    m = folium.Map(

        location=map_center,

        zoom_start=zoom,

        tiles="CartoDB positron"

    )


    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    if show_grid:

        grid_cells = build_grid(

            df,

            grid_size_m

        )


        for cell in grid_cells:

            cell_color = (
                severity_to_color(
                    cell[
                        "avg_severity"
                    ]
                )
            )


            folium.Rectangle(

                bounds=cell[
                    "bounds"
                ],

                color=cell_color,

                weight=1,

                fill=True,

                fill_color=cell_color,

                fill_opacity=0.10,

                popup=folium.Popup(

                    (
                        "<b>Zone</b><br>"
                        "Buildings: "
                        +
                        str(
                            cell[
                                "building_count"
                            ]
                        )
                        +
                        "<br>"
                        "Average damage severity: "
                        +
                        str(
                            cell[
                                "avg_severity"
                            ]
                        )
                    ),

                    max_width=220

                )

            ).add_to(m)


    # --------------------------------------------------------
    # HIGHEST PRIORITY
    # --------------------------------------------------------

    highest_priority_id = None


    if not filtered.empty:

        highest_priority_id = str(

            filtered.iloc[0]["id"]

        )


    # --------------------------------------------------------
    # BUILDINGS
    # --------------------------------------------------------

    for _, row in filtered.iterrows():

        building_id = str(
            row["id"]
        )


        is_selected = (

            building_id
            ==
            str(
                st.session_state.selected_id
            )

        )


        current_status = get_status(
            building_id
        )


        current_team = get_team(
            building_id
        )


        assignment_time = get_time(
            building_id
        )


        priority_level = (
            row["priority_level"]
        )


        display_density = int(
            round(
                row[
                    "population_density"
                ]
            )
        )


        display_exposure = int(
            round(
                row[
                    "estimated_population"
                ]
            )
        )


        if current_team is None:

            team_text = "&mdash;"

        else:

            team_text = current_team


        if assignment_time:

            time_text = assignment_time

        else:

            time_text = "&mdash;"


        if priority_level == "CRITICAL":

            header_block = (
                '<div style="'
                'display:flex;align-items:center;gap:6px;'
                'background:#fdf2f2;border:1px solid #f3c6c6;'
                'border-radius:4px;padding:4px 8px;margin-bottom:8px;">'
                '<span style="color:#b42318;font-weight:700;font-size:11.5px;'
                'letter-spacing:0.03em;">&#9888; CRITICAL</span>'
                '</div>'
            )

        else:

            header_block = ""


        priority_color = PRIORITY_TEXT_COLOR.get(priority_level, "#3f3f46")


        popup_html = f"""

        <div style="
            font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
            font-size:12.5px;
            min-width:230px;
            color:#27272a;
        ">

            {header_block}

            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                margin-bottom:8px;
            ">

                <span style="font-weight:650; font-size:14px;">
                    {building_id}
                </span>

                <span style="color:{priority_color}; font-weight:700; font-size:11.5px; letter-spacing:0.03em;">
                    {priority_level} &middot; {row['damage_level'].upper()}
                </span>

            </div>

            <div style="color:#9ca3af; font-size:10.5px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:2px;">
                Priority Score
            </div>
            <div style="font-weight:700; font-size:15px; margin-bottom:8px;">
                {row['priority_score']:.3f}
            </div>

            <div style="color:#9ca3af; font-size:10.5px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:3px;">
                Site
            </div>
            <table style="width:100%; border-collapse:collapse; margin-bottom:8px;">

                <tr>
                    <td style="color:#71717a; padding:1.5px 0;">Building area</td>
                    <td style="text-align:right; font-weight:600;">{row['area']:.0f} m&sup2;</td>
                </tr>

                <tr>
                    <td style="color:#71717a; padding:1.5px 0;">Population density</td>
                    <td style="text-align:right;">{display_density:,}/km&sup2;</td>
                </tr>

                <tr>
                    <td style="color:#71717a; padding:1.5px 0;">People affected</td>
                    <td style="text-align:right; font-weight:600;">{display_exposure:,}</td>
                </tr>

            </table>

            <div style="color:#9ca3af; font-size:10.5px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:3px;">
                Inspection
            </div>
            <div style="font-weight:600; margin-bottom:2px;">
                {current_status}
            </div>
            <div style="color:#71717a; font-size:11.5px;">
                Team: {team_text} &nbsp;&middot;&nbsp; Assigned: {time_text}
            </div>

        </div>

        """


        damage_color = DAMAGE_COLOR.get(

            row["damage_level"],

            "gray"

        )


        # ----------------------------------------------------
        # INSPECTION BORDER
        # ----------------------------------------------------

        if current_status == STATUS_WAITING:

            border_color = "#d97706"

        elif current_status == STATUS_IN_PROGRESS:

            border_color = "#2563eb"

        elif current_status == STATUS_DONE_SAFE:

            border_color = "#16a34a"

        elif current_status == STATUS_DONE_UNSAFE:

            border_color = "#7c3aed"

        else:

            border_color = damage_color


        border_weight = 2


        if is_selected:

            border_color = "#dc2626"

            border_weight = 4


        # Marker radius in pixels, driven by the same sidebar control
        # that used to size the square marker's footprint in meters.
        marker_radius = max(
            4,
            min(
                18,
                building_box_size_m * 0.6
            )
        )

        if is_selected:

            marker_radius += 3


        folium.CircleMarker(

            location=[
                row["lat"],
                row["lon"]
            ],

            radius=marker_radius,

            color=border_color,

            weight=border_weight,

            fill=True,

            fill_color=damage_color,

            fill_opacity=0.88,

            popup=folium.Popup(

                popup_html,

                max_width=300,

                show=is_selected

            ),

            tooltip=(

                f"{building_id} &middot; "

                f"{priority_level}"

            )

        ).add_to(m)


        # ----------------------------------------------------
        # HIGHEST PRIORITY HIGHLIGHT
        # ----------------------------------------------------

        if (

            building_id
            ==
            highest_priority_id

            and

            not is_selected

        ):

            folium.CircleMarker(

                location=[
                    row["lat"],
                    row["lon"]
                ],

                radius=marker_radius + 6,

                color="#dc2626",

                weight=2,

                fill=False,

                opacity=0.8,

                dash_array="4"

            ).add_to(m)


    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    legend_css = """
        font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
        background: #ffffff;
        padding: 8px 10px;
        border: 1px solid #e2e4e9;
        border-radius: 6px;
        font-size: 11px;
        color: #27272a;
        line-height: 1.6;
        box-shadow: none;
    """

    legend_html = f"""

    <div style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 9999;
        display: flex;
        gap: 8px;
    ">

        <div style="{legend_css}">

            <div style="font-weight:700; margin-bottom:3px; font-size:10.5px; letter-spacing:0.04em; text-transform:uppercase; color:#6b7280;">Damage</div>

            <span style="color:#e74c3c;">&#9679;</span> Destroyed<br>
            <span style="color:#e67e22;">&#9679;</span> Major Damage<br>
            <span style="color:#3498db;">&#9679;</span> Minor Damage<br>
            <span style="color:#2ecc71;">&#9679;</span> No Damage

        </div>

        <div style="{legend_css}">

            <div style="font-weight:700; margin-bottom:3px; font-size:10.5px; letter-spacing:0.04em; text-transform:uppercase; color:#6b7280;">Inspection Status</div>

            <span style="color:#d97706;">&#9679;</span> Waiting for Team<br>
            <span style="color:#2563eb;">&#9679;</span> Inspection Ongoing<br>
            <span style="color:#16a34a;">&#9679;</span> Completed &ndash; Safe<br>
            <span style="color:#7c3aed;">&#9679;</span> Completed &ndash; Unsafe

        </div>

    </div>

    """


    m.get_root().html.add_child(
        folium.Element(
            legend_html
        )
    )


    map_polish_css = """
    <style>
    .leaflet-popup-content-wrapper {
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(16,24,40,0.06), 0 4px 10px rgba(16,24,40,0.08) !important;
        border: 1px solid #e2e4e9;
    }
    .leaflet-popup-tip {
        box-shadow: 0 1px 2px rgba(16,24,40,0.06) !important;
    }
    .leaflet-bar {
        border-radius: 6px !important;
        overflow: hidden;
        box-shadow: none !important;
        border: 1px solid #e2e4e9 !important;
    }
    .leaflet-bar a {
        border-radius: 0 !important;
    }
    </style>
    """

    m.get_root().html.add_child(
        folium.Element(
            map_polish_css
        )
    )


    map_data = st_folium(

        m,

        width=None,

        height=540,

        key="real_damage_map"

    )


    # --------------------------------------------------------
    # MAP CLICK
    # --------------------------------------------------------

    if map_data:

        clicked = map_data.get(
            "last_object_clicked"
        )


        if clicked:

            clicked_lat = clicked.get(
                "lat"
            )

            clicked_lon = clicked.get(
                "lng"
            )


            if (

                clicked_lat is not None

                and

                clicked_lon is not None

            ):

                distances = (

                    (
                        df["lat"]
                        -
                        clicked_lat
                    ) ** 2

                    +

                    (
                        df["lon"]
                        -
                        clicked_lon
                    ) ** 2

                )


                nearest_index = (
                    distances.idxmin()
                )


                nearest = df.loc[
                    nearest_index
                ]


                distance = np.sqrt(

                    distances.loc[
                        nearest_index
                    ]

                )


                if distance < 0.001:

                    if (

                        str(
                            st.session_state.selected_id
                        )

                        !=

                        str(
                            nearest["id"]
                        )

                    ):

                        st.session_state.selected_id = (

                            str(
                                nearest["id"]
                            )

                        )

                        st.rerun()


    st.caption(

        "Fill = damage severity &middot; Border = inspection status &middot; Dashed outline = highest priority",
        unsafe_allow_html=True

    )


# ============================================================
# PRIORITY QUEUE
# ============================================================

with list_col:

    st.subheader(
        "Inspection Queue"
    )


    st.caption(
        "Ranked by priority score, highest first."
    )


    with st.container(
        height=540
    ):

        for _, row in filtered.iterrows():

            building_id = str(
                row["id"]
            )


            is_selected = (

                building_id
                ==
                str(
                    st.session_state.selected_id
                )

            )


            priority_level = (
                row["priority_level"]
            )


            current_status = get_status(
                building_id
            )


            current_team = get_team(
                building_id
            )


            # ------------------------------------------------
            # INITIALIZE TEAM SELECTOR
            # ------------------------------------------------

            team_choice_key = (
                "team_choice_"
                +
                building_id
            )


            if team_choice_key not in st.session_state:

                st.session_state[
                    team_choice_key
                ] = "Team 01"


            # ------------------------------------------------
            # BUILDING VALUES
            # ------------------------------------------------

            display_density = int(

                round(

                    row[
                        "population_density"
                    ]

                )

            )


            display_exposure = int(

                round(

                    row[
                        "estimated_population"
                    ]

                )

            )


            card_key = "queue_card_" + building_id

            inject_card_tint(
                card_key,
                row["damage_level"]
            )

            with st.container(
                border=True,
                key=card_key
            ):

                priority_color = PRIORITY_TEXT_COLOR.get(priority_level, "#3f3f46")

                title_badge = (
                    '<span class="tag-critical">&#9888; CRITICAL</span>'
                    if priority_level == "CRITICAL"
                    else f'<span style="color:{priority_color}; font-weight:700; font-size:0.72rem; letter-spacing:0.03em;">{priority_level}</span>'
                )

                st.markdown(

                    f"**{building_id}**  &nbsp; {title_badge}",

                    unsafe_allow_html=True

                )


                st.caption(

                    f"{row['damage_level']}  &middot;  "
                    f"Score {row['priority_score']:.3f}",
                    unsafe_allow_html=True

                )


                st.progress(

                    min(

                        float(
                            row[
                                "priority_score"
                            ]
                        ),

                        1.0

                    )

                )


                # ------------------------------------------------
                # POPULATION
                # ------------------------------------------------

                pop_col1, pop_col2 = (
                    st.columns(2)
                )


                with pop_col1:

                    st.metric(

                        "Population Density",

                        f"{display_density:,}"

                    )


                with pop_col2:

                    st.metric(

                        "People Affected",

                        f"{display_exposure:,}"

                    )


                st.caption(

                    f"Building area: "
                    f"{row['area']:.0f} m&sup2;",
                    unsafe_allow_html=True

                )


                # =================================================
                # NOT ASSIGNED
                # =================================================

                if current_status == STATUS_NOT_ASSIGNED:

                    focus_col, team_col = (
                        st.columns(2)
                    )


                    with focus_col:

                        st.button(

                            "Focus on map"
                            if not is_selected
                            else "Focused",

                            key=(
                                "focus_"
                                +
                                building_id
                            ),

                            on_click=select_building,

                            args=(
                                building_id,
                            ),

                            use_container_width=True,

                            disabled=is_selected

                        )


                    with team_col:

                        available_teams = (
                            get_available_teams()
                        )


                        if available_teams:

                            st.selectbox(

                                "Choose Team",

                                options=available_teams,

                                key=team_choice_key,

                                label_visibility="collapsed"

                            )


                            st.button(

                                "Assign Team",

                                key=(
                                    "assign_"
                                    +
                                    building_id
                                ),

                                use_container_width=True,

                                on_click=assign_team_to_building,

                                args=(

                                    building_id,

                                    st.session_state[
                                        team_choice_key
                                    ]

                                )

                            )

                        else:

                            st.caption(

                                "All teams currently assigned."

                            )


                            st.button(

                                "Add to Queue",

                                key=(
                                    "queue_"
                                    +
                                    building_id
                                ),

                                use_container_width=True,

                                on_click=add_to_queue,

                                args=(
                                    building_id,
                                )

                            )


                # =================================================
                # WAITING
                # =================================================

                elif current_status == STATUS_WAITING:

                    st.markdown(
                        '<div style="display:flex;align-items:center;gap:6px;'
                        'font-size:0.82rem;font-weight:600;color:#92400e;margin-bottom:2px;">'
                        '<span class="dot dot-orange"></span>WAITING FOR TEAM</div>',
                        unsafe_allow_html=True
                    )


                    st.caption(

                        "All inspection teams are currently "
                        "busy. This site will be assigned "
                        "automatically when a team becomes available."

                    )


                    st.button(

                        "Focus on map"
                        if not is_selected
                        else "Focused",

                        key=(
                            "focus_wait_"
                            +
                            building_id
                        ),

                        on_click=select_building,

                        args=(
                            building_id,
                        ),

                        use_container_width=True,

                        disabled=is_selected

                    )


                # =================================================
                # INSPECTION ONGOING
                # =================================================

                elif current_status == STATUS_IN_PROGRESS:

                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:6px;'
                        f'font-size:0.82rem;font-weight:600;color:#1e40af;margin-bottom:2px;">'
                        f'<span class="dot dot-blue"></span>INSPECTION ONGOING &middot; {current_team}</div>',
                        unsafe_allow_html=True
                    )


                    if get_time(
                        building_id
                    ):

                        st.caption(

                            f"Assigned at "
                            f"{get_time(building_id)}"

                        )


                    st.button(

                        "Focus on map"
                        if not is_selected
                        else "Focused",

                        key=(
                            "focus_active_"
                            +
                            building_id
                        ),

                        on_click=select_building,

                        args=(
                            building_id,
                        ),

                        use_container_width=True,

                        disabled=is_selected

                    )


                    safe_col, unsafe_col = (
                        st.columns(2)
                    )


                    with safe_col:

                        st.button(

                            "Mark Safe",

                            key=(
                                "safe_"
                                +
                                building_id
                            ),

                            use_container_width=True,

                            on_click=complete_inspection,

                            args=(

                                building_id,

                                STATUS_DONE_SAFE

                            )

                        )


                    with unsafe_col:

                        st.button(

                            "Mark Unsafe",

                            key=(
                                "unsafe_"
                                +
                                building_id
                            ),

                            use_container_width=True,

                            on_click=complete_inspection,

                            args=(

                                building_id,

                                STATUS_DONE_UNSAFE

                            )

                        )


                # =================================================
                # COMPLETED
                # =================================================

                else:

                    if current_status == STATUS_DONE_SAFE:

                        st.markdown(
                            '<div style="display:flex;align-items:center;gap:6px;'
                            'font-size:0.82rem;font-weight:600;color:#166534;margin-bottom:2px;">'
                            '<span class="dot dot-green"></span>COMPLETED &mdash; SAFE</div>',
                            unsafe_allow_html=True
                        )

                    elif current_status == STATUS_DONE_UNSAFE:

                        st.markdown(
                            '<div style="display:flex;align-items:center;gap:6px;'
                            'font-size:0.82rem;font-weight:600;color:#dc2626;margin-bottom:2px;">'
                            '<span class="dot dot-red"></span>COMPLETED &mdash; UNSAFE</div>',
                            unsafe_allow_html=True
                        )


                    if current_team is not None:

                        st.caption(

                            f"Inspection completed by "
                            f"{current_team}"

                        )


                    st.button(

                        "Focus on map"
                        if not is_selected
                        else "Focused",

                        key=(
                            "focus_done_"
                            +
                            building_id
                        ),

                        on_click=select_building,

                        args=(
                            building_id,
                        ),

                        use_container_width=True,

                        disabled=is_selected

                    )


    # ========================================================
    # CLEAR SELECTION
    # ========================================================

    if (
        st.session_state.selected_id
        is not None
    ):

        st.button(

            "Clear map selection",

            use_container_width=True,

            on_click=clear_selection

        )


# ============================================================
# SITE DETAILS
# ============================================================

if selected_row is not None:

    st.markdown("---")

    st.subheader(
        "Site Details"
    )


    selected_id = str(
        selected_row["id"]
    )

    inject_card_tint(
        "detail_panel_" + selected_id,
        selected_row["damage_level"]
    )

    detail_panel = st.container(
        border=True,
        key="detail_panel_" + selected_id
    )

    _detail_ctx = detail_panel.__enter__()


    selected_status = get_status(
        selected_id
    )


    selected_team = get_team(
        selected_id
    )


    selected_time = get_time(
        selected_id
    )


    selected_density = int(

        round(

            selected_row[
                "population_density"
            ]

        )

    )


    selected_exposure = int(

        round(

            selected_row[
                "estimated_population"
            ]

        )

    )


    priority_level = (
        selected_row[
            "priority_level"
        ]
    )

    priority_color = PRIORITY_TEXT_COLOR.get(priority_level, "#3f3f46")


    detail_col1, detail_col2 = st.columns(
        [3, 1]
    )


    with detail_col1:

        header_line = f"### {selected_id}"

        if priority_level == "CRITICAL":

            header_line += "&nbsp; <span class='tag-critical'>&#9888; CRITICAL</span>"

        else:

            header_line += (
                f"&nbsp; <span style='color:{priority_color}; "
                f"font-weight:700; font-size:0.8rem; letter-spacing:0.03em;'>"
                f"{priority_level} PRIORITY</span>"
            )

        st.markdown(header_line, unsafe_allow_html=True)


        damage = (
            selected_row[
                "damage_level"
            ]
        )

        damage_dot_color = {
            "Destroyed": "#dc2626",
            "Major": "#d97706",
            "Minor": "#2563eb",
            "No Damage": "#16a34a",
        }.get(damage, "#9ca3af")

        st.markdown(
            f"<span style='color:{damage_dot_color};'>&#9679;</span> "
            f"<span style='font-weight:600;'>{damage.upper()}</span>",
            unsafe_allow_html=True
        )


    with detail_col2:

        st.metric(

            "Priority Score",

            f"{selected_row['priority_score']:.3f}"

        )


    # ========================================================
    # SITE METRICS
    # ========================================================

    d1, d2, d3, d4 = st.columns(4)


    with d1:

        st.metric(

            "Building Area",

            f"{selected_row['area']:.0f} m²"

        )


    with d2:

        st.metric(

            "Population Density",

            f"{selected_density:,}"

        )


    with d3:

        st.metric(

            "People Affected",

            f"{selected_exposure:,}"

        )


    with d4:

        if selected_team is None:

            st.metric(
                "Inspection Team",
                "Waiting"
            )

        else:

            st.metric(

                "Inspection Team",

                selected_team

            )


    # ========================================================
    # LOCATION
    # ========================================================

    detail_left, detail_right = st.columns(
        2
    )


    with detail_left:

        st.markdown(
            '<div class="section-eyebrow">Location</div>',
            unsafe_allow_html=True
        )


        st.code(

            f"Latitude:  "
            f"{selected_row['latitude']}\n"

            f"Longitude: "
            f"{selected_row['longitude']}",

            language="text"

        )


    with detail_right:

        st.markdown(
            '<div class="section-eyebrow">Inspection</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f"<div style='display:flex;align-items:center;gap:6px;font-size:0.95rem;font-weight:650;color:#111827;'>"
            f"<span class='dot {STATUS_DOT.get(selected_status, 'dot-gray')}'></span>{selected_status}</div>",
            unsafe_allow_html=True
        )


        if selected_team is not None:

            st.write(

                f"**Team:** "
                f"{selected_team}"

            )


        if selected_time:

            st.write(

                f"**Assigned:** "
                f"{selected_time}"

            )


        if selected_status == STATUS_WAITING:

            st.caption(

                "All inspection teams are busy. "
                "This building is waiting in the queue."

            )

        elif selected_status == STATUS_IN_PROGRESS:

            st.caption(

                f"{selected_team} is currently "
                f"inspecting this building."

            )

        elif selected_status == STATUS_DONE_SAFE:

            st.caption(

                f"Inspection completed by "
                f"{selected_team}. Building marked safe."

            )

        elif selected_status == STATUS_DONE_UNSAFE:

            st.caption(

                f"Inspection completed by "
                f"{selected_team}. Building marked unsafe."

            )

        else:

            st.caption(

                "No inspection team assigned."

            )


    detail_panel.__exit__(None, None, None)


# ============================================================
# EMERGENCY RESPONSE OVERVIEW
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-eyebrow">Emergency Response</div>',
    unsafe_allow_html=True
)

st.subheader(
    "Emergency Response Overview"
)


not_assigned_count = 0

waiting_count = 0

ongoing_count = 0

safe_count = 0

unsafe_count = 0


for building_id in df["id"]:

    status = get_status(
        building_id
    )


    if status == STATUS_NOT_ASSIGNED:

        not_assigned_count += 1

    elif status == STATUS_WAITING:

        waiting_count += 1

    elif status == STATUS_IN_PROGRESS:

        ongoing_count += 1

    elif status == STATUS_DONE_SAFE:

        safe_count += 1

    elif status == STATUS_DONE_UNSAFE:

        unsafe_count += 1


with st.container(border=True, key="response_overview_bar"):

    response_col1, response_col2, response_col3, response_col4 = (
        st.columns(4)
    )

    with response_col1:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-gray"></span>Not Assigned</div>
            <div class="flat-metric-value">{not_assigned_count}</div>
            """,
            unsafe_allow_html=True
        )

    with response_col2:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-orange"></span>Waiting for Team</div>
            <div class="flat-metric-value">{waiting_count}</div>
            """,
            unsafe_allow_html=True
        )

    with response_col3:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-blue"></span>Inspection Ongoing</div>
            <div class="flat-metric-value">{ongoing_count}</div>
            """,
            unsafe_allow_html=True
        )

    with response_col4:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-green"></span>Completed</div>
            <div class="flat-metric-value">{safe_count + unsafe_count}</div>
            """,
            unsafe_allow_html=True
        )


st.markdown("")


# ============================================================
# TEAM STATUS
# ============================================================

st.markdown(
    '<div class="section-eyebrow" style="margin-top:22px;">Field Operations</div>',
    unsafe_allow_html=True
)

st.markdown(
    "#### Inspection Team Status"
)


team_cols = st.columns(
    len(INSPECTION_TEAMS)
)


for i, team in enumerate(
    INSPECTION_TEAMS
):

    with team_cols[i]:

        team_building = None


        for building_id in df["id"]:

            if (

                get_team(building_id)
                ==
                team

                and

                get_status(building_id)
                ==
                STATUS_IN_PROGRESS

            ):

                team_building = building_id

                break


        if team_building is not None:

            st.markdown(
                f"""
                <div class="team-card">
                    <div class="team-name">{team}</div>
                    <div class="team-status"><span class="dot dot-orange"></span>On Assignment &middot; {team_building}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="team-card">
                    <div class="team-name">{team}</div>
                    <div class="team-status"><span class="dot dot-green"></span>Available</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# WAITING QUEUE
# ============================================================

if st.session_state.inspection_queue:

    st.markdown("")

    st.markdown(
        "#### Inspection Waiting Queue"
    )


    queue_rows = []


    for position, building_id in enumerate(

        st.session_state.inspection_queue,

        start=1

    ):

        match = df[

            df["id"]
            ==
            building_id

        ]


        if match.empty:

            continue


        row = match.iloc[0]


        queue_rows.append({

            "Position": position,

            "Building": building_id,

            "Priority": row[
                "priority_level"
            ],

            "Damage": row[
                "damage_level"
            ],

            "People Affected": int(

                round(

                    row[
                        "estimated_population"
                    ]

                )

            )

        })


    if queue_rows:

        st.dataframe(

            pd.DataFrame(
                queue_rows
            ),

            use_container_width=True,

            hide_index=True

        )


# ============================================================
# PRIORITY DISTRIBUTION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-eyebrow">Prioritization</div>',
    unsafe_allow_html=True
)

st.markdown(
    "#### Priority Distribution"
)


priority_counts = (

    df[
        "priority_level"
    ]

    .value_counts()

)


with st.container(border=True, key="priority_distribution_bar"):

    priority_col1, priority_col2, priority_col3, priority_col4 = (
        st.columns(4)
    )

    with priority_col1:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-red"></span>Critical</div>
            <div class="flat-metric-value">{int(priority_counts.get("CRITICAL", 0))}</div>
            """,
            unsafe_allow_html=True
        )

    with priority_col2:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-orange"></span>High</div>
            <div class="flat-metric-value">{int(priority_counts.get("HIGH", 0))}</div>
            """,
            unsafe_allow_html=True
        )

    with priority_col3:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot" style="background:#d4a017;"></span>Medium</div>
            <div class="flat-metric-value">{int(priority_counts.get("MEDIUM", 0))}</div>
            """,
            unsafe_allow_html=True
        )

    with priority_col4:

        st.markdown(
            f"""
            <div class="flat-metric-label"><span class="dot dot-green"></span>Low</div>
            <div class="flat-metric-value">{int(priority_counts.get("LOW", 0))}</div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# POPULATION EXPOSURE ANALYSIS
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-eyebrow">Population Risk</div>',
    unsafe_allow_html=True
)

st.subheader(
    "Population Exposure Analysis"
)


pop_col1, pop_col2, pop_col3, pop_col4 = (
    st.columns(4)
)


total_exposure = int(

    round(

        df[
            "estimated_population"
        ].sum()

    )

)


average_density = int(

    round(

        df[
            "population_density"
        ].mean()

    )

)


highest_exposure = int(

    round(

        df[
            "estimated_population"
        ].max()

    )

)


high_exposure_count = (

    df[

        df[
            "estimated_population"
        ]

        >=

        5

    ]

).shape[0]


with pop_col1:

    st.metric(

        "Affected Population",

        f"{total_exposure:,}"

    )


with pop_col2:

    st.metric(

        "Average Density",

        f"{average_density:,}/km²"

    )


with pop_col3:

    st.metric(

        "Highest Site Exposure",

        f"{highest_exposure:,}"

    )


with pop_col4:

    st.metric(

        "High-Exposure Sites",

        high_exposure_count

    )


# ============================================================
# HIGHEST EXPOSURE SITES
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-eyebrow">Site Analysis</div>',
    unsafe_allow_html=True
)

st.subheader(
    "Highest Population Exposure Sites"
)


exposure_table = (

    df.sort_values(

        "estimated_population",

        ascending=False

    )

    [

        [

            "id",

            "damage_level",

            "priority_level",

            "area",

            "population_density",

            "estimated_population",

            "priority_score"

        ]

    ]

    .head(10)

    .copy()

)


exposure_table["area"] = (

    exposure_table[
        "area"
    ]

    .round(2)

)


exposure_table[
    "population_density"
] = (

    exposure_table[
        "population_density"
    ]

    .round()

    .astype(int)

)


exposure_table[
    "estimated_population"
] = (

    exposure_table[
        "estimated_population"
    ]

    .round()

    .astype(int)

)


exposure_table[
    "priority_score"
] = (

    exposure_table[
        "priority_score"
    ]

    .round(3)

)


exposure_table.columns = [

    "Building",

    "Damage",

    "Priority",

    "Area (m²)",

    "Density (people/km²)",

    "People Affected",

    "Priority Score"

]


st.dataframe(

    exposure_table,

    use_container_width=True,

    hide_index=True

)


# ============================================================
# FULL BUILDING DATASET
# ============================================================

st.markdown("---")


st.subheader(
    "Full Building Dataset"
)


full_table = (

    df.sort_values(

        "priority_score",

        ascending=False

    )

    [

        [

            "id",

            "damage_level",

            "priority_level",

            "area",

            "latitude",

            "longitude",

            "population_density",

            "estimated_population",

            "priority_score"

        ]

    ]

    .copy()

)


full_table["area"] = (

    full_table[
        "area"
    ]

    .round(2)

)


full_table[
    "population_density"
] = (

    full_table[
        "population_density"
    ]

    .round()

    .astype(int)

)


full_table[
    "estimated_population"
] = (

    full_table[
        "estimated_population"
    ]

    .round()

    .astype(int)

)


full_table[
    "priority_score"
] = (

    full_table[
        "priority_score"
    ]

    .round(3)

)


full_table.columns = [

    "Building",

    "Damage",

    "Priority",

    "Area (m²)",

    "Latitude",

    "Longitude",

    "Population Density",

    "People Affected",

    "Priority Score"

]


st.dataframe(

    full_table,

    use_container_width=True,

    hide_index=True

)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")


st.caption(

    "Population estimates are derived from WorldPop "
    "population-density data using georeferenced "
    "building coordinates and detected building area. "
    "Damage information originates from the building "
    "detection pipeline."

)