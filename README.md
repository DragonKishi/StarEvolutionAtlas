# The Star Evolution Atlas (SEA)
# Author: Parth Mishra

> **The single most important diagram in stellar astrophysics — now interactive.**

The Star Evolution Atlas (SEA) is a fully interactive Hertzsprung-Russell Diagram Explorer built with Python, Streamlit, and Plotly. It visualizes **119,000+ real stars** from the HYG catalog (ESA Hipparcos data), overlays **theoretical stellar evolution tracks**, and lets you click any star to see its position in the night sky.

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Data](https://img.shields.io/badge/Data-HYG%20v3%20(Hipparcos)-blue)](https://github.com/astronexus/HYG-Database)

---

## Features

| Feature | Description |

| **Interactive H-R Diagram** | 100k+ real stars rendered via WebGL. Click any star for      details. |

| **Real Star Data** | HYG v3 database — Hipparcos + Yale Bright Star + Gliese catalogs |

| **Stellar Filters** | Filter by distance, spectral class, magnitude, and stellar category |

| **Star Detail Panel** | Temperature, luminosity, radius, distance, coordinates — all computed |

| **Sky Chart** | Click a star → see its RA/Dec position on an equatorial sky map |

| **Evolution Tracks** | Overlay theoretical tracks for 0.8, 1, 2, 5, 10, 25 M☉ stars |

| **Evolution Animation** | Watch a star traverse its entire life in an animated H-R diagram |

| **Physics Guide** | In-app educational reference explaining all the astrophysics |

| **Dark Space Theme** | Full custom CSS with glassmorphism panels, glow effects, gradients |

| **Spectral Bands** | Toggle color-coded regions for O/B/A/F/G/K/M spectral classes |

| **ZAMS Line** | Zero-Age Main Sequence reference overlay |

| **Star Search** | Search by name (e.g. "Betelgeuse", "Sirius", "HIP 24436") |


---

## The Physics

### The Hertzsprung-Russell Diagram

The H-R diagram is a scatter plot of stellar **luminosity** (or absolute magnitude) on the vertical axis versus **surface temperature** (or color index B-V) on the horizontal axis. Stars are **not** randomly distributed; they cluster into distinct populations that reveal the physics of stellar interiors and evolution.

```
Luminosity (L☉)         H-R DIAGRAM
1,000,000 ┤ Hypergiants ████████████████
  100,000 ┤ Supergiants ██████████████
   10,000 ┤ Giants      ████████████
    1,000 ┤            ███████████████ ← Main Sequence
      100 ┤           ██████████████
       10 ┤ Sun →    ██████████████
        1 ┤  ☀       ██████████████
      0.1 ┤          ██████████████
     0.01 ┤ White Dwarfs ████████
   0.001 ┤
          └─────────────────────────────
           O    B    A    F    G    K    M    ← Spectral Type
          Hot ←────────────────────→ Cool
         (40,000 K)              (3,000 K)
```

### The Main Sequence

About 90% of all stars lie on the main sequence — a broad diagonal band where stars fuse **hydrogen into helium** in their cores. Position is determined almost entirely by **initial mass**:

| Mass (M☉) | Type | Temperature | Luminosity | Lifetime |

| 40       | O   | ~40,000 K | ~400,000 L☉ | ~4 Myr   |
| 10       | B   | ~20,000 K | ~10,000 L☉  | ~30 Myr  |
| 2        | A   | ~9,000 K  | ~25 L☉      | ~1.5 Gyr |
| 1 (Sun)  | G   | ~5,800 K  | 1.0 L☉      | ~10 Gyr  |
| 0.5      | K   | ~4,200 K  | ~0.08 L☉    | ~70 Gyr  |
| 0.2      | M   | ~3,200 K  | ~0.005 L☉   | ~trillion yr |

### Stellar Evolution

All stars follow the same basic sequence, but the endpoint depends on mass:

**Low-mass stars (< 8 M☉) — like the Sun:**
```
Protostar → Pre-MS (Hayashi track) → ZAMS → Main Sequence → 
Subgiant → Red Giant Branch → Helium Flash → Horizontal Branch → 
AGB → Planetary Nebula → White Dwarf
```

**High-mass stars (> 8 M☉):**
```
Protostar → ZAMS → Main Sequence → Supergiant → 
(Wolf-Rayet / LBV for very massive) → Type II Supernova → 
Neutron Star (M < ~25 M☉) or Black Hole (M > ~25 M☉)
```

### Key Formulas

**B-V Color Index → Effective Temperature** (Ballesteros 2012):
```
T_eff = 4600 × [ 1/(0.92·BV + 1.7) + 1/(0.92·BV + 0.62) ]  [Kelvin]
```

**Absolute Magnitude → Luminosity** (solar units):
```
L / L☉ = 10^[(M☉ − M) / 2.5]    where M☉ = 4.83
```

**Stellar Radius** (Stefan-Boltzmann law):
```
R / R☉ = √(L/L☉) × (T☉/T)²    where T☉ = 5778 K
```

**Main-Sequence Lifetime** (approximate):
```
τ_MS ≈ 10 × (M/M☉)^(−2.5)  [Gyr]
```

### Spectral Classification

Stars are classified O-B-A-F-G-K-M from hottest to coolest:

| Class | B-V Range | T_eff (K) | Color | 

| O | < −0.1  | > 30,000 | Blue-violet   | 
| B | −0.1–0  | 10,000–30,000 | Blue-white |
| A | 0–0.3   | 7,500–10,000 | White      |
| F | 0.3–0.58| 6,000–7,500 | Yellow-white| 
| G | 0.58–0.81| 5,200–6,000| Yellow      | 
| K | 0.81–1.4 | 3,700–5,200| Orange      | 
| M | > 1.4   | < 3,700   | Red-orange  | 

---

## Code Structure

```
H-R Diagram/
│
├── app.py                     #  Main Streamlit application (entry point)
├── requirements.txt           # Python dependencies
│
├── .streamlit/
│   └── config.toml            # Dark space theme configuration
│
├── data/
│   ├── fetch_data.py          # HYG catalog download & pre-processing pipeline
│   ├── hyg_processed.csv      # Pre-processed star data (generated on first run)
│   └── hyg_raw.csv            # Raw HYG download cache (auto-generated, ~30 MB)
│
├── physics/
│   ├── stellar_physics.py     # Core formulas: B-V→T, luminosity, radius, colors
│   └── evolution_data.py      # Theoretical evolution track data (Padova/Geneva)
│
└── components/
    ├── hr_diagram.py          # Plotly H-R diagram figure builder (WebGL)
    ├── sky_chart.py           # Sky position chart (equatorial coordinates)
    ├── evolution_animator.py  # Animated evolution track figure with frames
    └── star_detail.py         # Star info HTML panel renderer
```

### Key Design Decisions

- **WebGL rendering** (`go.Scattergl`) — allows 100k+ stars at 60fps without browser lag
- **Pre-processed CSV** — the HYG catalog is downloaded once and saved as `hyg_processed.csv`, making subsequent app launches instant (no network required after first run)
- **`@st.cache_data`** — the data loading function is cached by Streamlit, so filters and UI interactions never reload the file
- **Computed physics in Python** — temperature, luminosity, radius, and colors are all computed from the B-V and absolute magnitude values using peer-reviewed formulas
- **Theoretical tracks hardcoded** — evolution track coordinates are digitized from Padova/Geneva model literature, making the app fully self-contained without requiring external astrophysics libraries

---

## Local Installation & Running

### Prerequisites
- Python 3.10 or newer
- pip

## Sources

| Dataset | Source |

| **HYG v3 Database** | D. Nash / astronexus (GitHub) | 
| **Hipparcos Catalog** | ESA, van Leeuwen 2007, A&A 474 |
| **Yale Bright Star Catalog** | Hoffleit & Warren 1991 |
| **Gliese Catalog of Nearby Stars** | Gliese & Jahreiß 1991 | 
| **Stellar Evolution Tracks** | Padova (Bressan+2012), Geneva (Ekström+2012) | 

### Academic References

1. **van Leeuwen, F. (2007)** — *Validation of the new Hipparcos reduction*, A&A 474, 653–664
2. **Ballesteros, F.J. (2012)** — *New insights into black bodies*, EPL 97, 34008
3. **Bressan, A. et al. (2012)** — *PARSEC: stellar tracks and isochrones with the Padova and Trieste Stellar Evolution code*, MNRAS 427, 127–145
4. **Ekström, S. et al. (2012)** — *Grids of stellar models with rotation*, A&A 537, A146
5. **IAU (2015)** — *2015 IAU XXIX General Assembly, Resolution B3*, Nominal Solar Values



## Extending the App

### Adding Gaia DR3 Data
The [astroquery](https://astroquery.readthedocs.io/) library can query the Gaia archive directly:
```python
from astroquery.gaia import Gaia
job = Gaia.launch_job("SELECT TOP 10000 source_id, ra, dec, bp_rp, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE parallax > 10")
gaia_df = job.get_results().to_pandas()
```

### Adding Isochrone Overlays
PARSEC isochrones (age lines rather than mass tracks) can be downloaded from the [CMD web interface](http://stev.oapd.inaf.it/cgi-bin/cmd) and overlaid similarly to the evolution tracks.

### Performance Tuning
For deployments expecting high traffic:
- Host `hyg_processed.csv` on AWS S3 or Google Cloud Storage
- Use `st.cache_resource` for the heavy Plotly figure template
- Consider `parquet` format instead of CSV for faster I/O


*"The life of a star is told entirely in two numbers: its luminosity and its temperature. The H-R diagram makes that story visible."*
— Henry Norris Russell, paraphrased
