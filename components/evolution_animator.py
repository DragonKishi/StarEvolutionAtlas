"""
evolution_animator.py

 animated stellar evolution track figures for The Star Evolution Atlas.

When a user selects an evolution track, this module creates a Plotly
animation that shows a glowing star-dot traversing the H-R diagram
through its life phases, with educational labels.

Author: Parth Mishra
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from physics.evolution_data import EvolutionTrack, get_all_tracks, get_zams_line
from physics.stellar_physics import bv_to_hex_color


BG_COLOR = "#050A1A"


def build_evolution_animation(track: EvolutionTrack) -> go.Figure:
    """
    animated Plotly figure showing a star traversing its
    evolution track on the H-R diagram.

    Parameters
    
    track : EvolutionTrack
        The stellar evolution track to animate.

    Returns
    
    go.Figure
        Plotly figure with animation frames.
    """
    all_bv     = track.all_bv
    all_mag    = track.all_absmag
    all_phases = track.all_phase_labels
    all_descs  = track.all_descriptions

    n = len(all_bv)
    colors_arr = bv_to_hex_color(np.array(all_bv))

    # Base figure (track line) 
    fig = go.Figure()

    # ZAMS reference
    zams = get_zams_line()
    fig.add_trace(go.Scatter(
        x    = zams["bv"],
        y    = zams["absmag"],
        mode = "lines",
        line = dict(color="rgba(100,180,255,0.35)", width=1.5, dash="dot"),
        name = "ZAMS",
        hoverinfo = "skip",
    ))

    # All other tracks (faint background)
    all_tracks = get_all_tracks()
    for bg_track in all_tracks:
        if abs(bg_track.mass - track.mass) < 0.01:
            continue
        hex_col = bg_track.color
        r = int(hex_col[1:3], 16); g = int(hex_col[3:5], 16); b = int(hex_col[5:7], 16)
        fig.add_trace(go.Scatter(
            x    = bg_track.all_bv,
            y    = bg_track.all_absmag,
            mode = "lines",
            line = dict(color=f"rgba({r},{g},{b},0.18)", width=1),
            name = bg_track.label,
            hoverinfo = "skip",
            showlegend = False,
        ))

    # Main track (full path shown as faint background)
    hex_col = track.color
    r0 = int(hex_col[1:3], 16); g0 = int(hex_col[3:5], 16); b0 = int(hex_col[5:7], 16)
    fig.add_trace(go.Scatter(
        x    = all_bv,
        y    = all_mag,
        mode = "lines",
        line = dict(color=f"rgba({r0},{g0},{b0},0.30)", width=2),
        name = f"{track.label} (full path)",
        hoverinfo = "skip",
        showlegend = True,
    ))

    # Animated traces 
    # Trace 1: "visited" path so far (solid)
    fig.add_trace(go.Scatter(
        x    = [all_bv[0]],
        y    = [all_mag[0]],
        mode = "lines",
        line = dict(color=f"rgba({r0},{g0},{b0},0.85)", width=2.5),
        name = f"{track.label} path",
        showlegend = False,
    ))

    # Trace 2: animated star dot (glow)
    fig.add_trace(go.Scatter(
        x    = [all_bv[0]],
        y    = [all_mag[0]],
        mode = "markers+text",
        marker = dict(
            color  = colors_arr[0],
            size   = 18,
            line   = dict(color="white", width=2),
            symbol = "circle",
        ),
        text         = [f"  {all_phases[0]}"],
        textposition = "middle right",
        textfont     = dict(color="white", size=11),
        name         = "Star",
        showlegend   = False,
    ))

    # Outer glow
    fig.add_trace(go.Scatter(
        x    = [all_bv[0]],
        y    = [all_mag[0]],
        mode = "markers",
        marker = dict(
            color  = "rgba(255,255,255,0.1)",
            size   = 32,
            line   = dict(width=0),
        ),
        name       = "Glow",
        hoverinfo  = "skip",
        showlegend = False,
    ))

    # Animation frames
    frames = []
    for i in range(n):
        hex_i = colors_arr[i]
        ri = int(hex_i[1:3], 16); gi = int(hex_i[3:5], 16); bi = int(hex_i[5:7], 16)
        frames.append(go.Frame(
            data = [
                # ZAMS (static — no update needed)
                go.Scatter(x=zams["bv"], y=zams["absmag"]),
                # bg tracks (static)
                *[go.Scatter(x=bt.all_bv, y=bt.all_absmag)
                  for bt in all_tracks if abs(bt.mass - track.mass) >= 0.01],
                # full path (static)
                go.Scatter(x=all_bv, y=all_mag),
                # visited path so far
                go.Scatter(
                    x = all_bv[:i+1],
                    y = all_mag[:i+1],
                    mode = "lines",
                    line = dict(color=f"rgba({r0},{g0},{b0},0.85)", width=2.5),
                ),
                # star dot
                go.Scatter(
                    x    = [all_bv[i]],
                    y    = [all_mag[i]],
                    mode = "markers+text",
                    marker = dict(
                        color  = hex_i,
                        size   = 18,
                        line   = dict(color="white", width=2),
                    ),
                    text         = [f"  {all_phases[i]}"],
                    textposition = "middle right",
                    textfont     = dict(color="white", size=11),
                ),
                # glow
                go.Scatter(
                    x    = [all_bv[i]],
                    y    = [all_mag[i]],
                    mode = "markers",
                    marker = dict(
                        color = f"rgba({ri},{gi},{bi},0.15)",
                        size  = 35,
                        line  = dict(width=0),
                    ),
                ),
            ],
            name = str(i),
            layout = go.Layout(
                annotations = [dict(
                    x         = 0.01, y = 0.99,
                    xref      = "paper", yref = "paper",
                    text      = (
                        f"<b>{track.label}</b>  |  "
                        f"<span style='color:{hex_i}'>●</span>  "
                        f"<b>{all_phases[i]}</b><br>"
                        f"<span style='font-size:10px;color:rgba(180,200,240,0.8)'>"
                        f"{all_descs[i][:100]}</span>"
                    ),
                    showarrow  = False,
                    align      = "left",
                    font       = dict(color="#D6E4FF", size=12),
                    bgcolor    = "rgba(5,15,35,0.85)",
                    bordercolor = "rgba(100,150,255,0.3)",
                    borderpad  = 8,
                    borderwidth = 1,
                )],
            ),
        ))

    fig.frames = frames

    # Animation controls 
    fig.update_layout(
        template      = "plotly_dark",
        plot_bgcolor  = BG_COLOR,
        paper_bgcolor = BG_COLOR,
        height        = 600,
        margin        = dict(l=60, r=20, t=60, b=60),

        title = dict(
            text    = f"Stellar Evolution: {track.label} — {track.mass_description[:80]}",
            font    = dict(color="#8AABDB", size=13),
            x       = 0.5,
            xanchor = "center",
        ),

        xaxis = dict(
            title       = dict(text="← Hotter   B-V Color Index   Cooler →",
                               font=dict(color="#8AABDB", size=12)),
            autorange   = "reversed",
            range       = [2.1, -0.45],
            gridcolor   = "rgba(100,140,200,0.12)",
            tickfont    = dict(color="#8AABDB"),
        ),
        yaxis = dict(
            title       = dict(text="← Brighter   Absolute Magnitude   Dimmer →",
                               font=dict(color="#8AABDB", size=12)),
            autorange   = "reversed",
            range       = [-10, 16],
            gridcolor   = "rgba(100,140,200,0.12)",
            tickfont    = dict(color="#8AABDB"),
        ),

        updatemenus = [dict(
            type       = "buttons",
            showactive = False,
            y          = 1.08,
            x          = 0.5,
            xanchor    = "center",
            buttons    = [
                dict(
                    label  = "▶  Play",
                    method = "animate",
                    args   = [None, dict(
                        frame         = dict(duration=180, redraw=True),
                        fromcurrent   = True,
                        transition    = dict(duration=80, easing="cubic-in-out"),
                    )],
                ),
                dict(
                    label  = "⏸  Pause",
                    method = "animate",
                    args   = [[None], dict(
                        frame       = dict(duration=0, redraw=False),
                        mode        = "immediate",
                        transition  = dict(duration=0),
                    )],
                ),
            ],
            bgcolor     = "rgba(20,40,80,0.9)",
            bordercolor = "rgba(100,150,255,0.5)",
            font        = dict(color="white", size=12),
            pad         = dict(r=10, t=5, b=5, l=10),
        )],

        sliders = [dict(
            active       = 0,
            currentvalue = dict(
                prefix   = "Step: ",
                font     = dict(color="#8AABDB", size=11),
                visible  = True,
            ),
            steps = [dict(
                args  = [[str(i)], dict(
                    frame       = dict(duration=100, redraw=True),
                    mode        = "immediate",
                    transition  = dict(duration=50),
                )],
                label  = str(i),
                method = "animate",
            ) for i in range(n)],
            pad       = dict(t=50, b=10),
            len       = 0.9,
            x         = 0.05,
            y         = 0.0,
            bgcolor   = "rgba(20,40,80,0.5)",
            bordercolor = "rgba(100,150,255,0.3)",
            tickcolor = "rgba(100,150,255,0.4)",
            font      = dict(color="#8AABDB", size=9),
        )],

        hoverlabel = dict(
            bgcolor     = "rgba(8,20,50,0.95)",
            bordercolor = "rgba(100,150,255,0.4)",
            font        = dict(color="#D6E4FF", size=12),
        ),
    )

    return fig


def get_phase_info_html(track: EvolutionTrack) -> str:
    """
    Return HTML for a phase-by-phase breakdown of the track.

    Parameters
    
    track : EvolutionTrack

    Returns
    
    str
        HTML string for use in st.markdown().
    """
    rows = ""
    for phase in track.phases:
        rows += f"""
        <tr>
            <td style='padding:6px 12px; color:#A0C4FF; font-weight:600;'>{phase.name}</td>
            <td style='padding:6px 12px; color:#FFD700;'>{phase.duration}</td>
            <td style='padding:6px 12px; color:#D6E4FF; font-size:0.88em;'>{phase.description}</td>
        </tr>
        """
    return f"""
    <table style='width:100%; border-collapse:collapse; font-family:sans-serif;
                  background:rgba(5,15,35,0.6); border-radius:8px; overflow:hidden;'>
        <thead>
            <tr style='background:rgba(30,60,120,0.5);'>
                <th style='padding:8px 12px; text-align:left; color:#8AABDB;'>Phase</th>
                <th style='padding:8px 12px; text-align:left; color:#8AABDB;'>Duration</th>
                <th style='padding:8px 12px; text-align:left; color:#8AABDB;'>Description</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <div style='margin-top:8px; padding:8px 12px; background:rgba(20,40,80,0.4);
                border-radius:6px; font-family:sans-serif;'>
        <span style='color:#8AABDB;'>End State:</span>
        <span style='color:#FFD700; font-size:1.1em; margin-left:8px;'>
            {track.end_state_icon} {track.end_state}
        </span>
    </div>
    """
