"""

stellar_physics.py

Core astrophysical formulas for The Star Evolution Atlas (SEA).

Physics References:
  - Ballesteros (2012), EPL, 97, 34008  → B-V to Temperature
  - IAU 2015 Nominal Solar Values       → Absolute magnitude of Sun (M☉ = 4.83)
  - Mamajek et al. (2015)               → Spectral class boundaries

Author: Parth Mishra

"""

import numpy as np


#  Constants 
SUN_ABS_MAG = 4.83   # Absolute magnitude of the Sun (V-band)
SUN_BV      = 0.65   # B-V color index of the Sun
SUN_TEFF    = 5778   # Effective temperature of the Sun in Kelvin


#  Temperature Conversion 

def bv_to_temperature(bv: float | np.ndarray) -> float | np.ndarray:

    """

    Convert B-V color index to effective temperature (Kelvin) using the
    Ballesteros (2012) empirical formula.

    Formula:
        T = 4600 × [ 1 / (0.92·BV + 1.7) + 1 / (0.92·BV + 0.62) ]

    Valid range: roughly -0.4 < B-V < 2.0

    Parameters
    
    bv : float or np.ndarray
        B-V photometric color index.

    Returns
   
    float or np.ndarray
        Effective temperature in Kelvin.

    """

    bv = np.asarray(bv, dtype=float)
    T = 4600.0 * (1.0 / (0.92 * bv + 1.7) + 1.0 / (0.92 * bv + 0.62))
    return T


#  Luminosity Conversion 

def absmag_to_luminosity(absmag: float | np.ndarray) -> float | np.ndarray:

    """

    Convert absolute magnitude (V-band) to luminosity in solar units (L☉).

    Formula:
        L / L☉ = 10^[(M☉ - M) / 2.5]

    where M☉ = 4.83 (IAU 2015 nominal absolute magnitude of the Sun).

    Parameters
    
    absmag : float or np.ndarray
        Absolute visual magnitude of the star.

    Returns
   
    float or np.ndarray
        Luminosity in solar luminosities (L☉).

    """

    absmag = np.asarray(absmag, dtype=float)
    return 10.0 ** ((SUN_ABS_MAG - absmag) / 2.5)


def luminosity_to_absmag(luminosity: float | np.ndarray) -> float | np.ndarray:

    """

    Convert luminosity in solar units (L☉) back to absolute magnitude.

    Parameters
    
    luminosity : float or np.ndarray
        Luminosity in solar luminosities.

    Returns
    
    float or np.ndarray
        Absolute visual magnitude.

    """

    luminosity = np.asarray(luminosity, dtype=float)
    return SUN_ABS_MAG - 2.5 * np.log10(luminosity)


#  Stellar Radius Estimate 

def estimate_radius(luminosity: float | np.ndarray, temperature: float | np.ndarray) -> float | np.ndarray:
    
    """

    Estimate stellar radius in solar radii using the Stefan-Boltzmann law.

    Formula:
        R / R☉ = (L / L☉)^0.5 × (T☉ / T)^2

    Parameters
    
    luminosity : float or np.ndarray
        Luminosity in solar luminosities (L☉).
    temperature : float or np.ndarray
        Effective temperature in Kelvin.

    Returns
    
    float or np.ndarray
        Stellar radius in solar radii (R☉).


    """

    luminosity   = np.asarray(luminosity, dtype=float)
    temperature  = np.asarray(temperature, dtype=float)
    return np.sqrt(luminosity) * (SUN_TEFF / temperature) ** 2


#  Spectral Classification 



# B-V boundaries for OBAFGKM classification (approximate)


_SPECTRAL_BV_BOUNDS = [
    (-0.40, -0.10, "O"),
    (-0.10,  0.00, "B"),
    ( 0.00,  0.30, "A"),
    ( 0.30,  0.58, "F"),
    ( 0.58,  0.81, "G"),
    ( 0.81,  1.40, "K"),
    ( 1.40,  3.00, "M"),
]


def spectral_class(bv: float | np.ndarray) -> np.ndarray:
    
    """

    Return a spectral class letter (O, B, A, F, G, K, M) for each B-V value.

    Parameters
    
    
    bv : float or np.ndarray

    Returns

    np.ndarray of str

    """

    bv = np.atleast_1d(np.asarray(bv, dtype=float))
    result = np.full(bv.shape, "?", dtype=object)
    for lo, hi, cls in _SPECTRAL_BV_BOUNDS:
        mask = (bv >= lo) & (bv < hi)
        result[mask] = cls
    return result if result.size > 1 else result[0]


#  Color Mapping 

# Control points: (B-V, R, G, B) — mapping photometric color to RGB
_COLOR_STOPS = [
    (-0.40, (155, 176, 255)),  # O-type: hot blue-violet
    (-0.10, (170, 191, 255)),  # B-type: blue-white
    ( 0.00, (202, 215, 255)),  # A-type: white-blue
    ( 0.30, (248, 247, 255)),  # F-type: white
    ( 0.58, (255, 244, 234)),  # G-type: yellow-white (Sun)
    ( 0.81, (255, 210, 161)),  # K-type: orange
    ( 1.40, (255, 140,  80)),  # K/M boundary: deep orange
    ( 2.00, (255,  80,  40)),  # M-type: red
]



def bv_to_hex_color(bv: float | np.ndarray) -> np.ndarray:

    """

    Map B-V color index to a hex color string for visual rendering.

    Uses linear interpolation between empirically chosen control points
    that approximate the visual appearance of stars.

    Parameters
    
    bv : float or np.ndarray
        B-V photometric color index.

    Returns
    
    np.ndarray of str  (or single str if scalar input)
        Hex color strings, e.g. '#FFD4A3'.

    """

    scalar = np.ndim(bv) == 0
    bv = np.atleast_1d(np.asarray(bv, dtype=float))
    bv_clipped = np.clip(bv, _COLOR_STOPS[0][0], _COLOR_STOPS[-1][0])

    stops_bv  = np.array([s[0] for s in _COLOR_STOPS])
    stops_rgb = np.array([s[1] for s in _COLOR_STOPS], dtype=float)

    r = np.interp(bv_clipped, stops_bv, stops_rgb[:, 0])
    g = np.interp(bv_clipped, stops_bv, stops_rgb[:, 1])
    b = np.interp(bv_clipped, stops_bv, stops_rgb[:, 2])

    r = np.clip(r, 0, 255).astype(int)
    g = np.clip(g, 0, 255).astype(int)
    b = np.clip(b, 0, 255).astype(int)

    hexcols = np.array([f"#{ri:02X}{gi:02X}{bi:02X}" for ri, gi, bi in zip(r, g, b)])
    return hexcols[0] if scalar else hexcols


def bv_to_rgba(bv: float, alpha: float = 0.9) -> str:
    """Return an rgba() CSS string for a given B-V index."""
    hex_col = bv_to_hex_color(float(bv))
    r = int(hex_col[1:3], 16)
    g = int(hex_col[3:5], 16)
    b = int(hex_col[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


#  Stellar Lifetime Estimate 

def main_sequence_lifetime(mass_solar: float | np.ndarray) -> float | np.ndarray:

    """

    Estimate main-sequence lifetime in billions of years (Gyr).

    Formula (Schaller et al. 1992 approximation):
        τ_MS ≈ (M / L) × 10 Gyr ≈ (1 / M^2.5) × 10 Gyr
        (using L ∝ M^4 and simplified to τ ∝ M^(1-4) = M^-3)

    More accurate approximation:
        τ_MS ≈ 10 × M^(-2.5) Gyr  for M > 0.5 M☉

    Parameters
    
    mass_solar : float or np.ndarray
        Stellar mass in solar masses (M☉).

    Returns
    
    float or np.ndarray
        Approximate main-sequence lifetime in Gyr.

    """

    mass_solar = np.asarray(mass_solar, dtype=float)
    return 10.0 * mass_solar ** (-2.5)


#  Stellar Category 

def stellar_category(absmag: float | np.ndarray, bv: float | np.ndarray) -> np.ndarray:

    """

    Classify a star into a broad evolutionary category.

    Categories: 'Main Sequence', 'Giant', 'Supergiant', 'White Dwarf', 'Unknown'

    Parameters
    
    absmag : float or np.ndarray
        Absolute visual magnitude.
    bv : float or np.ndarray
        B-V color index.

    Returns

    np.ndarray of str

    """

    absmag = np.atleast_1d(np.asarray(absmag, dtype=float))
    bv     = np.atleast_1d(np.asarray(bv,     dtype=float))
    result = np.full(absmag.shape, "Unknown", dtype=object)

    # White dwarfs: very faint and blue/white
    wd_mask = (absmag > 10) & (bv < 0.6)
    result[wd_mask] = "White Dwarf"

    # Supergiants: very luminous (M < -3)
    sg_mask = absmag < -3
    result[sg_mask] = "Supergiant"

    # Giants: moderately luminous with red/orange color
    g_mask = (absmag < 2) & (bv > 0.8) & (~sg_mask)
    result[g_mask] = "Giant"

    # Main sequence: everything else roughly following the MS
    ms_mask = ~(wd_mask | sg_mask | g_mask)
    result[ms_mask] = "Main Sequence"

    return result if result.size > 1 else result[0]
