"""
star_detail.py

Renders a rich star information panel in the Streamlit sidebar.

When a user clicks a star on the H-R diagram, this module
generates a detailed HTML panel with all physical properties,
a color sphere SVG, and contextual stellar facts.

Author: Parth Mishra
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from physics.stellar_physics import (
    bv_to_hex_color, bv_to_rgba, spectral_class,
    stellar_category, main_sequence_lifetime
)


#  Spectral class descriptions 
_SPECTRAL_DESCRIPTIONS = {
    "O": ("O-type Supergiant", "Extremely hot (~30,000–50,000 K), blue-violet, and rare. "
          "These monsters are so luminous they blow off mass through powerful stellar winds."),
    "B": ("B-type Star", "Hot (10,000–30,000 K) blue-white stars. Many famous stars like Rigel "
          "and Spica are B-type. They live fast and die young as supernovae."),
    "A": ("A-type Star", "White to blue-white (7,500–10,000 K). Sirius, the brightest star in "
          "our night sky, is an A-type star. Hydrogen absorption lines dominate their spectra."),
    "F": ("F-type Star", "Yellow-white (6,000–7,500 K), slightly hotter than the Sun. "
          "Procyon and Canopus are F-type. Often called 'slightly super-solar' stars."),
    "G": ("G-type Star (like the Sun!)", "Yellow (5,200–6,000 K). Our Sun is a G2V star. "
          "G-type stars have stable, long main-sequence lives of ~10 billion years."),
    "K": ("K-type Star", "Orange (3,700–5,200 K), cooler and dimmer than the Sun. "
          "Known as 'Goldilocks stars' — potentially ideal for habitable planets. "
          "Epsilon Eridani is an example."),
    "M": ("M-type Red Dwarf", "Cool (2,400–3,700 K), dim, and the most common stars in the galaxy. "
          "Proxima Centauri is an M-type red dwarf — our closest stellar neighbor. "
          "They can live for trillions of years."),
    "?": ("Unknown Type", "Spectral classification not available for this star."),
}

_CATEGORY_DESCRIPTIONS = {
    "Main Sequence": "This is a main-sequence (dwarf) star, actively fusing hydrogen into helium "
                     "in its core — the most stable phase of stellar evolution.",
    "Giant":         "An evolved giant star. Hydrogen in the core is depleted; the star has "
                     "expanded dramatically as shell burning drives its envelope outward.",
    "Supergiant":    "A rare and massive supergiant — one of the most luminous objects in the galaxy. "
                     "These stars have short lives measured in millions of years.",
    "White Dwarf":   "A stellar remnant — the dense, hot core of a dead star. No fusion occurs; "
                     "it slowly radiates its remaining thermal energy over billions of years.",
    "Unknown":       "Classification uncertain based on available photometric data.",
}


def _star_color_svg(hex_color: str, size: int = 80) -> str:
    """Generate an SVG radial gradient sphere in the star's color."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    # Brighten center highlight
    r_h = min(255, r + 80)
    g_h = min(255, g + 80)
    b_h = min(255, b + 80)

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"
         xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="starGrad" cx="38%" cy="35%" r="65%">
          <stop offset="0%"   stop-color="rgb({r_h},{g_h},{b_h})" stop-opacity="1"/>
          <stop offset="50%"  stop-color="rgb({r},{g},{b})"       stop-opacity="1"/>
          <stop offset="100%" stop-color="rgb({max(0,r-60)},{max(0,g-60)},{max(0,b-60)})"
                stop-opacity="0.9"/>
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 5}"
              fill="url(#starGrad)" filter="url(#glow)"/>
    </svg>
    """


def render_star_panel(star: pd.Series) -> str:

    """
    
    Generate a full HTML detail panel for a selected star.

    Parameters
    
    star : pd.Series
        A single row from the processed star DataFrame.

    Returns
    
    str
        HTML string ready for st.markdown(..., unsafe_allow_html=True).

    """
    name    = str(star.get("name", "Unknown Star"))
    bv      = float(star.get("bv", 0.65))
    absmag  = float(star.get("absmag", 4.83))
    temp    = float(star.get("temperature", 5778))
    lum     = float(star.get("luminosity", 1.0))
    radius  = float(star.get("radius", 1.0))
    dist_ly = float(star.get("dist_ly", 0))
    dist_pc = float(star.get("dist_pc", 0))
    spec    = str(star.get("spectral", "G"))
    spect   = str(star.get("spect", "G2V"))
    cat     = str(star.get("category", "Main Sequence"))
    con     = str(star.get("constellation", "—")).upper()
    ra      = float(star.get("ra", 0))
    dec     = float(star.get("dec", 0))
    app_mag = star.get("app_mag", None)

    hex_col = str(star.get("color_hex", bv_to_hex_color(bv)))

    spec_title, spec_desc = _SPECTRAL_DESCRIPTIONS.get(spec, _SPECTRAL_DESCRIPTIONS["?"])
    cat_desc = _CATEGORY_DESCRIPTIONS.get(cat, "")

    # Apparent magnitude string
    app_mag_str = f"{float(app_mag):.2f}" if app_mag is not None and str(app_mag) not in ("nan", "None", "") else "—"

    # Distance string
    if dist_ly < 10:
        dist_str = f"{dist_ly:.2f} ly ({dist_pc:.2f} pc)"
    elif dist_ly < 10000:
        dist_str = f"{dist_ly:,.1f} ly ({dist_pc:,.1f} pc)"
    else:
        dist_str = f"{dist_ly:,.0f} ly ({dist_pc:,.0f} pc)"

    # Luminosity string
    if lum > 1e6:
        lum_str = f"{lum:.2e} L☉"
    elif lum > 1000:
        lum_str = f"{lum:,.0f} L☉"
    else:
        lum_str = f"{lum:.3g} L☉"

    # Radius string
    if radius > 1000:
        radius_str = f"~{radius:,.0f} R☉"
    elif radius > 10:
        radius_str = f"{radius:.1f} R☉"
    else:
        radius_str = f"{radius:.3f} R☉"

    # Temperature
    temp_str = f"{temp:,.0f} K"

    # Mass estimate via piecewise mass-luminosity relation (M-L relation)
    try:
        import math, numpy as np
        lum_safe = float(lum)
        if not math.isfinite(lum_safe) or lum_safe <= 0:
            mass_est = None
        elif lum_safe < 0.033:              # very low-mass: L ∝ M^2.3
            mass_est = (lum_safe / 0.23) ** (1.0 / 2.3)
        elif lum_safe < 16:                 # solar neighbourhood: L ∝ M^4
            mass_est = lum_safe ** 0.25
        elif lum_safe < 54_000:             # mid-range: L ∝ M^3.5
            mass_est = (lum_safe / 1.4) ** (1.0 / 3.5)
        else:                               # very massive: L ∝ 3200 M
            mass_est = lum_safe / 3200.0
    except Exception:
        mass_est = None

    if mass_est is None or not math.isfinite(mass_est):
        mass_str = "—"
    elif mass_est < 0.1:
        mass_str = f"~{mass_est:.3f} M☉"
    elif mass_est < 10:
        mass_str = f"~{mass_est:.2f} M☉"
    else:
        mass_str = f"~{mass_est:.1f} M☉"

    # RA/Dec formatting
    ra_h  = int(ra)
    ra_m  = int((ra - ra_h) * 60)
    ra_s  = ((ra - ra_h) * 60 - ra_m) * 60
    dec_d = int(abs(dec))
    dec_m = int((abs(dec) - dec_d) * 60)
    sign  = "+" if dec >= 0 else "−"
    coord_str = f"{ra_h:02d}h {ra_m:02d}m {ra_s:04.1f}s  /  {sign}{dec_d:02d}° {dec_m:02d}'"

    svg = _star_color_svg(hex_col, size=72)

    # Category badge color
    badge_colors = {
        "Main Sequence": "#3A7BFF",
        "Giant":         "#FF8C42",
        "Supergiant":    "#FF3860",
        "White Dwarf":   "#A0C4FF",
        "Unknown":       "#666699",
    }
    badge_col = badge_colors.get(cat, "#666699")

    html = f"""
<div style="
    background: linear-gradient(135deg, rgba(10,20,50,0.95) 0%, rgba(5,15,35,0.98) 100%);
    border: 1px solid rgba(100,150,255,0.25);
    border-radius: 14px;
    padding: 20px 16px;
    font-family: 'Segoe UI', sans-serif;
    color: #D6E4FF;
    margin-bottom: 12px;
">
  <!-- Header -->
  <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
    <div style="flex-shrink:0;">{svg}</div>
    <div>
      <div style="font-size:1.25em; font-weight:700; color:white; letter-spacing:0.5px;">
        {name}
      </div>
      <div style="font-size:0.82em; color:#8AABDB; margin-top:3px;">
        {spec_title}
      </div>
      <div style="margin-top:6px;">
        <span style="
            background:{badge_col}22; color:{badge_col};
            border:1px solid {badge_col}55; border-radius:20px;
            padding:2px 10px; font-size:0.75em; font-weight:600;
        ">{cat}</span>
        {f'<span style="margin-left:6px; background:rgba(255,215,0,0.1); color:#FFD700; border:1px solid rgba(255,215,0,0.3); border-radius:20px; padding:2px 10px; font-size:0.75em;">{spect}</span>' if spect and spect not in ("", "nan") else ""}
      </div>
    </div>
  </div>

  <hr style="border:none; border-top:1px solid rgba(100,150,255,0.15); margin:12px 0;">

  <!-- Physical Properties -->
  <div style="font-size:0.78em; color:#8AABDB; font-weight:600; letter-spacing:1px;
              text-transform:uppercase; margin-bottom:8px;">Physical Properties</div>
  <table style="width:100%; border-collapse:collapse; font-size:0.88em;">
    {_prop_row("🌡 Temperature",   temp_str,    hex_col)}
    {_prop_row("✨ Luminosity",    lum_str,     "#FFD700")}
    {_prop_row("🪐 Mass (est.)",   mass_str,    "#C8A2FF")}
    {_prop_row("📏 Radius",        radius_str,  "#A0C4FF")}
    {_prop_row("🎨 B-V Index",     f"{bv:.3f}", hex_col)}
    {_prop_row("⭐ Abs Magnitude", f"{absmag:.2f}", "#D6E4FF")}
    {_prop_row("👁 App Magnitude", app_mag_str, "#D6E4FF")}
  </table>

  <hr style="border:none; border-top:1px solid rgba(100,150,255,0.15); margin:12px 0;">

  <!-- Location -->
  <div style="font-size:0.78em; color:#8AABDB; font-weight:600; letter-spacing:1px;
              text-transform:uppercase; margin-bottom:8px;">Location</div>
  <table style="width:100%; border-collapse:collapse; font-size:0.88em;">
    {_prop_row("📡 Coordinates",  coord_str,  "#C0D8FF")}
    {_prop_row("📏 Distance",     dist_str,   "#A0C4FF")}
    {_prop_row("🌌 Constellation", con if con and con != "NAN" else "—", "#D6E4FF")}
  </table>

  <hr style="border:none; border-top:1px solid rgba(100,150,255,0.15); margin:12px 0;">

  <!-- Description -->
  <div style="font-size:0.82em; color:#9ABADF; line-height:1.55; margin-bottom:8px;">
    {spec_desc}
  </div>
  <div style="font-size:0.80em; color:#7A9ABF; line-height:1.5; font-style:italic;">
    {cat_desc}
  </div>
</div>
"""
    return html


def _prop_row(label: str, value: str, color: str = "#D6E4FF") -> str:
    """Build a two-column property table row."""
    return f"""
    <tr>
        <td style="padding:4px 0; color:#6A8ABF; white-space:nowrap;">{label}</td>
        <td style="padding:4px 0 4px 12px; color:{color}; font-weight:500;
                   word-break:break-word;">{value}</td>
    </tr>
    """


def render_no_star_selected() -> str:
    """HTML shown when no star is selected."""
    return """
<div style="
    background: rgba(10,20,50,0.6);
    border: 1px solid rgba(100,150,255,0.15);
    border-radius: 14px;
    padding: 24px 16px;
    text-align: center;
    font-family: sans-serif;
    color: rgba(140,170,220,0.7);
">
  <div style="font-size:2.5em; margin-bottom:10px;">🌌</div>
  <div style="font-size:0.95em; font-weight:600; color:#8AABDB;">No Star Selected</div>
  <div style="font-size:0.82em; margin-top:8px; line-height:1.5;">
    Click any star on the H-R Diagram to explore its physical properties,
    position in the sky, and place in the stellar zoo.
  </div>
</div>
"""
