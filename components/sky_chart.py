"""
sky_chart.py

Builds the sky position chart for a selected star.

Shows the star's position in equatorial coordinates (RA/Dec) on a
pseudo-Mollweide projection with surrounding neighborhood stars.

Author: Parth Mishra
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go


BG_COLOR = "#050A1A"


def build_sky_chart(
    selected_star: pd.Series | None,
    df: pd.DataFrame,
    neighborhood_radius_deg: float = 30.0,
    max_neighbor_stars: int = 2000,
) -> go.Figure:

    """

    Build a sky chart showing the selected star's position and its surroundings.

    Parameters
    
    selected_star : pd.Series or None
        A single row from the star DataFrame. If None, shows all stars.
    df : pd.DataFrame
        Full processed star catalog.
    neighborhood_radius_deg : float
        Angular radius (degrees) around the selected star to show neighbors.
    max_neighbor_stars : int
        Maximum number of neighbor stars to render.

    Returns
    
    go.Figure
    """

    fig = go.Figure()

    # Convert RA hours → degrees
    df = df.copy()
    df["ra_deg"] = df["ra"] * 15.0  # 1 hour = 15 degrees

    if selected_star is not None:
        sel_ra_deg  = float(selected_star["ra"]) * 15.0
        sel_dec_deg = float(selected_star["dec"])

        #  Find neighborhood stars 
        ra_diff  = np.abs(df["ra_deg"].values - sel_ra_deg)
        ra_diff  = np.minimum(ra_diff, 360 - ra_diff)          # handle wrap-around
        dec_diff = np.abs(df["dec"].values - sel_dec_deg)

        # Approximate angular distance
        ang_dist = np.sqrt(ra_diff**2 + dec_diff**2)
        nearby   = df[ang_dist < neighborhood_radius_deg].copy()

        # Limit to max stars
        if len(nearby) > max_neighbor_stars:
            nearby = nearby.nsmallest(max_neighbor_stars, "absmag")

        #  Background stars 
        if len(nearby) > 0:
            neighbor_ids = nearby["id"].values
            is_selected  = nearby["id"].values == int(selected_star["id"])
            bg_nearby    = nearby[~is_selected]

            if len(bg_nearby) > 0:
                fig.add_trace(go.Scatter(
                    x    = bg_nearby["ra_deg"].values,
                    y    = bg_nearby["dec"].values,
                    mode = "markers",
                    marker = dict(
                        color   = bg_nearby["color_hex"].values,
                        size    = np.clip(bg_nearby["marker_size"].values * 0.7, 1.5, 10),
                        opacity = 0.65,
                        line    = dict(width=0),
                    ),
                    hovertemplate = (
                        "<b>%{customdata[0]}</b><br>"
                        "RA: %{x:.2f}°  Dec: %{y:.2f}°<br>"
                        "Abs Mag: %{customdata[1]:.2f}<br>"
                        "Distance: %{customdata[2]:.1f} ly<br>"
                        "<extra></extra>"
                    ),
                    customdata = bg_nearby[["name", "absmag", "dist_ly"]].values,
                    name       = "Nearby Stars",
                    showlegend = False,
                ))

        #  Selected star 
        hex_col = str(selected_star.get("color_hex", "#FFD700"))
        r = int(hex_col[1:3], 16) if hex_col.startswith("#") else 255
        g = int(hex_col[3:5], 16) if hex_col.startswith("#") else 200
        b = int(hex_col[5:7], 16) if hex_col.startswith("#") else 0

        # Glow effect (two rings)
        for sz, alpha in [(40, 0.08), (25, 0.18), (14, 0.9)]:
            fig.add_trace(go.Scatter(
                x    = [sel_ra_deg],
                y    = [sel_dec_deg],
                mode = "markers",
                marker = dict(
                    color  = f"rgba({r},{g},{b},{alpha})" if sz > 14 else hex_col,
                    size   = sz,
                    line   = dict(width=0),
                ),
                hoverinfo  = "skip",
                showlegend = False,
            ))

        # Star label
        star_name = str(selected_star.get("name", "Selected Star"))
        fig.add_annotation(
            x         = sel_ra_deg,
            y         = sel_dec_deg + 2.0,
            text      = f"<b>{star_name}</b>",
            showarrow = False,
            font      = dict(color=hex_col, size=12),
            xref      = "x", yref = "y",
        )

        #  Crosshair lines 
        fig.add_hline(y=sel_dec_deg, line=dict(color="rgba(255,255,255,0.08)", width=1, dash="dot"))
        fig.add_vline(x=sel_ra_deg,  line=dict(color="rgba(255,255,255,0.08)", width=1, dash="dot"))

        #  Coordinate annotations 
        fig.add_annotation(
            x=sel_ra_deg, y=-80,
            text=f"RA {sel_ra_deg/15:.2f}h ({sel_ra_deg:.1f}°)",
            showarrow=False, font=dict(color="rgba(150,180,230,0.7)", size=10),
        )
        fig.add_annotation(
            x=15.0, y=sel_dec_deg,
            text=f"Dec {sel_dec_deg:+.2f}°",
            showarrow=False, font=dict(color="rgba(150,180,230,0.7)", size=10),
        )

        x_range = [sel_ra_deg - neighborhood_radius_deg,
                   sel_ra_deg + neighborhood_radius_deg]
        y_range = [sel_dec_deg - neighborhood_radius_deg,
                   sel_dec_deg + neighborhood_radius_deg]

        title_text = f"Sky Position: {star_name}"

    else:
        # Show all stars in full-sky view
        sample = df.sample(min(5000, len(df)), random_state=42)
        fig.add_trace(go.Scatter(
            x    = sample["ra_deg"].values,
            y    = sample["dec"].values,
            mode = "markers",
            marker = dict(
                color   = sample["color_hex"].values,
                size    = np.clip(sample["marker_size"].values * 0.5, 1, 6),
                opacity = 0.5,
                line    = dict(width=0),
            ),
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "RA: %{x:.1f}°  Dec: %{y:.1f}°<br>"
                "<extra></extra>"
            ),
            customdata = sample[["name"]].values,
            name       = "Stars",
            showlegend = False,
        ))
        x_range = [0, 360]
        y_range = [-90, 90]
        title_text = "Full Sky Map — Select a star in the H-R Diagram"

    #  Celestial equator 
    fig.add_hline(y=0, line=dict(color="rgba(100,150,255,0.2)", width=1, dash="dash"))

    #  Layout 
    fig.update_layout(
        template      = "plotly_dark",
        plot_bgcolor  = BG_COLOR,
        paper_bgcolor = BG_COLOR,
        height        = 500,
        margin        = dict(l=60, r=20, t=50, b=50),
        title         = dict(
            text  = title_text,
            font  = dict(color="#8AABDB", size=14),
            x     = 0.5,
            xanchor = "center",
        ),
        xaxis = dict(
            title       = dict(text="Right Ascension (degrees)", font=dict(color="#8AABDB")),
            range       = x_range,
            gridcolor   = "rgba(80,120,180,0.1)",
            tickcolor   = "rgba(100,140,200,0.4)",
            tickfont    = dict(color="#8AABDB", size=10),
            zeroline    = False,
            tickvals    = list(range(0, 361, 30)),
            ticktext    = [f"{h}h" for h in range(0, 25, 2)],
        ),
        yaxis = dict(
            title       = dict(text="Declination (degrees)", font=dict(color="#8AABDB")),
            range       = y_range,
            gridcolor   = "rgba(80,120,180,0.1)",
            tickcolor   = "rgba(100,140,200,0.4)",
            tickfont    = dict(color="#8AABDB", size=10),
            zeroline    = False,
        ),
        hoverlabel = dict(
            bgcolor     = "rgba(8,20,50,0.95)",
            bordercolor = "rgba(100,150,255,0.4)",
            font        = dict(color="#D6E4FF", size=12),
        ),
    )

    return fig
