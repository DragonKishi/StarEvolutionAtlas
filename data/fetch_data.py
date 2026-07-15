"""
fetch_data.py

Downloads and pre-processes the HYG v3.8 star catalog for The Star Evolution Atlas (SEA).

The HYG database (Hipparcos + Yale Bright Star + Gliese) contains ~119,615 stars
with positions, magnitudes, color indices, and spectral types.

Run this script once to generate data/hyg_processed.csv:
    python data/fetch_data.py

Data Source:
    https://github.com/astronexus/HYG-Database (hyg/v3/hyg_v38.csv.gz)
    License: CC BY-SA 2.5

Author: Parth Mishra
"""

import gzip
import io
import os
import sys
import requests
import pandas as pd
import numpy as np

# Allow importing from parent package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from physics.stellar_physics import (
    bv_to_temperature, absmag_to_luminosity, bv_to_hex_color,
    spectral_class, stellar_category, estimate_radius
)

#  Configuration 
# HYG v3.8 — latest v3 release, gzip compressed CSV
HYG_URL = (
    "https://raw.githubusercontent.com/astronexus/HYG-Database/main/hyg/v3/hyg_v38.csv.gz"
)
HYG_IS_GZIP = True   # The downloaded file is gzip-compressed

DATA_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(DATA_DIR, "hyg_processed.csv")
RAW_PATH    = os.path.join(DATA_DIR, "hyg_raw.csv.gz")   # stored as gzip


def download_hyg(force: bool = False) -> pd.DataFrame:

    """

    Download the HYG v3 catalog CSV, or load from local cache.

    Parameters
    
    force : bool
        If True, re-download even if local cache exists.

    Returns
    pd.DataFrame
        Raw HYG data.

    """
    if os.path.exists(RAW_PATH) and not force:
        print(f"[SEA] Loading cached raw catalog: {RAW_PATH}")
        if HYG_IS_GZIP:
            return pd.read_csv(RAW_PATH, compression="gzip", low_memory=False)
        return pd.read_csv(RAW_PATH, low_memory=False)

    print(f"[SEA] Downloading HYG v3 catalog from:\n  {HYG_URL}")
    print("      This is ~30 MB — please wait...")

    resp = requests.get(HYG_URL, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    chunks = []

    for chunk in resp.iter_content(chunk_size=65536):
        chunks.append(chunk)
        downloaded += len(chunk)
        if total:
            pct = 100 * downloaded / total
            print(f"\r      {pct:5.1f}% ({downloaded // 1024} KB / {total // 1024} KB)", end="", flush=True)

    print("\n[SEA] Download complete. Caching raw file...")
    raw_bytes = b"".join(chunks)

    with open(RAW_PATH, "wb") as f:
        f.write(raw_bytes)

    print("[SEA] Decompressing catalog...")
    if HYG_IS_GZIP:
        with gzip.open(io.BytesIO(raw_bytes), 'rt', encoding='utf-8') as gz:
            df = pd.read_csv(gz, low_memory=False)
    else:
        df = pd.read_csv(io.BytesIO(raw_bytes), low_memory=False)

    print(f"[SEA] Loaded {len(df):,} stars.")
    return df


def process_hyg(df_raw: pd.DataFrame) -> pd.DataFrame:

    """
    Clean and enrich the raw HYG catalog.

    Steps:
      1. Drop rows missing B-V (ci) or absolute magnitude (absmag)
      2. Drop the Sun (id==0) and unphysical entries
      3. Compute derived quantities: temperature, luminosity, radius, color, category
      4. Rename / select columns for the app

    Parameters
    df_raw : pd.DataFrame
        Raw HYG catalog.

    Returns
    
    pd.DataFrame
        Cleaned, enriched star table.
    """

    
    print("[SEA] Processing raw catalog...")
    df = df_raw.copy()

    #  Step 1: Filter to rows with usable photometry 
    df = df[df["ci"].notna()].copy()          # B-V color index
    df = df[df["absmag"].notna()].copy()      # Absolute magnitude
    df = df[df["dist"].notna()].copy()        # Distance (parsecs)

    # Remove entries with invalid distances or magnitudes
    df = df[df["dist"] > 0].copy()
    df = df[df["dist"] < 100_000].copy()      # Remove objects with distance >100 kpc

    # Remove unphysical B-V values
    df = df[(df["ci"] > -0.5) & (df["ci"] < 3.0)].copy()

    # Remove unphysical absolute magnitudes
    df = df[(df["absmag"] > -10) & (df["absmag"] < 20)].copy()

    print(f"[SEA]   After photometry filter: {len(df):,} stars")

    #  Step 2: Compute derived quantities 
    bv_arr      = df["ci"].values
    absmag_arr  = df["absmag"].values
    dist_arr    = df["dist"].values

    temperature  = bv_to_temperature(bv_arr)
    luminosity   = absmag_to_luminosity(absmag_arr)
    radius       = estimate_radius(luminosity, temperature)
    colors       = bv_to_hex_color(bv_arr)
    spec_class   = spectral_class(bv_arr)
    category     = stellar_category(absmag_arr, bv_arr)

    dist_ly     = dist_arr * 3.26156      # parsecs → light-years
    app_mag     = df.get("mag", pd.Series(np.nan, index=df.index))

    #  Step 3: Build output DataFrame 
    # Star names: prefer proper > Bayer/Flamsteed > Hipparcos > HD
    def get_name(row):
        if pd.notna(row.get("proper")) and str(row.get("proper", "")).strip():
            return str(row["proper"]).strip().title()
        if pd.notna(row.get("bf")) and str(row.get("bf", "")).strip():
            return str(row["bf"]).strip()
        if pd.notna(row.get("hip")) and row.get("hip", 0) > 0:
            return f"HIP {int(row['hip'])}"
        if pd.notna(row.get("hd")) and row.get("hd", 0) > 0:
            return f"HD {int(row['hd'])}"
        return f"Star #{int(row.get('id', 0))}"

    names = df.apply(get_name, axis=1)

    # Constellation
    con = df.get("con", pd.Series("", index=df.index)).fillna("").astype(str)

    out = pd.DataFrame({
        "id":           df["id"].values,
        "name":         names.values,
        "ra":           df["ra"].values,          # Right Ascension (hours)
        "dec":          df["dec"].values,          # Declination (degrees)
        "dist_pc":      dist_arr,                  # Distance (parsecs)
        "dist_ly":      dist_ly,                   # Distance (light-years)
        "absmag":       absmag_arr,                # Absolute magnitude (V)
        "app_mag":      app_mag.values,            # Apparent magnitude
        "bv":           bv_arr,                    # B-V color index
        "temperature":  temperature,               # Effective temperature (K)
        "luminosity":   luminosity,                # Luminosity (L☉)
        "radius":       radius,                    # Radius estimate (R☉)
        "color_hex":    colors,                    # Hex color string
        "spectral":     spec_class.astype(str),    # Spectral class letter
        "category":     category.astype(str),      # Broad stellar category
        "constellation": con.values,               # IAU constellation code
        "spect":        df.get("spect", pd.Series("", index=df.index)).fillna("").values,  # Full spectrum
        "x":            df.get("x",   pd.Series(np.nan, index=df.index)).values,
        "y":            df.get("y",   pd.Series(np.nan, index=df.index)).values,
        "z":            df.get("z",   pd.Series(np.nan, index=df.index)).values,
    })

    #  Step 4: Clamp to physically plausible marker sizes 
    # Log-luminosity for marker size (clamp between 0.5 and 20)
    log_lum = np.log10(np.clip(out["luminosity"].values, 1e-4, 1e6))
    size    = np.interp(log_lum, [-4, 6], [2, 18])
    out["marker_size"] = size

    print(f"[SEA]   Final processed catalog: {len(out):,} stars")

    # Category summary
    cats = out["category"].value_counts()
    for cat, cnt in cats.items():
        print(f"[SEA]     {cat}: {cnt:,}")

    return out


def save_processed(df: pd.DataFrame, path: str = OUTPUT_PATH) -> None:
    """Save the processed DataFrame to CSV."""
    df.to_csv(path, index=False, float_format="%.6g")
    size_kb = os.path.getsize(path) // 1024
    print(f"[SEA] Saved: {path}  ({size_kb} KB, {len(df):,} rows)")


def main():
    """Full pipeline: download → process → save."""
    print("=" * 60)
    print("  The Star Evolution Atlas — Data Preparation")
    print("=" * 60)

    df_raw  = download_hyg(force=False)
    df_proc = process_hyg(df_raw)
    save_processed(df_proc)

    print("=" * 60)
    print("  Done! hyg_processed.csv is ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()
