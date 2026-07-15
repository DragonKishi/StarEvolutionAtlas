"""
app.py

The Star Evolution Atlas (SEA) 

An interactive Hertzsprung-Russell Diagram Explorer powered by the
HYG star catalog (~119k real stars) with:
  - Interactive H-R diagram (WebGL, 100k+ stars)
  - Stellar evolution tracks & animations (6 masses)
  - Sky position chart for any clicked star
  - Rich star detail panel with physics



Author: Parth Mishra
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Path setup 
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from components.hr_diagram        import build_hr_figure, add_spectral_bands, add_temperature_axis
from components.sky_chart         import build_sky_chart
from components.evolution_animator import build_evolution_animation, get_phase_info_html
from components.star_detail       import render_star_panel, render_no_star_selected
from physics.evolution_data       import get_all_tracks, get_track_by_mass
from physics.stellar_physics      import bv_to_hex_color


# Page Configuration 
st.set_page_config(
    page_title    = "The Star Evolution Atlas (SEA)",
    page_icon     = "⭐",
    layout        = "wide",
    initial_sidebar_state = "expanded",
)


#  Custom CSS 
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Root & Background ── */
html, body, [data-testid="stApp"] {
    background: #050A1A !important;
    font-family: 'Inter', sans-serif;
    color: #D6E4FF;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080F24 0%, #050A1A 100%) !important;
    border-right: 1px solid rgba(100,150,255,0.12) !important;
}

/* ── Main header ── */
.sea-header {
    background: linear-gradient(135deg, rgba(10,20,60,0.8) 0%, rgba(5,10,30,0.95) 100%);
    border: 1px solid rgba(91,140,255,0.25);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    backdrop-filter: blur(10px);
}

.sea-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.0em;
    font-weight: 700;
    background: linear-gradient(90deg, #5B8CFF, #A78BFA, #60C6FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

.sea-subtitle {
    color: rgba(160,196,255,0.8);
    font-size: 0.9em;
    margin-top: 4px;
    font-weight: 400;
}

.sea-badge {
    display: inline-block;
    background: rgba(91,140,255,0.15);
    border: 1px solid rgba(91,140,255,0.35);
    color: #5B8CFF;
    font-size: 0.72em;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 8px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Metrics ── */
.sea-metric {
    background: rgba(10,20,50,0.7);
    border: 1px solid rgba(100,150,255,0.15);
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.sea-metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4em;
    font-weight: 700;
    color: #5B8CFF;
}
.sea-metric-label {
    font-size: 0.75em;
    color: rgba(140,170,220,0.7);
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: rgba(10,20,50,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(100,150,255,0.12) !important;
}
[data-testid="stTabs"] [role="tab"] {
    color: rgba(140,170,220,0.75) !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: rgba(91,140,255,0.2) !important;
    color: #A0C4FF !important;
}

/* ── Sidebar sections ── */
.sidebar-section {
    background: rgba(10,25,55,0.5);
    border: 1px solid rgba(100,150,255,0.12);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}
.sidebar-section-title {
    font-size: 0.75em;
    font-weight: 600;
    color: #5B8CFF;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

/* ── Streamlit widgets ── */
.stSlider label, .stMultiSelect label, .stSelectbox label,
.stCheckbox label, .stRadio label {
    color: rgba(160,196,255,0.85) !important;
    font-size: 0.88em !important;
}
.stButton > button {
    background: linear-gradient(135deg, rgba(40,80,180,0.7), rgba(91,140,255,0.5)) !important;
    border: 1px solid rgba(91,140,255,0.4) !important;
    color: #D6E4FF !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(60,110,220,0.85), rgba(120,170,255,0.65)) !important;
    border-color: rgba(120,170,255,0.6) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(91,140,255,0.25) !important;
}

/* ── Info boxes ── */
.physics-card {
    background: linear-gradient(135deg, rgba(10,25,55,0.8), rgba(8,18,45,0.95));
    border: 1px solid rgba(100,150,255,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    margin: 10px 0;
}
.physics-card h3 {
    color: #5B8CFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05em;
    margin: 0 0 10px 0;
}
.physics-card p {
    color: rgba(200,220,255,0.85);
    font-size: 0.88em;
    line-height: 1.6;
    margin: 0;
}

/* ── Divider ── */
.sea-divider {
    border: none;
    border-top: 1px solid rgba(100,150,255,0.1);
    margin: 16px 0;
}

/* ── Star count pill ── */
.star-count-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(91,140,255,0.12);
    border: 1px solid rgba(91,140,255,0.25);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82em;
    color: #8AABDB;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #050A1A; }
::-webkit-scrollbar-thumb { background: rgba(91,140,255,0.3); border-radius: 3px; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


#  Data Loading 
DATA_PATH    = os.path.join(ROOT, "data", "hyg_processed.csv")
HYG_RAW_URL  = (
    "https://raw.githubusercontent.com/astronexus/HYG-Database/master/hygdata_v3.csv"
)


@st.cache_data(show_spinner=False)
def load_star_data() -> pd.DataFrame:
    """
    Load (and if necessary, fetch+process) the HYG star catalog.

    Returns
    -------
    pd.DataFrame
        Processed star catalog with physics columns.
    """
    # If pre-processed file exists, use it directly
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, low_memory=False)
        df["color_hex"] = df["color_hex"].fillna("#FFD700")
        df["name"]      = df["name"].fillna("Unknown")
        df["spect"]     = df["spect"].fillna("")
        df["category"]  = df["category"].fillna("Main Sequence")
        df["constellation"] = df["constellation"].fillna("")
        return df

    # Otherwise, download and process on the fly
    st.info("⬇️  Downloading HYG star catalog for the first time (~30 MB)…")
    from data.fetch_data import download_hyg, process_hyg, save_processed
    df_raw  = download_hyg()
    df_proc = process_hyg(df_raw)
    save_processed(df_proc)
    return df_proc


#  Session State Initialization 
if "selected_star_id" not in st.session_state:
    st.session_state.selected_star_id = None
if "selected_track_mass" not in st.session_state:
    st.session_state.selected_track_mass = 1.0
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0


#  Header 
st.markdown("""
<div class="sea-header">
  <div style="font-size:3em; line-height:1;">🌌</div>
  <div>
    <div class="sea-title">The Star Evolution Atlas</div>
    <div class="sea-subtitle">
      Explore 119,000+ real stars on the Hertzsprung-Russell Diagram
      · Stellar evolution tracks · Interactive sky charts
    </div>
    <div>
      <span class="sea-badge">⚡ Powered by HYG Catalog v3</span>
      <span class="sea-badge" style="margin-left:6px;">📡 ESA Hipparcos Data</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


#  Load Data 
with st.spinner("🌟 Loading star catalog…"):
    df = load_star_data()


#  Sidebar 
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 16px;">
      <span style="font-size:2em;">⭐</span>
      <div style="font-family:'Space Grotesk',sans-serif; font-weight:700;
                  color:#5B8CFF; font-size:1.1em; margin-top:4px;">
        SEA Controls
      </div>
    </div>
    """, unsafe_allow_html=True)

    #  Catalog stats 
    total_stars = len(df)
    st.markdown(f"""
    <div class="sidebar-section">
      <div class="sidebar-section-title">📊 Catalog Stats</div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <div class="sea-metric">
          <div class="sea-metric-value">{total_stars:,}</div>
          <div class="sea-metric-label">Total Stars</div>
        </div>
        <div class="sea-metric">
          <div class="sea-metric-value">{df["category"].value_counts().get("Main Sequence", 0):,}</div>
          <div class="sea-metric-label">Main Seq.</div>
        </div>
        <div class="sea-metric">
          <div class="sea-metric-value">{df["category"].value_counts().get("Giant", 0):,}</div>
          <div class="sea-metric-label">Giants</div>
        </div>
        <div class="sea-metric">
          <div class="sea-metric-value">{df["category"].value_counts().get("White Dwarf", 0):,}</div>
          <div class="sea-metric-label">White Dwarfs</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    #  H-R Diagram Filters 
    st.markdown("""
    <div class="sidebar-section-title" style="margin-top:10px;">🔭 H-R Diagram Filters</div>
    """, unsafe_allow_html=True)

    dist_max = st.slider(
        "Max Distance (parsecs)",
        min_value  = 10,
        max_value  = int(df["dist_pc"].quantile(0.99)),
        value      = int(df["dist_pc"].quantile(0.99)),
        step       = 10,
        help       = "Show only stars within this distance from the Sun.",
    )

    spectral_options = ["All", "O", "B", "A", "F", "G", "K", "M"]
    spec_filter = st.multiselect(
        "Spectral Classes",
        options   = ["O", "B", "A", "F", "G", "K", "M"],
        default   = ["O", "B", "A", "F", "G", "K", "M"],
        help      = "Filter by spectral class (temperature group).",
    )

    mag_range = st.slider(
        "Absolute Magnitude Range",
        min_value = -10.0,
        max_value =  18.0,
        value     = (-10.0, 18.0),
        step      = 0.5,
        help      = "Lower = brighter. Upper = dimmer.",
    )

    cat_filter = st.multiselect(
        "Star Categories",
        options = ["Main Sequence", "Giant", "Supergiant", "White Dwarf"],
        default = ["Main Sequence", "Giant", "Supergiant", "White Dwarf"],
    )

    st.markdown("<hr class='sea-divider'>", unsafe_allow_html=True)

    #  Overlay Options 
    st.markdown("""
    <div class="sidebar-section-title">🌠 Overlays</div>
    """, unsafe_allow_html=True)

    show_tracks = st.checkbox("Show Evolution Tracks", value=False,
        help="Overlay theoretical stellar evolution tracks (0.8–25 M☉)")
    show_zams   = st.checkbox("Show ZAMS Line",         value=True,
        help="Show the Zero-Age Main Sequence reference line")
    show_labels = st.checkbox("Show Region Labels",     value=True,
        help="Label diagram regions: Main Sequence, Giants, White Dwarfs, etc.")
    show_bands  = st.checkbox("Show Spectral Bands",    value=False,
        help="Color-coded vertical bands for O/B/A/F/G/K/M spectral classes")
    show_temp   = st.checkbox("Show Temperature Axis",  value=False,
        help="Display secondary top axis with approximate temperature (K)")

    st.markdown("<hr class='sea-divider'>", unsafe_allow_html=True)

    #  Star Search 
    st.markdown("""
    <div class="sidebar-section-title">🔍 Star Search</div>
    """, unsafe_allow_html=True)

    search_query = st.text_input(
        "Search by name",
        placeholder = "e.g. Sirius, Betelgeuse, HIP 24436…",
        label_visibility = "collapsed",
    )

    if search_query:
        matches = df[df["name"].str.contains(search_query, case=False, na=False)]
        if len(matches) > 0:
            options = matches["name"].head(10).tolist()
            selected_name = st.selectbox("Select:", options, key="search_select")
            if st.button("⭐ Go to Star", use_container_width=True):
                match = matches[matches["name"] == selected_name]
                if not match.empty:
                    st.session_state.selected_star_id = int(match["id"].iloc[0])
        else:
            st.markdown(
                f"<div style='color:rgba(255,100,100,0.7);font-size:0.82em;'>"
                f"No results for \"{search_query}\"</div>",
                unsafe_allow_html=True
            )

    st.markdown("<hr class='sea-divider'>", unsafe_allow_html=True)

    #  Selected Star Panel 
    st.markdown("""
    <div class="sidebar-section-title">📌 Selected Star</div>
    """, unsafe_allow_html=True)

    if st.session_state.selected_star_id is not None:
        star_row_df = df[df["id"] == st.session_state.selected_star_id]
        if not star_row_df.empty:
            star_row = star_row_df.iloc[0]
            st.html(render_star_panel(star_row))
            if st.button("✕ Clear Selection", use_container_width=True):
                st.session_state.selected_star_id = None
                st.rerun()
        else:
            st.session_state.selected_star_id = None
    else:
        st.html(render_no_star_selected())


#  Apply Filters 
df_filtered = df[
    (df["dist_pc"]  <= dist_max) &
    (df["spectral"].isin(spec_filter if spec_filter else ["O","B","A","F","G","K","M"])) &
    (df["absmag"]   >= mag_range[0]) &
    (df["absmag"]   <= mag_range[1]) &
    (df["category"].isin(cat_filter if cat_filter else ["Main Sequence","Giant","Supergiant","White Dwarf"]))
].copy()

# Performance cap: if >80k stars, sample intelligently
MAX_PLOT_STARS = 80_000
if len(df_filtered) > MAX_PLOT_STARS:
    df_filtered = df_filtered.sample(MAX_PLOT_STARS, random_state=42)

n_showing = len(df_filtered)


#  Main Tabs 
tab1, tab2, tab3, tab4 = st.tabs([
    "🌌  H-R Diagram",
    "🔭  Sky Chart",
    "✨  Evolution Atlas",
    "📖  Physics Guide",
])



# TAB 1 — H-R DIAGRAM

with tab1:
    # Filter status bar
    col_a, col_b, col_c = st.columns([3, 1, 1])
    with col_a:
        st.markdown(
            f"<div class='star-count-pill'>⭐ Showing <b style='color:#5B8CFF; margin:0 4px;'>"
            f"{n_showing:,}</b> stars "
            f"(filtered from {len(df):,})</div>",
            unsafe_allow_html=True
        )
    with col_b:
        opacity_val = st.slider("Opacity", 0.2, 1.0, 0.75, 0.05,
                                label_visibility="collapsed",
                                help="Star marker opacity",
                                key="opacity_slider")
    with col_c:
        st.markdown("<div style='color:#6A8ABF;font-size:0.78em;padding-top:8px;'>Opacity</div>",
                    unsafe_allow_html=True)

    # Build figure
    fig_hr = build_hr_figure(
        df_filtered,
        show_tracks    = show_tracks,
        show_zams      = show_zams,
        show_labels    = show_labels,
        highlight_id   = st.session_state.selected_star_id,
        selected_track = st.session_state.selected_track_mass if show_tracks else None,
        opacity        = opacity_val,
    )

    if show_bands:
        fig_hr = add_spectral_bands(fig_hr)

    if show_temp:
        fig_hr = add_temperature_axis(fig_hr)

    # Click handler via plotly_events
    clicked = st.plotly_chart(
        fig_hr,
        width               = "stretch",
        key                 = "hr_diagram_chart",
        on_select           = "rerun",
        selection_mode      = "points",
    )

    # Handle point click
    if clicked and clicked.get("selection") and clicked["selection"].get("points"):
        pts = clicked["selection"]["points"]
        if pts:
            pt = pts[0]
            # customdata[0] is the star ID
            cd = pt.get("customdata")
            if cd is not None and len(cd) > 0:
                clicked_id = int(cd[0])
                if clicked_id != st.session_state.selected_star_id:
                    st.session_state.selected_star_id = clicked_id
                    st.rerun()

    # Spectral class legend
    st.markdown("""
    <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:center;
                margin-top:8px; padding:10px 0;">
    """ + "".join([
        f'<div style="display:flex;align-items:center;gap:5px;font-size:0.78em;color:#8AABDB;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{bv_to_hex_color(bv)};'
        f'display:inline-block;"></span>{cls}'
        f'<span style="color:rgba(100,140,200,0.5);">({label})</span></div>'
        for cls, bv, label in [
            ("O", -0.3, "~40,000 K"), ("B", -0.15, "~20,000 K"),
            ("A",  0.1, "~9,000 K"),  ("F",  0.4,  "~6,500 K"),
            ("G",  0.65,"~5,800 K"),  ("K",  1.0,  "~4,500 K"),
            ("M",  1.6, "~3,200 K"),
        ]
    ]) + "</div>", unsafe_allow_html=True)



# TAB 2 — SKY CHART

with tab2:
    selected_star = None
    if st.session_state.selected_star_id is not None:
        row = df[df["id"] == st.session_state.selected_star_id]
        if not row.empty:
            selected_star = row.iloc[0]

    col1, col2 = st.columns([3, 1])
    with col2:
        neighborhood_r = st.slider(
            "Neighborhood Radius (°)",
            min_value = 5.0,
            max_value = 60.0,
            value     = 25.0,
            step      = 5.0,
            help      = "Angular radius around the selected star to show neighbors.",
        )
    with col1:
        if selected_star is None:
            st.info("💡 Select a star by clicking it on the **H-R Diagram** tab first, "
                    "then return here to see its sky position.")

    fig_sky = build_sky_chart(
        selected_star       = selected_star,
        df                  = df,
        neighborhood_radius_deg = neighborhood_r,
    )
    st.plotly_chart(fig_sky, width="stretch")

    if selected_star is not None:
        st.markdown("""
        <div class="physics-card">
          <h3>🌐 Reading Sky Coordinates</h3>
          <p>
            <b>Right Ascension (RA)</b> — the celestial equivalent of longitude, measured in hours
            (0h–24h) eastward along the celestial equator. One hour = 15°.<br><br>
            <b>Declination (Dec)</b> — the celestial equivalent of latitude, measured in degrees
            north (+90°) or south (−90°) of the celestial equator.<br><br>
            Stars near Dec 0° are on the celestial equator and rise/set for most observers.
            Stars near Dec +90° are circumpolar in the northern hemisphere (never set).
          </p>
        </div>
        """, unsafe_allow_html=True)



# TAB 3 — EVOLUTION ATLAS

with tab3:
    all_tracks = get_all_tracks()
    track_options = {t.label: t.mass for t in all_tracks}

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        st.markdown("""
        <div style="color:#8AABDB; font-size:0.82em; font-weight:600;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
          Select a Star Mass
        </div>
        """, unsafe_allow_html=True)

        selected_label = st.selectbox(
            "Track",
            options          = list(track_options.keys()),
            index            = list(track_options.keys()).index("1 M☉ ☀"),
            label_visibility = "collapsed",
            key              = "track_selector",
        )
        selected_mass  = track_options[selected_label]
        selected_track = get_track_by_mass(selected_mass)
        st.session_state.selected_track_mass = selected_mass

        if selected_track:
            hex_c = selected_track.color
            r = int(hex_c[1:3],16); g = int(hex_c[3:5],16); b = int(hex_c[5:7],16)
            st.markdown(f"""
            <div style="
                background: rgba({r},{g},{b},0.12);
                border: 1px solid rgba({r},{g},{b},0.35);
                border-radius: 10px;
                padding: 14px;
                margin-top: 12px;
                font-size: 0.86em;
                line-height: 1.55;
                color: #D6E4FF;
            ">
              <div style="color:rgb({r},{g},{b}); font-weight:700; margin-bottom:6px;">
                {selected_track.label} — {selected_track.end_state_icon} {selected_track.end_state}
              </div>
              {selected_track.mass_description}
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        if selected_track:
            st.markdown("""
            <div style="color:#8AABDB; font-size:0.82em; font-weight:600;
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">
              Life Phases
            </div>
            """, unsafe_allow_html=True)
            st.html(get_phase_info_html(selected_track))

    # Animation
    if selected_track:
        st.markdown("<hr class='sea-divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="color:#8AABDB; font-size:0.82em; font-weight:600;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">
          ▶ Animated Evolution Sequence — Press Play
        </div>
        """, unsafe_allow_html=True)

        fig_anim = build_evolution_animation(selected_track)
        st.plotly_chart(fig_anim, width="stretch", key="evolution_anim")

    # Mass comparison table
    st.markdown("<hr class='sea-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#8AABDB; font-size:0.82em; font-weight:600;
                text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">
      Track Comparison
    </div>
    """, unsafe_allow_html=True)

    comparison_data = []
    for t in all_tracks:
        comparison_data.append({
            "Mass": t.label,
            "End State": f"{t.end_state_icon} {t.end_state}",
            "Phases": len(t.phases),
            "Description": t.mass_description[:100] + "…",
        })

    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(
        comp_df,
        width       = "stretch",
        hide_index  = True,
        column_config = {
            "Mass":        st.column_config.TextColumn("Mass",        width="small"),
            "End State":   st.column_config.TextColumn("End State",   width="medium"),
            "Phases":      st.column_config.NumberColumn("# Phases",  width="small"),
            "Description": st.column_config.TextColumn("Description", width="large"),
        }
    )


# TAB 4 — PHYSICS GUIDE
with tab4:
    st.markdown("""
    <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3em; font-weight:700;
                color:#5B8CFF; margin-bottom:16px;">
      📖 The Physics of the Hertzsprung-Russell Diagram
    </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("""
        <div class="physics-card">
          <h3>🌡 What is the H-R Diagram?</h3>
          <p>
            Independently invented by Ejnar Hertzsprung (1911) and Henry Norris Russell (1913),
            the H-R diagram is the cornerstone of stellar astrophysics. It reveals that stars
            are not randomly distributed — they cluster into distinct populations that directly
            reflect the physics of stellar structure and evolution.
            <br><br>
            The X-axis runs from <b>hot (left) to cool (right)</b> — counterintuitively reversed
            from our instinct, because blue stars are hotter than red stars.
            The Y-axis runs from <b>bright (top) to dim (bottom)</b>.
          </p>
        </div>

        <div class="physics-card">
          <h3>⭐ The Main Sequence</h3>
          <p>
            The diagonal band from upper-left (hot, bright) to lower-right (cool, dim) contains
            ~90% of all stars — including our Sun. Main-sequence stars are in <b>hydrostatic
            equilibrium</b>: gravity pulling in is exactly balanced by radiation pressure pushing out,
            powered by hydrogen fusion in the core.
            <br><br>
            A star's position on the main sequence is almost entirely determined by its <b>mass</b>.
            More massive → hotter → more luminous → shorter-lived.
          </p>
        </div>

        <div class="physics-card">
          <h3>🔴 Red Giants & Supergiants</h3>
          <p>
            When a star exhausts its core hydrogen, the core contracts and shell burning begins.
            The outer envelope expands enormously (up to 100–1000× the original radius),
            cooling the surface and turning the star red-orange.
            <br><br>
            <b>Giants</b> (upper right): evolved stars of 0.8–8 M☉, forming the Red Giant Branch.<br>
            <b>Supergiants</b> (top): massive stars (> 8 M☉) that have left the main sequence
            and now burn heavier elements in shell layers.
          </p>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="physics-card">
          <h3>⚪ White Dwarfs</h3>
          <p>
            Located in the lower-left, white dwarfs are the <b>dead cores</b> of stars that shed
            their envelopes as planetary nebulae. They are supported not by fusion but by
            <b>electron degeneracy pressure</b> — a quantum mechanical effect.
            <br><br>
            White dwarfs have masses up to ~1.4 M☉ (the Chandrasekhar limit). Above this,
            they can trigger Type Ia supernovae. They slowly cool over billions of years,
            eventually becoming hypothetical "black dwarfs."
          </p>
        </div>

        <div class="physics-card">
          <h3>🎨 Color Index B-V</h3>
          <p>
            The B-V color index is the difference in a star's brightness measured through two
            filters: Blue (B, λ≈440 nm) and Visual/Green (V, λ≈550 nm).
            <br><br>
            <b>B-V &lt; 0</b>: more flux in blue → hot, blue star (O/B type)<br>
            <b>B-V ≈ 0.65</b>: balanced → yellow-white star like the Sun (G type)<br>
            <b>B-V &gt; 1.4</b>: more flux in red/green → cool, red star (M type)<br><br>
            Temperature from B-V uses the <b>Ballesteros (2012)</b> formula:
          </p>
          <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:10px; margin-top:8px;
                      font-family:monospace; font-size:0.85em; color:#A0C4FF; text-align:center;">
            T = 4600 × [1/(0.92·BV+1.7) + 1/(0.92·BV+0.62)]
          </div>
        </div>

        <div class="physics-card">
          <h3>✨ Stellar Evolution Summary</h3>
          <p>
            <b>Low mass (≤ 8 M☉)</b>: Main Sequence → Red Giant → Planetary Nebula → White Dwarf<br><br>
            <b>High mass (> 8 M☉)</b>: Main Sequence → Supergiant → Type II Supernova →
            Neutron Star (or Black Hole for M > 25 M☉)<br><br>
            The most important rule: <b>mass determines destiny</b>. A star's initial mass
            dictates its temperature, luminosity, lifetime, and final state. The H-R diagram
            makes this visible at a glance.
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="physics-card" style="margin-top:10px;">
      <h3>📚 Key Formulas Reference</h3>
      <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-top:8px;">
        <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:12px;">
          <div style="color:#5B8CFF; font-size:0.78em; font-weight:600; margin-bottom:6px;">LUMINOSITY</div>
          <div style="font-family:monospace; font-size:0.85em; color:#A0C4FF;">
            L/L☉ = 10^[(4.83 − M) / 2.5]
          </div>
          <div style="font-size:0.75em; color:rgba(160,190,240,0.6); margin-top:4px;">
            M = absolute magnitude, M☉ = 4.83
          </div>
        </div>
        <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:12px;">
          <div style="color:#5B8CFF; font-size:0.78em; font-weight:600; margin-bottom:6px;">STELLAR RADIUS</div>
          <div style="font-family:monospace; font-size:0.85em; color:#A0C4FF;">
            R/R☉ = √(L/L☉) × (T☉/T)²
          </div>
          <div style="font-size:0.75em; color:rgba(160,190,240,0.6); margin-top:4px;">
            Stefan-Boltzmann law, T☉ = 5778 K
          </div>
        </div>
        <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:12px;">
          <div style="color:#5B8CFF; font-size:0.78em; font-weight:600; margin-bottom:6px;">MAIN-SEQ. LIFETIME</div>
          <div style="font-family:monospace; font-size:0.85em; color:#A0C4FF;">
            τ_MS ≈ 10 × M^(−2.5) Gyr
          </div>
          <div style="font-size:0.75em; color:rgba(160,190,240,0.6); margin-top:4px;">
            Approximate, M in solar masses
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # References
    st.markdown("""
    <div style="margin-top:20px; padding:16px 20px;
                background:rgba(10,20,50,0.5); border-radius:10px;
                border:1px solid rgba(100,150,255,0.12);">
      <div style="color:#5B8CFF; font-size:0.8em; font-weight:600; letter-spacing:1px;
                  text-transform:uppercase; margin-bottom:10px;">
        Data Sources & References
      </div>
      <ul style="color:rgba(160,196,255,0.75); font-size:0.82em; line-height:1.7; margin:0; padding-left:20px;">
        <li><b>HYG Database v3</b> — D. Nash (astronexus) — Hipparcos + Yale Bright Star + Gliese Catalogs (CC BY-SA 2.5)</li>
        <li><b>ESA Hipparcos Mission</b> — van Leeuwen (2007), A&A 474, 653 — Stellar parallaxes and photometry</li>
        <li><b>Ballesteros (2012)</b> — EPL, 97, 34008 — B-V to effective temperature formula</li>
        <li><b>Bressan et al. (2012)</b> — MNRAS 427, 127 — Padova stellar evolution grids (PARSEC)</li>
        <li><b>Ekström et al. (2012)</b> — A&A 537, A146 — Geneva stellar evolution models with rotation</li>
        <li><b>IAU 2015</b> — Nominal Solar Values: M☉ = 4.74 (bol), L☉ = 3.828×10²⁶ W</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)


#  Footer 
st.html("""
<hr style="border:none; border-top:1px solid rgba(100,150,255,0.08); margin:24px 0 12px;">
<div style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 14px;
    font-family: 'Inter', sans-serif;
">
  <div style="color:rgba(100,140,200,0.4); font-size:0.73em;">
    The Star Evolution Atlas (SEA) &nbsp;·&nbsp; Star data: HYG v3.8 (Hipparcos) &nbsp;·&nbsp;
    Evolution tracks: Padova / Geneva grids &nbsp;·&nbsp; MIT License
  </div>
  <div style="font-size:0.78em; color:rgba(140,170,230,0.65); white-space:nowrap;">
    Built by
    <a href="https://github.com/DragonKishi"
       target="_blank"
       style="color:#5B8CFF; font-weight:600; text-decoration:none;
              border-bottom:1px solid rgba(91,140,255,0.35); padding-bottom:1px;"
    >Parth Mishra</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/DragonKishi"
       target="_blank"
       style="color:rgba(140,170,230,0.55); text-decoration:none; font-size:0.9em;"
    > GitHub</a>
  </div>
</div>
""")
