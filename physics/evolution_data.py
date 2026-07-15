"""
evolution_data.py
=================
Theoretical stellar evolution track data for the H-R Diagram.

Track data is digitized from the Padova/Geneva stellar evolution grids
(Bressan et al. 2012; Ekström et al. 2012) and encoded as B-V / Absolute
Magnitude sequences so they overlay directly on an observational H-R diagram.

Each track covers the following phases for a given initial mass:
  1. Pre-Main Sequence (PMS) / Hayashi track
  2. Zero-Age Main Sequence (ZAMS) arrival
  3. Main Sequence evolution
  4. Terminal-Age Main Sequence (TAMS) / Subgiant branch
  5. Giant / Red Giant Branch (RGB) or Red Supergiant (RSG)
  6. Horizontal Branch / AGB (low mass) or Wolf-Rayet / supernova (high mass)
  7. Final state: White Dwarf | Neutron Star | Black Hole

Author: Parth Mishra
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class EvolutionPhase:
    """A single named phase within a stellar evolution track."""
    name: str              # Display name, e.g. "Main Sequence"
    bv: List[float]        # B-V color index sequence for this phase
    absmag: List[float]    # Absolute magnitude sequence for this phase
    duration: str          # Human-readable lifetime, e.g. "10 Gyr"
    description: str       # Short physics description


@dataclass
class EvolutionTrack:
    """Complete evolution track for a star of given initial mass."""
    mass: float            # Initial mass in solar masses (M☉)
    label: str             # Display label, e.g. "1 M☉"
    color: str             # Hex color for the track line
    phases: List[EvolutionPhase]
    end_state: str         # "White Dwarf", "Neutron Star", or "Black Hole"
    end_state_icon: str    # Emoji icon for end state
    mass_description: str  # Brief description of this mass class

    @property
    def all_bv(self) -> List[float]:
        """Flatten all B-V points across all phases."""
        pts = []
        for p in self.phases:
            pts.extend(p.bv)
        return pts

    @property
    def all_absmag(self) -> List[float]:
        """Flatten all absolute magnitude points across all phases."""
        pts = []
        for p in self.phases:
            pts.extend(p.absmag)
        return pts

    @property
    def all_phase_labels(self) -> List[str]:
        """Return phase label for each point (for animation frames)."""
        labels = []
        for p in self.phases:
            labels.extend([p.name] * len(p.bv))
        return labels

    @property
    def all_descriptions(self) -> List[str]:
        """Return description for each point."""
        labels = []
        for p in self.phases:
            labels.extend([p.description] * len(p.bv))
        return labels


#  Theoretical Evolution Tracks 
# B-V and Absolute Magnitude values are approximate digitizations of published
# Padova (Bressan+2012) isochrone/track models for solar metallicity (Z=0.017).

EVOLUTION_TRACKS: List[EvolutionTrack] = [

    #  0.8 M☉ 
    EvolutionTrack(
        mass=0.8, label="0.8 M☉", color="#A0C4FF",
        end_state="White Dwarf", end_state_icon="⚪",
        mass_description="A K-type star, cooler and dimmer than the Sun. Lives for ~20 billion years — longer than the current age of the universe.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[1.8, 1.5, 1.2, 0.95],
                absmag=[3.5, 4.0, 5.0, 6.0],
                duration="~30 Myr",
                description="Gravitational contraction (Hayashi track). The protostar descends almost vertically."
            ),
            EvolutionPhase(
                name="Main Sequence",
                bv=[0.95, 0.92, 0.90, 0.88],
                absmag=[6.0, 6.1, 6.3, 6.5],
                duration="~20 Gyr",
                description="Stable hydrogen fusion in the core (p-p chain dominant). Extremely long-lived."
            ),
        ]
    ),

    #  1.0 M☉ (Solar) 
    EvolutionTrack(
        mass=1.0, label="1 M☉ ☀", color="#FFD700",
        end_state="White Dwarf", end_state_icon="⚪",
        mass_description="A solar-mass G-type star like our Sun. Lives ~10 billion years, evolving to a Red Giant before leaving a White Dwarf.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[2.0, 1.6, 1.2, 0.8, 0.65],
                absmag=[2.0, 3.0, 4.0, 4.5, 4.83],
                duration="~50 Myr",
                description="Hayashi + Henyey tracks. Gravitational contraction heats the core until hydrogen fusion ignites."
            ),
            EvolutionPhase(
                name="Main Sequence",
                bv=[0.65, 0.66, 0.67, 0.70, 0.74],
                absmag=[4.83, 4.75, 4.60, 4.30, 3.90],
                duration="~10 Gyr",
                description="Stable core H-fusion. The Sun grows slightly hotter and brighter over its main-sequence lifetime."
            ),
            EvolutionPhase(
                name="Subgiant Branch",
                bv=[0.74, 0.85, 1.00, 1.15],
                absmag=[3.90, 3.20, 2.40, 1.80],
                duration="~1 Gyr",
                description="Core hydrogen depleted. Shell burning begins; star expands and cools, moving right on the diagram."
            ),
            EvolutionPhase(
                name="Red Giant Branch",
                bv=[1.15, 1.30, 1.45, 1.55, 1.60],
                absmag=[1.80, 0.80, 0.00, -0.50, -0.80],
                duration="~1-2 Gyr",
                description="Massive expansion to ~100× the Sun's radius. Helium flash triggers at the RGB tip."
            ),
            EvolutionPhase(
                name="Horizontal Branch",
                bv=[0.60, 0.65, 0.70],
                absmag=[0.60, 0.60, 0.65],
                duration="~100 Myr",
                description="Stable core helium fusion. Star contracts slightly and heats up."
            ),
            EvolutionPhase(
                name="Asymptotic Giant Branch",
                bv=[1.40, 1.55, 1.70, 1.80],
                absmag=[0.20, -0.50, -1.20, -2.00],
                duration="~20 Myr",
                description="Double shell burning (H+He). Star expands enormously; heavy mass loss via stellar winds."
            ),
            EvolutionPhase(
                name="White Dwarf",
                bv=[0.00, -0.05, -0.10],
                absmag=[10.5, 11.0, 11.5],
                duration="Billions of Gyr",
                description="Exposed C/O core cools slowly. The ejected envelope forms a beautiful planetary nebula."
            ),
        ]
    ),

    #  2 M☉ 
    EvolutionTrack(
        mass=2.0, label="2 M☉", color="#FFFFFF",
        end_state="White Dwarf", end_state_icon="⚪",
        mass_description="An A-type star. About 2× solar mass, ~25× solar luminosity. Lives ~1.5 billion years.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[0.9, 0.6, 0.30, 0.10],
                absmag=[1.0, 1.5, 2.0, 2.4],
                duration="~10 Myr",
                description="Henyey track dominates for intermediate-mass stars; descent is more horizontal."
            ),
            EvolutionPhase(
                name="Main Sequence",
                bv=[0.10, 0.13, 0.17, 0.22],
                absmag=[2.4, 2.2, 1.9, 1.6],
                duration="~1.5 Gyr",
                description="Core H-fusion via CNO cycle. Stars of this mass have convective cores."
            ),
            EvolutionPhase(
                name="Subgiant Branch",
                bv=[0.22, 0.50, 0.85, 1.10],
                absmag=[1.6, 0.8, 0.2, -0.2],
                duration="~200 Myr",
                description="Rapid evolution across the Hertzsprung Gap — few stars observed here."
            ),
            EvolutionPhase(
                name="Red Giant Branch",
                bv=[1.10, 1.30, 1.50, 1.60],
                absmag=[-0.2, -1.0, -2.0, -2.5],
                duration="~500 Myr",
                description="Significant envelope expansion. Helium core ignition is non-degenerate for 2 M☉."
            ),
            EvolutionPhase(
                name="Horizontal Branch",
                bv=[0.50, 0.55, 0.60],
                absmag=[-0.5, -0.4, -0.3],
                duration="~80 Myr",
                description="Core helium burning phase."
            ),
            EvolutionPhase(
                name="White Dwarf",
                bv=[0.00, -0.05],
                absmag=[10.0, 11.0],
                duration="Cooling forever",
                description="Leaves behind a 0.6–0.8 M☉ white dwarf after AGB mass loss."
            ),
        ]
    ),

    #  5 M☉ 
    EvolutionTrack(
        mass=5.0, label="5 M☉", color="#FF9F43",
        end_state="Neutron Star", end_state_icon="💫",
        mass_description="A B-type star. ~700× solar luminosity. Lives only ~100 million years. Dies in a Type II supernova.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[0.50, 0.20, -0.05],
                absmag=[-1.0, -1.5, -2.0],
                duration="~1 Myr",
                description="Very rapid Henyey track descent. Massive stars ignite quickly."
            ),
            EvolutionPhase(
                name="Main Sequence",
                bv=[-0.05, -0.04, -0.01, 0.05],
                absmag=[-2.0, -1.9, -1.7, -1.4],
                duration="~100 Myr",
                description="CNO cycle dominates. Convective core is large (~40% of mass). Strong stellar winds begin."
            ),
            EvolutionPhase(
                name="Hertzsprung Gap / Subgiant",
                bv=[0.05, 0.40, 0.80, 1.20],
                absmag=[-1.4, -2.0, -2.8, -3.5],
                duration="~5 Myr",
                description="Rapid rightward evolution. Very few stars observed here (the 'Hertzsprung Gap')."
            ),
            EvolutionPhase(
                name="Red Supergiant",
                bv=[1.20, 1.50, 1.70, 1.85],
                absmag=[-3.5, -4.5, -5.0, -5.5],
                duration="~10 Myr",
                description="Massive expansion. Shell burning; luminous red supergiant phase."
            ),
            EvolutionPhase(
                name="Supernova / Neutron Star",
                bv=[0.0],
                absmag=[-18.0],
                duration="Seconds",
                description="Core collapse triggers a Type II supernova. The remnant is a neutron star (pulsar)."
            ),
        ]
    ),

    #  10 M☉ 
    EvolutionTrack(
        mass=10.0, label="10 M☉", color="#FF6B6B",
        end_state="Neutron Star", end_state_icon="💫",
        mass_description="A massive B-type star. ~10,000× solar luminosity. Lives only ~30 million years before a spectacular supernova.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[0.30, 0.0, -0.20],
                absmag=[-3.0, -3.5, -4.0],
                duration="~0.3 Myr",
                description="Extremely rapid. Massive stars arrive on the main sequence almost instantly."
            ),
            EvolutionPhase(
                name="Main Sequence",
                bv=[-0.20, -0.18, -0.14, -0.08],
                absmag=[-4.0, -3.9, -3.7, -3.5],
                duration="~30 Myr",
                description="Powerful stellar winds drive mass loss. Radiation pressure dominates."
            ),
            EvolutionPhase(
                name="Hertzsprung Gap",
                bv=[-0.08, 0.30, 0.80, 1.30],
                absmag=[-3.5, -4.5, -5.5, -6.0],
                duration="~1 Myr",
                description="Rapid crossing of the instability strip. May appear as Cepheid variables."
            ),
            EvolutionPhase(
                name="Red Supergiant",
                bv=[1.30, 1.60, 1.80, 1.90],
                absmag=[-6.0, -6.5, -7.0, -7.2],
                duration="~3 Myr",
                description="Among the largest stars by radius (~1000 R☉). Betelgeuse is a famous example."
            ),
            EvolutionPhase(
                name="Supernova",
                bv=[0.0],
                absmag=[-18.5],
                duration="Seconds",
                description="Iron core collapse. Releases 3×10⁴⁶ J. Outshines the entire galaxy briefly."
            ),
        ]
    ),

    #  25 M☉ 
    EvolutionTrack(
        mass=25.0, label="25 M☉", color="#C92A2A",
        end_state="Black Hole", end_state_icon="🕳",
        mass_description="An O-type hypergiant. ~100,000× solar luminosity. Lives only ~7 million years. Likely forms a black hole.",
        phases=[
            EvolutionPhase(
                name="Pre-Main Sequence",
                bv=[0.10, -0.20, -0.30],
                absmag=[-5.0, -5.5, -5.8],
                duration="~0.05 Myr",
                description="Almost instantaneous arrival on the ZAMS. Radiation pressure is enormous from birth."
            ),
            EvolutionPhase(
                name="Main Sequence (O-type)",
                bv=[-0.30, -0.28, -0.25, -0.20],
                absmag=[-5.8, -5.7, -5.5, -5.2],
                duration="~7 Myr",
                description="O-type supergiant. UV flux ionizes surrounding nebula. Mass loss rate ~10⁻⁶ M☉/yr."
            ),
            EvolutionPhase(
                name="Wolf-Rayet Phase",
                bv=[-0.20, -0.15, -0.05, 0.20],
                absmag=[-5.2, -5.8, -6.2, -6.5],
                duration="~0.5 Myr",
                description="Outer envelope stripped by intense winds, exposing hot nuclear-burning core (WN/WC stage)."
            ),
            EvolutionPhase(
                name="Luminous Blue Variable",
                bv=[0.20, 0.60, 1.00, 1.50],
                absmag=[-6.5, -7.0, -7.5, -7.8],
                duration="~0.1 Myr",
                description="Eruptive instability at the Eddington luminosity limit. Massive eruptions shed solar masses."
            ),
            EvolutionPhase(
                name="Hypernova / Black Hole",
                bv=[0.0],
                absmag=[-20.0],
                duration="Milliseconds",
                description="Catastrophic core collapse. May produce a long-duration gamma-ray burst. Remnant: black hole."
            ),
        ]
    ),
]


#  ZAMS Reference Line 

def get_zams_line() -> dict:
    """
    Return the Zero-Age Main Sequence (ZAMS) as B-V / AbsMag sequences.

    The ZAMS marks where stars of various masses first arrive on the
    main sequence after completing gravitational contraction.

    Values digitized from Bressan et al. (2012) Padova isochrones at age=0.

    Returns
    -------
    dict with keys 'bv' and 'absmag'
    """
    return {
        "bv":     [-0.35, -0.30, -0.25, -0.20, -0.15, -0.10, -0.02,
                    0.10,  0.20,  0.30,  0.42,  0.55,  0.65,  0.75,
                    0.85,  0.95,  1.10,  1.30,  1.50],
        "absmag": [-5.80, -5.20, -4.60, -4.00, -3.40, -2.80, -2.00,
                   -1.20, -0.60,  0.00,  0.80,  1.60,  2.40,  3.20,
                    4.00,  4.83,  5.80,  7.20,  9.00],
        "masses": ["25 M☉", "15 M☉", "12 M☉", "9 M☉", "7 M☉", "5 M☉", "3 M☉",
                   "2 M☉", "1.7 M☉", "1.5 M☉", "1.2 M☉", "1 M☉", "0.9 M☉", "0.8 M☉",
                   "0.7 M☉", "0.6 M☉", "0.5 M☉", "0.4 M☉", "0.2 M☉"]
    }


def get_all_tracks() -> List[EvolutionTrack]:
    """Return all theoretical evolution tracks."""
    return EVOLUTION_TRACKS


def get_track_by_mass(mass: float) -> EvolutionTrack | None:
    """Return a track matching the given mass (exact)."""
    for track in EVOLUTION_TRACKS:
        if abs(track.mass - mass) < 0.01:
            return track
    return None
