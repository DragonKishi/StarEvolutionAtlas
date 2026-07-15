"""
hr_diagram.py

Interactive Hertzsprung-Russell diagram Plotly figure.

The H-R diagram plots stars by:
  X-axis: B-V Color Index (proxy for surface temperature), REVERSED
           (hot blue O-type stars on the left, cool red M-type on the right)
  Y-axis: Absolute Magnitude (proxy for luminosity), REVERSED
           (bright stars at top, dim stars at bottom)

Author: Parth Mishra
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from physics.stellar_physics import bv_to_hex_color
from physics.evolution_data import get_all_tracks, get_zams_line


# Plot Constants 
BG_COLOR        = "#050A1A"
GRID_COLOR      = "rgba(100,140,200,0.12)"
AXIS_COLOR      = "rgba(100,140,200,0.35)"
TRACK_ALPHA     = 0.85

REGION_ANNOTATIONS = [
    dict(x=0.65,  y=4.83,   text="☀ Sun",           showarrow=True,  arrowhead=2,
         ax=40,   ay=-30,   font_color="#FFD700",    font_size=11),
    dict(x=0.0,   y=-0.5,   text="Main Sequence",    showarrow=False,
         font_color="rgba(180,220,255,0.7)", font_size=13, textangle=-57),
    dict(x=1.50,  y=0.5,    text="Red Giants",       showarrow=False,
         font_color="rgba(255,160,80,0.85)", font_size=13),
    dict(x=-0.05, y=11.5,   text="White Dwarfs",     showarrow=False,
         font_color="rgba(200,220,255,0.75)", font_size=13),
    dict(x=0.80,  y=-5.5,   text="Supergiants",      showarrow=False,
         font_color="rgba(255,100,100,0.8)", font_size=13),
    dict(x=-0.25, y=-3.5,   text="Blue Giants",      showarrow=False,
         font_color="rgba(130,170,255,0.75)", font_size=12),
]


# Main Figure Builder 

def build_hr_figure(
    df: pd.DataFrame,
    show_tracks:    bool = False,
    show_zams:      bool = True,
    show_labels:    bool = True,
    show_sun:       bool = True,
    highlight_id:   int | None = None,
    selected_track: float | None = None,
    opacity:        float = 0.75,
) -> go.Figure:
    """
    Build the main H-R diagram Plotly figure.

    Parameters
    
    df : pd.DataFrame
        Processed star catalog (from hyg_processed.csv).
    show_tracks : bool
        Overlay theoretical stellar evolution tracks.
    show_zams : bool
        Overlay the Zero-Age Main Sequence reference line.
    show_labels : bool
        Show region annotation labels.
    show_sun : bool
        Highlight the Sun's position.
    highlight_id : int or None
        Star ID to highlight (from a user click).
    selected_track : float or None
        Mass of track to visually emphasize (bold).
    opacity : float
        Opacity of star markers.

    Returns
    
    go.Figure
        A fully configured Plotly figure.
    """
    fig = go.Figure()

    #  Star scatter (WebGL for performance) 
    colors = df["color_hex"].values
    sizes  = df["marker_size"].values.clip(1.5, 18)

    # Hover text
    hover = (
        "<b>" + df["name"].astype(str) + "</b><br>"
        + "Spectral: " + df["spectral"].astype(str)
        + " (" + df["spect"].astype(str).str[:6] + ")<br>"
        + "B-V: "      + df["bv"].map("{:.3f}".format)    + "<br>"
        + "Abs Mag: "  + df["absmag"].map("{:.2f}".format) + "<br>"
        + "Temp: "     + df["temperature"].map("{:,.0f}".format) + " K<br>"
        + "Luminosity: " + df["luminosity"].map("{:.3g}".format) + " L☉<br>"
        + "Radius: "   + df["radius"].map("{:.2f}".format) + " R☉<br>"
        + "Distance: " + df["dist_ly"].map("{:,.1f}".format) + " ly<br>"
        + "Category: " + df["category"].astype(str)
        + "<extra></extra>"
    )

    fig.add_trace(go.Scattergl(
        x          = df["bv"].values,
        y          = df["absmag"].values,
        mode       = "markers",
        marker     = dict(
            color   = colors,
            size    = sizes,
            opacity = opacity,
            line    = dict(width=0),
        ),
        customdata  = df[["id", "name", "ra", "dec", "bv", "absmag",
                           "temperature", "luminosity", "radius", "dist_ly",
                           "dist_pc", "spectral", "spect", "category",
                           "constellation", "marker_size", "color_hex"]].values,
        hovertemplate = hover,
        name          = "Stars",
        showlegend    = False,
    ))

    # Highlighted star 
    if highlight_id is not None:
        row = df[df["id"] == highlight_id]
        if not row.empty:
            hex_col = row["color_hex"].iloc[0]
            fig.add_trace(go.Scatter(
                x    = row["bv"].values,
                y    = row["absmag"].values,
                mode = "markers",
                marker = dict(
                    color  = hex_col,
                    size   = 16,
                    line   = dict(color="white", width=2),
                    symbol = "circle",
                ),
                name      = row["name"].iloc[0],
                hoverinfo = "skip",
                showlegend= False,
            ))
            # Glow ring
            fig.add_trace(go.Scatter(
                x    = row["bv"].values,
                y    = row["absmag"].values,
                mode = "markers",
                marker = dict(
                    color  = "rgba(255,255,255,0.15)",
                    size   = 28,
                    line   = dict(width=0),
                ),
                hoverinfo  = "skip",
                showlegend = False,
            ))

    #  ZAMS line (rendered LAST so it sits on top of all star dots) 
    if show_zams:
        zams = get_zams_line()
        # Glow layer — wide, semi-transparent
        fig.add_trace(go.Scatter(
            x    = zams["bv"],
            y    = zams["absmag"],
            mode = "lines",
            line = dict(color="rgba(80,180,255,0.18)", width=10),
            hoverinfo  = "skip",
            showlegend = False,
        ))
        # Core line — crisp and bold
        fig.add_trace(go.Scatter(
            x    = zams["bv"],
            y    = zams["absmag"],
            mode = "lines",
            line = dict(color="rgba(130,200,255,0.92)", width=2.5, dash="dash"),
            name = "ZAMS",
            hovertemplate = "<b>ZAMS</b><br>B-V: %{x:.2f}<br>Abs Mag: %{y:.2f}<extra></extra>",
        ))

    #  Evolution tracks 
    if show_tracks:
        tracks = get_all_tracks()
        for track in tracks:
            is_selected = (selected_track is not None and
                           abs(track.mass - selected_track) < 0.01)
            line_width = 2.5 if is_selected else 1.4
            line_alpha = 1.0 if is_selected else 0.65
            col = track.color

            # Convert hex to rgba
            r = int(col[1:3], 16)
            g = int(col[3:5], 16)
            b = int(col[5:7], 16)
            rgba = f"rgba({r},{g},{b},{line_alpha})"

            fig.add_trace(go.Scatter(
                x    = track.all_bv,
                y    = track.all_absmag,
                mode = "lines+markers",
                line = dict(color=rgba, width=line_width, dash="solid"),
                marker = dict(
                    color = rgba,
                    size  = 5 if is_selected else 3,
                ),
                name = track.label,
                customdata = [[track.mass, track.label, track.end_state]] * len(track.all_bv),
                hovertemplate = (
                    f"<b>{track.label} Track</b><br>"
                    "Phase: %{text}<br>"
                    "B-V: %{x:.3f}<br>"
                    "Abs Mag: %{y:.2f}<br>"
                    "<extra></extra>"
                ),
                text = track.all_phase_labels,
            ))

    #  Sun marker 
    if show_sun:
        fig.add_trace(go.Scatter(
            x    = [0.65],
            y    = [4.83],
            mode = "markers+text",
            marker = dict(
                color  = "#FFD700",
                size   = 10,
                symbol = "star",
                line   = dict(color="#FFA500", width=1.5),
            ),
            text          = ["  ☀ Sun"],
            textposition  = "middle right",
            textfont      = dict(color="#FFD700", size=11),
            name          = "Sun",
            hovertemplate = "<b>The Sun</b><br>B-V: 0.65<br>Abs Mag: 4.83<br>T_eff: 5,778 K<br>Luminosity: 1.0 L☉<extra></extra>",
        ))

    #  Region labels 
    if show_labels:
        for ann in REGION_ANNOTATIONS:
            fig.add_annotation(**ann,
                xref="x", yref="y",
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
            )

    #  Layout 
    fig.update_layout(
        template    = "plotly_dark",
        plot_bgcolor  = BG_COLOR,
        paper_bgcolor = BG_COLOR,
        margin      = dict(l=60, r=20, t=20, b=60),
        height      = 680,

        xaxis = dict(
            title       = dict(text="← Hotter   B-V Color Index   Cooler →",
                               font=dict(color="#8AABDB", size=13)),
            autorange   = "reversed",
            range       = [2.1, -0.5],
            gridcolor   = GRID_COLOR,
            zerolinecolor = AXIS_COLOR,
            tickcolor   = AXIS_COLOR,
            tickfont    = dict(color="#8AABDB"),
            showspikes  = True,
            spikecolor  = "rgba(150,180,255,0.4)",
            spikethickness = 1,
        ),

        yaxis = dict(
            title       = dict(text="← Brighter   Absolute Magnitude   Dimmer →",
                               font=dict(color="#8AABDB", size=13)),
            autorange   = "reversed",
            range       = [-10, 18],
            gridcolor   = GRID_COLOR,
            zerolinecolor = AXIS_COLOR,
            tickcolor   = AXIS_COLOR,
            tickfont    = dict(color="#8AABDB"),
            showspikes  = True,
            spikecolor  = "rgba(150,180,255,0.4)",
            spikethickness = 1,
        ),

        legend = dict(
            bgcolor      = "rgba(5,15,35,0.85)",
            bordercolor  = "rgba(100,140,200,0.3)",
            borderwidth  = 1,
            font         = dict(color="#8AABDB", size=11),
            x            = 1.0,
            xanchor      = "right",
            y            = 1.0,
        ),

        hoverlabel = dict(
            bgcolor     = "rgba(8,20,50,0.95)",
            bordercolor = "rgba(100,150,255,0.4)",
            font        = dict(color="#D6E4FF", size=12, family="monospace"),
        ),

        dragmode = "zoom",
        uirevision = "hr_diagram",
    )

    return fig


#  Temperature Dual Axis  

def add_temperature_axis(fig: go.Figure) -> go.Figure:
    """
    Add a secondary X-axis showing approximate effective temperature (K)
    corresponding to the B-V color index.

    Note: Uses the Ballesteros approximation for labeling only.
    """
    tick_bv   = [-0.3, -0.1, 0.0, 0.3, 0.6, 1.0, 1.5, 2.0]
    tick_temp = [30000, 10000, 8000, 6000, 5000, 4000, 3600, 3300]

    fig.update_layout(
        xaxis2 = dict(
            overlaying   = "x",
            side         = "top",
            range        = [2.1, -0.5],
            tickvals     = tick_bv,
            ticktext     = [f"{t:,} K" for t in tick_temp],
            tickfont     = dict(color="rgba(140,170,220,0.7)", size=10),
            showgrid     = False,
            title        = dict(text="Surface Temperature (K)",
                                font=dict(color="#8AABDB", size=11)),
        )
    )
    return fig


#  Spectral Class Band Overlay 

def add_spectral_bands(fig: go.Figure) -> go.Figure:
    """
    Add faint colored vertical bands showing spectral class regions
    (O, B, A, F, G, K, M) along the B-V axis.
    """
    bands = [
        (-0.45, -0.10, "rgba(140,160,255,0.04)", "O"),
        (-0.10,  0.00, "rgba(170,190,255,0.04)", "B"),
        ( 0.00,  0.30, "rgba(210,220,255,0.04)", "A"),
        ( 0.30,  0.58, "rgba(255,255,240,0.04)", "F"),
        ( 0.58,  0.81, "rgba(255,240,200,0.04)", "G"),
        ( 0.81,  1.40, "rgba(255,200,150,0.04)", "K"),
        ( 1.40,  2.10, "rgba(255,150,100,0.04)", "M"),
    ]

    for lo, hi, color, label in bands:
        fig.add_vrect(
            x0        = lo,  x1    = hi,
            fillcolor = color,
            line_width = 0,
            layer      = "below",
            annotation_text     = label,
            annotation_position = "top left",
            annotation_font     = dict(color="rgba(150,180,230,0.5)", size=10),
        )

    return fig
