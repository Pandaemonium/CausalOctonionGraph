# RFC-027: Solar 3-Phase Assimilation, Neutrino Fronts, and Extrasolar Meteor Re-Phasing Contract

Status: Draft v2 (Prediction Lock + Literature Integration)
Date: 2026-03-03 (v1); updated 2026-03-03 (v2 — lit review)
Owner: COG Core (Codex lane + Claude lane)
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-016_Koide_Formula_C12_Generation_Phase_Derivation.md`
- `cog_v3/rfc/RFC-024_SM_Particle_Identity_Map_and_W_Interaction_in_S2880.md`

---

## 1. Purpose and Original Motivation

This RFC locks a concrete prediction set for the hypothesis of **solar 3-phase assimilation**:

The Sun's neutrino output has been, over billions of years, phase-biasing nearby matter and
vacuum into the local dominant C12 generation sector. As a consequence:

1. **Generation-1 is frame-dependent.** Every local observer, near their own star, will see
   their local matter as "Gen1" (the lowest-mass, most abundant generation). The Z3 symmetry
   of C12 is exact: what we call electron/up-quark/down-quark is only "Gen1" relative to our
   local solar phase domain. A star with a different C12 phase would see its own matter as
   "Gen1" and ours as "Gen2" or "Gen3."

2. **Muon stars and tau stars exist** (from our frame of reference). Stars in other C12 phase
   domains are producing matter at what we would call the muon or tau mass scale — but to
   their inhabitants, they are ordinary "Gen1" matter. The mass hierarchy is an artifact of
   our local frame, not an absolute property.

3. **3-phase neutrino fronts** form at domain boundaries between differently-phased stellar
   regions. Neutrinos from a star pass freely through same-phase medium but interact with
   off-phase medium, creating cascaded phase-exchange events. At boundaries between two stellar
   domains, these fronts form neutrino "traps" where neutrinos bounce between same-phase and
   off-phase regions until they escape along the boundary surface.

4. **Solar tails** form behind moving stars. As the Sun moves at ~20 km/s through the local
   interstellar medium, it leaves behind a long tail of phase-synced medium and has a shorter
   front (upwind direction) where phase-syncing is still in progress.

5. **Extrasolar objects entering the solar domain** begin off-phase and progressively re-phase
   toward the local solar C12 phase. During re-phasing they experience internal structural
   stress measurable as anomalous material strength, non-gravitational acceleration, or
   anomalous fragmentation.

This RFC is intentionally strict and falsifiable against **existing public data**.

---

## 2. Theoretical Framework

### 2.1 Z3 symmetry and frame-relativity of "generation"

The C12 clock has Z12 = Z4 x Z3 structure. The Z3 factor assigns generation index g = p mod 3.
There is NO absolute definition of which phase is "Gen1". The three generation phases are
completely equivalent under the Z3 symmetry of the theory.

Consequence: The designation of our local matter as "Gen1" (electron, up, down) is a choice
of reference frame — specifically, the frame defined by our local solar phase domain. A star
with C12 phase g=1 (from our frame) produces "muon-mass" matter locally, but its own
inhabitants measure the same Koide ratio K=2/3 and the same mass hierarchies within their
own frame.

This is analogous to the relativity of velocity in special relativity: no absolute rest frame
exists, only relative motion. Similarly, no absolute "Gen1 frame" exists, only relative phase.

### 2.1.1 Convention vs physical state (explicit lock)

This RFC uses the following strict distinction:

1. **Convention (label choice):**
   - The name "Gen1/Gen2/Gen3" is a label convention.
   - Global relabel `p -> p + 4k (mod 12)` for all states and observers is an exact Z3 symmetry.
   - Therefore, which sector is called "Gen1" is not absolute.

2. **Physical in-model variables (not convention):**
   - Full state identity is `(p, q)` with decomposition `p -> (a, g)`, where:
     - `g = p mod 3` (generation sector),
     - `a = p mod 4` (within-generation sub-clock).
   - Relative offsets, hop channels, and interaction outcomes depend on `(a, q)` as well as `g`.

3. **What symmetry does and does not imply:**
   - Symmetry implies equivalence under **global** relabel of the entire system.
   - Symmetry does **not** imply any two arbitrary motifs are identical if they differ in `(a, q)` or environment.
   - So "local Gen1 is frame-relative" is true, while "all states in different sectors are automatically identical" is false.

4. **Observer-language translation:**
   - Alice/Bob/Charlie in different phase domains can each call local matter "Gen1."
   - Their cross-domain statements ("that is a muon/tau star") are relative-phase descriptions in their chosen basis.
   - This is a basis statement, not a claim that all microscopic states are indistinguishable.

### 2.2 Assimilation mechanism

In the S2880 kernel, a neutrino emitted at phase p cannot interact with matter at the same
phase p (same-generation interaction is suppressed — neutrinos are the A16-scalar sector with
near-zero associator activity, see RFC-024). Neutrinos interact preferentially with
off-phase matter, causing a Dp=3 or Dp=4 phase exchange hop.

Over billions of years and ~10^57 solar neutrinos emitted:
- Same-phase matter: essentially transparent to solar neutrinos
- Off-phase matter: driven toward solar phase by repeated phase-exchange events
- Result: solar domain becomes dominated by Gen1 matter; the Sun has "assimilated" its neighborhood

The relevant interaction cross-section is:
```
sigma_assimilation ~ sigma_SM * (off-phase enhancement factor)
```
The off-phase enhancement factor is the ratio of Dp!=0 hop probability vs Dp=0 (same-phase
pass-through). From Phase D simulations: R3 ~ 0.09-0.22, implying off-phase interactions are
~10-20% of all interactions. This is the effective "assimilation cross-section" for solar
neutrinos acting on off-phase matter.

### 2.3 Standard Model analog: neutrino forces in directional backgrounds

A direct SM-framework analog exists in the literature. Ghosh, Grossman, Tangarife, Xu, Yu
(2022, arXiv:2209.07082) showed that:

- In vacuum, two fermions exchange a pair of neutrinos producing a long-range force ~ G_F^2/r^5
- In a DIRECTIONAL neutrino background (e.g., solar neutrino flux), this force acquires a 1/r
  component in the direction parallel to the neutrino flow, enhanced by many orders of magnitude
  compared to the vacuum case
- The enhancement is proportional to the neutrino number density: n_nu * G_F^2 * L / r

For the solar neutrino flux at 1 AU: n_nu ~ 6.5 x 10^10 / cm^2/s / c ~ 220 /cm^3.
This gives an enhancement of ~10^{10} over the vacuum neutrino force at 1 AU.

In the COG model, this SM-compatible mechanism provides the proximate cause of assimilation:
the directional solar neutrino background creates an enhanced phase-exchange force on off-phase
matter, systematically driving it toward the local solar phase.

Also relevant: Horowitz & Pantaleone (1993, hep-ph/9306222) showed that the cosmic neutrino
background mediates long-range forces with spin-dependent components, scaling as 1/r for
r << 1/T (short distances) and screened at r >> 1/T (long distances). The solar neutrino
background (directed, not isotropic) should produce an asymmetric version of this force.

### 2.4 Heliosphere structure: known nose-tail asymmetry

The heliosphere is the bubble carved by the solar wind in the local interstellar medium.
The Sun moves at ~20 km/s through the local ISM, with the solar apex at approximately
RA = 18h28m, Dec = +30 deg (toward Hercules; R.A. 277 deg, Dec +30 deg in J2000 equatorial).

Key known heliosphere facts (all from observational data):
- Heliopause NOSE direction: ~RA=255 deg, Dec=+5 deg (roughly toward the tail of Scorpius)
  — the upwind direction of ISM flow INTO the heliosphere
- Termination shock: ~94 AU (nose), ~84 AU (south, Voyager 2 direction) — confirmed asymmetric
- Heliopause nose: ~120 AU; tail extends to >300 AU (estimated)
- The heliosphere is already known to be nose-tail asymmetric due to ISM pressure and ISMF geometry
  (Opher et al. 2006, astro-ph/0606324; Bladek & Ratkiewicz 2023)

The COG prediction is an ADDITIONAL asymmetry on top of the known plasma/wind asymmetry:
a phase-domain asymmetry in which the tail direction has been fully phase-synced (old solar
domain) while the nose direction contains more off-phase ISM material.

### 2.5 Z3 fraction prediction

Assuming C12 phase domains are distributed randomly in the galaxy (maximum entropy), and
the three generations are equally common globally, then for any given incoming interstellar
object:
- Probability of same phase as local solar domain: 1/3
- Probability of off-phase (Gen2 or Gen3 from our frame): 2/3

Prediction: approximately 2/3 of interstellar objects entering the solar system will be
off-phase and subject to re-phasing effects. Approximately 1/3 will pass through without
anomaly (same phase, hence transparent to solar neutrinos in the COG framework).

Observable test: over a large enough sample of interstellar objects, ~2/3 should show
anomalous behavior relative to solar-system-origin objects of similar size/composition.

### 2.6 Phase front physics and the mass convention (Option B)

When matter is rephased from one C12 generation sector to another, the question of rest
mass must be resolved. This RFC adopts the following frame-consistent convention:

**Rest mass is absolute (frame-independent).** An electron has m_e = 0.511 MeV in EVERY
C12 generation domain, in common Planck-derived units shared by all observers. The
generation index g labels the C12 clock sector the particle occupies in the S2880 state
space — not its absolute mass. What changes across domains is the Fano triple interaction
network (which C12 sectors couple strongly to which), not the fundamental particle masses.

Under this convention:
- "Muon stars" are stars whose matter occupies the g=1 C12 sector from our frame's
  convention. Their electrons still have m_e = 0.511 MeV; their protons m_p = 938 MeV.
- The mass hierarchy m_e << m_mu << m_tau exists in every domain. What differs between
  domains is which C12 phase sector is the dominant (assimilated) configuration in that
  stellar system. All three lepton mass states exist everywhere; the local star determines
  which sector is most abundant.
- Observable cross-domain differences are in INTERACTION CROSS-SECTIONS (Delta_Gamma
  selection rules) and in the sector-specific crystal/nuclear bonding geometry produced
  by the local Fano triple pattern.

This resolves the rephasing energy problem. The phase-exchange reaction:
```
nu(Gamma=0) + e-(Gamma=1) -> nu(Gamma=1) + e-(Gamma=0)
```
conserves rest mass on both sides (both electrons have m_e = 0.511 MeV). The neutrino's
kinetic energy (~few MeV from solar pp/pep reactions) drives the C12 clock-sector shift.
This is energetically feasible with standard solar neutrinos. No ~105 MeV gamma burst is
predicted per rephasing event. The phase front is NOT a high-energy emission source.

The material strength anomalies of off-phase interstellar objects (Sections 3.2, 4.4)
arise from sector-mismatched Fano bonding geometry — the internal cohesion network of the
crystal/nucleus is phase-locked to a different triple pattern — not from heavier atomic
masses.

**Local environment at a phase front — five characteristic features:**

1. FINITE WIDTH: The front is a diffuse reaction zone, not a sharp surface. Width
   delta ~ lambda_rephase = 1 / (n_matter * sigma_rephase). In the warm ISM
   (n ~ 1 cm^{-3}), delta ranges from ~AU scale near the heliopause (where the solar
   neutrino flux is still substantial) to ~light-year scale in the deep ISM (driven only
   by background stellar neutrinos from all surrounding stars). Objects traversing the
   front experience a gradual increase then decrease in off-phase interaction rate —
   not an abrupt step.

2. NEUTRINO TRAP: Neutrinos from domain A (Gamma=0) scatter preferentially off domain B
   matter (Delta_Gamma=1, enhanced cross-section). Neutrinos from domain B scatter
   preferentially off domain A matter (also Delta_Gamma=1, enhanced). Neither domain's
   neutrinos easily penetrate deep into the other side. The result is a steady-state
   neutrino density enhancement at the boundary — a "neutrino cushion" sustained by
   competing fluxes from both sides. Local neutrino number density at the front exceeds
   that in either bulk domain.

3. PEAK INTERACTION RATE: In the bulk of either domain, all local neutrino-matter pairs
   have Delta_Gamma=0 (suppressed). At the front, cross-domain neutrinos irradiate
   cross-domain matter at Delta_Gamma=1 or 2 (enhanced). The causal graph edge density
   peaks at the front. The front is the most interaction-dense region of the ISM between
   the two stellar domains.

4. EXOTIC CHEMISTRY: In the transition zone, atoms from different generation sectors
   co-exist. Molecules forming from mixed-sector atoms experience sector-mismatched Fano
   bonding geometry and are structurally strained. The transition zone resists stable
   molecular formation. Observable prediction: ISM molecular clouds straddling a phase
   front should show anomalous molecular abundances and spectral line broadening
   inconsistent with thermal or magnetic field models.

5. JUNCTION STRINGS: Where three domain walls of types (Gamma=0|1), (Gamma=1|2),
   (Gamma=2|0) converge, a 1D topological defect (junction string) exists in 3D space.
   At junction strings, all neutrino-matter interactions have Delta_Gamma != 0 — from
   all three adjacent domains simultaneously. These are the most interaction-dense linear
   structures in the galactic ISM. Possible observable: anomalous ISM linear filaments
   with emission spectra not explained by thermal or magnetic-field models.

The heliopause nose (~120 AU, upwind at ~RA=255 deg, Dec=+5 deg) is the closest accessible
example of an active phase front. The heliopause tail (>300 AU, downwind) is a relic domain
wall in the process of decohering as the Sun moves away and the solar neutrino flux at that
distance weakens. The known nose-tail asymmetry of the heliosphere (Voyager, IBEX) includes
this phase-front contribution in addition to the known plasma pressure and magnetic field
asymmetry.

---

## 3. Existing Evidence (Pre-registered as already observed)

These observations exist PRIOR to this RFC and are being identified as potential COG evidence
post hoc. They are listed for context only — not as confirmed predictions.

### 3.1 'Oumuamua's non-gravitational acceleration (1I/2017 U1)

'Oumuamua showed a confirmed non-gravitational acceleration directed RADIALLY AWAY FROM THE
SUN, with power-law scaling r^{-1} to r^{-2} (Spada 2023, arXiv:2304.06964; Micheli et al.
2018). No standard explanation is fully satisfactory:
- Outgassing: no coma, no CO/CO2 detected (Trilling et al. 2018, arXiv:1811.08072)
- Radiation pressure: requires anomalously thin/flat geometry
- Cometary: incompatible with spin stability (Rafikov 2018, arXiv:1809.06389)

COG interpretation: 'Oumuamua was from an off-phase stellar system. As it traveled through
the solar domain, enhanced solar neutrino interactions (Ghosh et al. mechanism) acted on its
off-phase matter. The radially outward direction of the non-gravitational acceleration makes
sense: solar neutrinos propagate radially outward, and the phase-exchange force imparted to
off-phase matter by this directional neutrino background is radially directed.

The r^{-1} to r^{-2} scaling (Spada 2023) matches the expected scaling of the Ghosh et al.
directional neutrino force (proportional to neutrino flux, which scales as r^{-2}) combined
with the re-phasing cross-section.

This is a NATURAL EXPLANATION for the 'Oumuamua anomaly in the COG framework — but it must be
noted that this explanation is being proposed after the fact (post-hoc). The TRUE test is P4/P5
with new data.

Observational note: 'Oumuamua was first detected on 2017 October 19, AFTER its perihelion
passage (2017 September 9). All confirmed trajectory and non-gravitational acceleration data
comes from the OUTBOUND leg only. The observed radially-outward acceleration is therefore
specifically the ACCELERATE ON EXIT phase of the neutrino pressure model (Section 4.7,
Regime 2a or 2b). The corresponding DECELERATE ON ENTRY phase (inbound approach to
perihelion) was not observed. A future extrasolar object detected on an inbound trajectory
and showing radial deceleration before perihelion would directly confirm the entry-phase
prediction at the quantitative level — this remains an untested prediction of the model.

### 3.2 Interstellar meteors as material strength outliers

Siraj & Loeb (2022, arXiv:2209.09905) found:
- IM1 (CNEOS 2014-01-08) is ranked #1 in material strength out of 273 CNEOS fireballs (3.5 sigma outlier)
- IM2 (second candidate) is ranked #3 (2.6 sigma outlier)
- Combined probability of drawing two objects this strong from the CNEOS catalog: ~10^{-4} to ~10^{-6}

If these objects are confirmed interstellar, this implies interstellar meteors are
SYSTEMATICALLY STRONGER than solar system meteors.

COG interpretation: Off-phase matter is structurally coherent in a different way than
solar-domain matter. The internal bonding geometry of matter phase-locked to a different
star's C12 phase differs from solar-domain matter. This manifests as anomalously high
material strength (harder to ablate/fragment). The effect is a prediction of the COG model,
not an assumption.

### 3.3 Growing interstellar object catalog

Confirmed interstellar objects and candidates as of 2026:
- 1I/'Oumuamua (2017): non-gravitational acceleration anomaly [unexplained]
- 2I/Borisov (2019): cometary, no anomaly detected [consistent with ~1/3 being same-phase]
- IM1/CNEOS-2014-01-08 (2014, confirmed 2022): material strength 3.5 sigma outlier
- CNEOS-22 (2022): confirmed interstellar at 8.7 sigma (Cloete & Loeb 2026, arXiv:2602.08956)
- CNEOS-25 (2025): confirmed interstellar at 5.5 sigma (ibid.)
- 3I/ATLAS (2025): third large interstellar object, comet-like; from old thick-disk system

Rough count: 3 confirmed interstellar comets/asteroids (Oumuamua, Borisov, 3I/ATLAS) + 3
confirmed/candidate interstellar meteors. Of those with anomaly data:
- Oumuamua: anomalous [off-phase candidate]
- Borisov: normal [same-phase candidate, or anomaly not yet detected]
- IM1: material strength outlier [off-phase candidate]

Ratio: 2/3 showing anomaly. Consistent with Z3 prediction (2/3 off-phase) but sample too
small for statistical significance.

---

## 4. Locked Predictions

### 4.1 Solar-neutrino directional prediction (primary: P1)

After controlling for known annual 1/r^2 modulation and day-night MSW matter effects, the
residual solar neutrino observable contains a non-zero dipole term aligned with the
solar apex/anti-apex axis.

Operational model:
```
R(t, dir) = A0 + A1*cos(2*pi*t/T_year + phi_year) + A2*D_daynight(t) + A3*(n_dir . n_apex)
```

Where:
- R: chosen neutrino observable (flavor ratio or event class ratio)
- n_apex: fixed solar apex unit vector (RA=277 deg, Dec=+30 deg, J2000)
- A3: apex-aligned coefficient of interest
- D_daynight: binary or continuous day-night function (corrects MSW Earth matter effect)

Prediction direction:
- ANTI-APEX direction (solar tail, already-phased): stronger electron-like (Gen1) content
- APEX direction (solar front, active phasing zone): elevated off-phase content → possible
  enhanced mu-like or tau-like neutrino appearance

Note: the direction of A3 is not predicted with high confidence because the cross-section for
off-phase neutrino emission from the front region vs. the tail region depends on kernel details
not yet fully worked out. The MAGNITUDE being non-zero is the primary claim.

### 4.2 Sidereal structure prediction (primary: P2)

Residual anisotropy (after annual + day-night) projects onto sidereal frame aligned to solar
apex, NOT explainable by annual harmonics alone.

Pass condition: apex-aligned sidereal component survives model comparison vs. null (annual +
day-night only).

### 4.3 Phase-boundary/front-trap prediction (secondary: P3)

At the heliopause nose direction (~255 deg RA, +5 deg Dec), an elevated neutrino
flavor-conversion-like signal should be seen compared to the tail direction, because the nose
region has more active phase-exchange (off-phase ISM flowing in) vs. the already-synced tail.

This prediction is WEAK in current solar neutrino data because the heliopause is at ~120 AU
and the effect is diffuse. It is more relevant to future instruments with better directional
resolution or to cosmic-ray neutrino data with longer baselines.

### 4.4 Extrasolar meteor re-phasing prediction (primary for meteor lane: P4)

Incoming interstellar meteoroids show trajectory-dependent anomalies consistent with
re-phasing stress:

1. Anomalous material strength (already seen in IM1/IM2 at 3.5/2.6 sigma)
2. Elevated multi-stage fragmentation rate
3. Anomalous light-curve jitter bursts
4. Directional correlation with solar apex direction

Predicted Z3 statistics: across a large sample (N > 10 confirmed interstellar meteors),
approximately 2/3 should show anomalous behavior. Approximately 1/3 should be consistent
with solar-system-origin objects (same-phase, transparent to solar neutrinos).

### 4.5 Relative-phase decay prediction (primary: P5)

Meteor anomalies are HIGHEST near entry (maximum off-phase, minimum re-phasing completed)
and DECAY along the atmospheric path as re-phasing progresses.

Observable proxy: anomaly rate (fragmentation bursts, light-curve jitter) should decrease
with increasing depth of atmospheric penetration.

### 4.6 'Oumuamua retroactive prediction (P6 — retroactive, lower weight)

The non-gravitational acceleration of 'Oumuamua (arXiv:2304.06964, confirmed ~ r^{-1} to
r^{-2} scaling) is reproduced by the radially-directed solar neutrino phase-exchange force
acting on off-phase matter. The scaling should match the solar neutrino flux profile:
```
a_NG(r) ~ Phi_nu(r) * sigma_rephase * m_target^{-1}
         ~ L_nu / (4*pi*r^2) * sigma_rephase / m
         ~ r^{-2} [dominant term]
```
With a sub-leading correction from the changing re-phasing fraction (as 'Oumuamua re-phases,
sigma_rephase decreases, flattening the r dependence toward r^{-1}).

This matches the Spada (2023) observational constraint of r^{-1} to r^{-2}.

IMPORTANT CAVEAT: This is a post-hoc explanation. It is not a locked prediction in the strict
sense. It is included to document the explanatory scope of the model.

### 4.7 Three-regime neutrino pressure for extrasolar objects (P7)

Under the Option B mass convention (Section 2.6) and generation triality conservation
(RFC-028), extrasolar solid bodies entering the solar domain fall into one of exactly three
neutrino pressure regimes, determined by their source domain's generation triality
Gamma_source:

**REGIME 1 — No effect (Gamma_source = 0, triality-matched):**
- Delta_Gamma = 0 for all solar neutrino-matter interactions on the object.
- Same-phase suppression applies: solar neutrinos pass through the object with near-zero
  rephasing cross-section.
- No anomalous force, no rephasing stress, no material strength anomaly. The object's
  trajectory matches a pure gravitational prediction; it is indistinguishable from
  solar-system-origin bodies of comparable composition.
- Expected fraction: ~1/3 of all extrasolar objects (Z3 fraction, Section 2.5).

**REGIME 2a — Muon-sector object (Gamma_source = 1, one generation offset):**
- Delta_Gamma = 1 for all solar neutrino-matter interactions.
- INBOUND LEG (approach to perihelion): Solar neutrino flux is directed radially outward
  from the Sun. The phase-exchange force on the object is radially outward, opposing the
  inbound motion. The object DECELERATES relative to its gravitational trajectory. This
  deceleration onset corresponds to entering the solar neutrino cone at the heliopause.
- OUTBOUND LEG (departure from perihelion): Force is still radially outward, now aligned
  with the direction of motion. The object ACCELERATES beyond the gravitational prediction.
  Acceleration decays with r as rephasing progresses: sigma_rephase decreases as
  Gamma_object(r) -> 0 (object becomes increasingly phase-matched), flattening the r^{-2}
  profile toward r^{-1} (consistent with Spada 2023 for 'Oumuamua).
- Force scale: a(r) ~ Phi_nu(r) * sigma_rephase(Delta_Gamma=1) * Gamma_object(r) / m_object.
- Material anomaly: moderate structural stress from Fano bonding mismatch.
- Expected fraction: ~1/3 of extrasolar objects.

**REGIME 2b — Tau-sector object (Gamma_source = 2, two generation offsets):**
- Delta_Gamma = 2 for direct single-step rephasing to Gamma=0. Alternatively the object
  may rephase sequentially through an intermediate Gamma=1 state (two consecutive
  Delta_Gamma=1 hops), in which case it spends time in each intermediate state.
- Same qualitative profile as Regime 2a: DECELERATE inbound, ACCELERATE outbound.
- Force magnitude: labeled "tau-like" to identify the source generation sector. The ratio
  sigma_rephase(Regime 2b) / sigma_rephase(Regime 2a) is a Phase M kernel parameter not
  yet determined. Theory predicts the two regimes are distinguishable if this ratio differs
  from unity, which is expected under CP asymmetry (RFC-028 open question Q1). If rephasing
  proceeds through the intermediate Gamma=1 state, Regime 2b objects show a two-phase
  rephasing curve — initial fast response followed by a slower second stage.
- Material anomaly: potentially distinct from 2a in magnitude and fragmentation pattern.
- Expected fraction: ~1/3 of extrasolar objects.

Summary of regimes:

| Regime | Source Gamma | Delta_Gamma | Entry behavior | Exit behavior | Fraction |
|---|---|---|---|---|---|
| 1 | 0 (matched) | 0 | None | None | ~1/3 |
| 2a | 1 (muon-like) | 1 | Decelerate | Accelerate | ~1/3 |
| 2b | 2 (tau-like) | 2 or 1+1 | Decelerate | Accelerate | ~1/3 |

'Oumuamua identification: The confirmed radially-outward acceleration observed on the
outbound leg (2017-10-19 through departure) places 'Oumuamua in Regime 2a or 2b. The
distinction between 2a and 2b requires the inbound deceleration data (not available) or
an independent sigma_rephase measurement. The observed r^{-1} to r^{-2} scaling is
consistent with the Regime 2 force profile with declining sigma_rephase.

Falsification trigger for P7: any extrasolar object with clean inbound tracking that shows
NO pre-perihelion deceleration but DOES show post-perihelion acceleration (force inward on
inbound and outward on outbound simultaneously) would be inconsistent with this model and
require a different mechanism. An outbound force that is radially INWARD (toward the Sun)
on the outbound leg would falsify the model outright.

### 4.8 Neutrino front geometry modulation (P8)

The anomaly magnitude for Regime 2a and 2b objects is not uniform across approach
directions. It is modulated by the geometry of the object's path relative to the solar
phase front (the heliopause asymmetry established in Section 2.4).

**CASE M1 — Approach from the solar tail (anti-apex direction,
~RA=90 deg, Dec=-30 deg, opposite to solar motion):**
The Sun's ~20 km/s motion toward the apex has progressively assimilated matter in the
anti-apex direction behind it. An object approaching from this direction has been traveling
through increasingly pre-assimilated medium for an extended period before reaching the
heliopause. Solar neutrino exposure along the inbound path reduces the object's off-phase
fraction (Gamma_object) before it enters the strongest part of the solar neutrino cone.
PREDICTION: Weaker anomaly than the nose or side approach cases. Deceleration on entry and
acceleration on exit both reduced. The effective Gamma_object at heliopause crossing is
< Gamma_source.

**CASE M2 — Approach from the solar nose (apex direction,
~RA=277 deg, Dec=+30 deg, direction of solar motion):**
The object travels through unassimilated ISM with no prior solar neutrino exposure before
reaching the active neutrino trap at the heliopause nose. Gamma_object = Gamma_source at
heliopause crossing (no pre-rephasing). The heliopause nose region has the densest neutrino
cushion (competing fluxes from solar and ISM domains). The object enters maximum neutrino
pressure immediately upon crossing the heliopause.
PREDICTION: Strongest anomaly. Maximum deceleration on inbound leg, maximum acceleration
on outbound leg. Highest rephasing stress and material anomaly for solid bodies.

**CASE M3 — Lateral approach (perpendicular to apex-antapex axis):**
Moderate pre-assimilation along the lateral ISM; near-symmetric heliosphere geometry.
PREDICTION: Intermediate anomaly, between M1 and M2.

Operational model for the modulation. The effective triality content at heliopause crossing:
```
Gamma_eff = Gamma_source * exp(-integral[sigma_rephase * Phi_nu(r) * dt, inbound path])
```
where the integral runs from the onset of solar neutrino exposure along the inbound path.
For M1 (tail approach), the integral is large (long path through the solar neutrino cone
via the already-assimilated tail). For M2 (nose approach), the integral is near zero (the
object arrives from outside the cone and encounters the front abruptly). For M3, intermediate.

Falsifiable prediction: among confirmed Regime 2a or 2b objects, the anomaly magnitude
(material strength excess, non-gravitational acceleration amplitude, fragmentation rate)
should show a positive Spearman correlation with (n_approach . n_apex), where n_approach
is the object's inbound trajectory unit vector and n_apex = (RA=277 deg, Dec=+30 deg).
Objects approaching from near the apex direction should cluster at higher anomaly; objects
from the anti-apex tail direction should cluster at lower anomaly.

Regime 1 objects (no anomaly, Gamma_source=0) provide the control: they should show NO
directional preference in approach direction, since there is no rephasing to modulate.

Combined locked thresholds for P7/P8 (over N >= 6 confirmed extrasolar objects with full
trajectory data):
1. Z3 fraction: ~1/3 no anomaly, ~2/3 showing Regime 2a or 2b signal (P4 test).
2. Among anomalous objects: positive Spearman correlation between anomaly magnitude and
   (n_approach . n_apex), with p < 0.05 (one-tailed, direction pre-registered).
3. Regime 1 objects (no anomaly): approach direction distribution consistent with isotropic.
4. At least one confirmed extrasolar object tracked inbound showing pre-perihelion radial
   deceleration, consistent with Regime 2 entry behavior.

---

## 5. What Is NOT Predicted

The following are explicitly NOT predicted:

1. Which specific stars are "muon stars" or "tau stars" from our frame. C12 phase of a star
   is not observable from its electromagnetic spectrum (the Koide ratio K=2/3 holds for ALL
   stars' local matter, regardless of their phase). Only incoming objects can probe the
   phase difference.

2. The absolute magnitude of A3 (solar apex neutrino dipole). The COG model predicts A3 != 0
   but cannot yet calculate the magnitude without Phase M simulation data.

3. The re-phasing timescale in absolute units. This requires kernel parameters (sigma_rephase)
   from Phase M runs and Solar neutrino interaction cross-sections (RFC-022 input).

4. Any SM modification of neutrino oscillation parameters (theta_12, Dm^2). The C12 phase
   domain does not change the MSW oscillation physics within the Sun itself. The predicted
   effect is on long-range matter in the solar domain, not on solar interior physics.

---

## 6. Immediate Data Targets

### 6.1 Solar neutrino datasets (priority order)

1. Super-Kamiokande-IV/V long-baseline solar neutrino time series (1996-present)
   - ~20 years of 8B solar neutrino data with zenith-angle and time-variation analysis
   - Day-night asymmetry measured at -1.8 +/- 1.6% (stat) (SK collaboration, hep-ex/0309011)
   - NO existing search for solar apex dipole in the residuals → open lane
   - Contact: SK Collaboration public data products
2. Borexino solar neutrino time series/public products
   - Sub-MeV neutrino coverage (pp, pep, CNO, 7Be fluxes)
   - Directional information available for 8B via elastic scattering
3. SNO/SNO+ flavor-separated measurements (NC/CC/ES separation gives explicit flavor content)
   - NC is flavor-blind → total flux reference
   - CC/ES ratio gives effective electron neutrino fraction

### 6.2 Meteor datasets (priority order)

1. CNEOS fireball catalog (NASA JPL) — 273 entries, publicly available
   - Already used by Siraj & Loeb (2022) for material strength analysis
   - Trajectory data for directional analysis
   - Material strength (inferred ram pressure at maximum brightness)
2. CNEOS-22 (2022-07-28) and CNEOS-25 (2025-02-12) — newly confirmed interstellar candidates
   (Cloete & Loeb 2026, arXiv:2602.08956)
3. 3I/ATLAS (2025) — optical photometry available, light-curve for re-phasing analysis
4. High-cadence fireball networks (FRIPON, AllSky7, Global Meteor Network) for light-curve
   jitter analysis

---

## 7. Pre-registered Analysis Plan

### 7.1 Solar neutrino apex dipole (P1/P2)

Models:
- M0: annual + day-night only (standard oscillation correction)
- M1: M0 + apex dipole term (n_dir . n_apex, with n_apex fixed from solar apex literature)
- M2: M1 + higher harmonics + systematic nuisance terms

Primary statistic: support for A3 != 0, stable sign across detector subsets.

Locked thresholds:
1. Per-dataset apex coefficient: |A3|/sigma_A3 >= 3
2. Combined significance (SK + Borexino + SNO): >= 5 sigma
3. Model preference: DeltaBIC(M0 -> M1) <= -10
4. Fitted A3 sign must be consistent across primary datasets

Robustness checks:
1. Leave-one-era-out stability
2. Detector systematic nuisance terms
3. Sidereal vs solar-time leakage check
4. Bootstrap resampling (90% same-sign threshold)

### 7.2 Interstellar meteor directional anomaly (P4/P5)

Models:
- N0: baseline predictors (speed, mass proxy, entry angle, estimated composition)
- N1: N0 + apex directional term (angle between trajectory and n_apex)
- N2: N1 + path-integrated solar neutrino exposure proxy (total fluence along path)

Primary statistics:
1. Material strength vs. trajectory direction correlation
2. Fragmentation onset depth vs. solar neutrino column density
3. Z3 fraction test: among confirmed interstellar meteors, fraction showing anomalies vs. 2/3

Locked thresholds:
1. DeltaBIC(N0 -> N2) <= -10 (directional terms improve fit)
2. Z3 fraction test: observed anomalous fraction within [0.45, 0.90] 2-sigma interval of 2/3
3. Coefficient signs stable under bootstrap (>= 90% same-sign)
4. At least one anomaly metric (material strength or fragmentation) at corrected p < 0.01

### 7.3 'Oumuamua re-analysis (P6)

Fit the non-gravitational acceleration profile a_NG(r) to:
- Model A: standard outgassing (r^{-2} scaled by sublimation curve)
- Model B: COG re-phasing (r^{-2} times decreasing sigma_rephase(r))
- Model C: radiation pressure (r^{-2} times sublimation area proxy)

Compare using AIC/BIC. Model B adds one free parameter (initial sigma_rephase).
Prediction: Model B should fit at least as well as Model A with the added freedom,
AND the fitted sigma_rephase should be positive and physically reasonable.

---

## 8. Falsification Criteria (Locked)

Hypothesis considered falsified if ALL hold:
1. Solar datasets: no reproducible apex-aligned residual after annual/day-night controls
2. Sign of fitted A3 is unstable or inconsistent across datasets
3. Meteor anomaly models: no directional/re-phasing incremental signal over baseline
4. Z3 fraction test: observed anomalous fraction of interstellar meteors is < 0.1 or > 0.95
   (inconsistent with 2/3 prediction at >3 sigma)

Numerical falsification trigger:
1. No primary solar dataset reaches 3 sigma on |A3|
2. Combined apex evidence remains < 5 sigma
3. DeltaBIC(M0 -> M1) > -10 AND DeltaBIC(N0 -> N2) > -10

Three-regime model (P7/P8) additionally falsified if:
4. Any extrasolar object with clean inbound tracking shows radially INWARD non-gravitational
   acceleration on the outbound leg.
5. Over N >= 6 confirmed extrasolar objects: anomaly magnitudes show NEGATIVE correlation
   with (n_approach . n_apex) at > 2 sigma (i.e., tail-approach objects are systematically
   MORE anomalous than nose-approach objects — the reverse of the M1/M2 prediction).
6. Regime 1 (no anomaly) objects cluster in a specific approach direction (they should be
   isotropically distributed if triality assignment is random).

Partial support requires:
1. Consistent non-zero apex term in at least 2 independent solar datasets.
2. Meteor directional signal surviving standard covariates.
3. Z3 fraction within 1 sigma of 2/3 for N >= 6 confirmed interstellar meteors.
4. At least one inbound extrasolar object detection showing pre-perihelion deceleration.

---

## 9. Explicit Divergence from Standard Model

This RFC predicts phenomena not present in standard neutrino treatment:

1. Stellar-neutrino-driven generation-domain assimilation — matter is asymptotically driven
   toward local stellar C12 phase by sustained neutrino bombardment
2. Frame-relative generation labels — "Gen1" is defined locally by each star's C12 phase
3. Phase-domain fronts at stellar boundaries — neutrino trapping at phase-domain boundaries
4. Non-gravitational acceleration of off-phase interstellar objects — caused by the Ghosh et
   al. (2022) directional neutrino force mechanism acting on off-phase matter
5. Systematic material-strength anomalies in interstellar meteors — off-phase matter has
   different internal cohesion from differently-structured C12 orbit geometry

The Ghosh et al. (2022) directional neutrino force provides a SM-COMPATIBLE proximate mechanism
for points 4 and part of point 3. The COG model provides the UNDERLYING CAUSE (discrete phase
domains) while standard SM provides the PROXIMATE MECHANISM (directional neutrino exchange force).
This makes the prediction doubly motivated and harder to dismiss.

---

## 10. Literature Summary (v2 addition)

The following papers were reviewed in constructing this RFC:

### Solar neutrino experiments
- Super-K I/II solar neutrino measurements (hep-ex/0508053, 0803.4312): establish baseline
  annual and day-night analyses; NO apex search done — open lane
- Day-night asymmetry measured: -1.8 +/- 1.6% (stat) +1.3/-1.2 (syst)% (hep-ex/0309011)
- MSW/matter effect review (Smirnov 2004, hep-ph/0412391; 2003, hep-ph/0305106): establishes
  known matter-effect physics that must be subtracted
- Neutrino oscillations in complex/inhomogeneous medium (Smirnov 2022, arXiv:2212.10242):
  raises domain-wall effects as open question in neutrino oscillation theory

### Neutrino forces and backgrounds
- CRITICAL: Ghosh, Grossman, Tangarife, Xu, Yu (2022, arXiv:2209.07082): directional neutrino
  backgrounds produce 1/r enhanced force in the direction of neutrino flow, enhanced by
  many orders of magnitude over vacuum case. Directly relevant to assimilation mechanism.
- Horowitz & Pantaleone (1993, hep-ph/9306222): long-range neutrino forces from cosmic
  background, 1/r scaling at short distances
- Ferrer, Grifols, Nowakowski (1999, hep-ph/9906463): relic neutrino background SCREENS
  the 2-neutrino exchange force at cosmological distances (important: solar domain is small
  compared to screening length, so screening is negligible)

### Heliosphere structure
- Opher, Stone, Liewer, Gombosi (2006, astro-ph/0606324): ISM magnetic field produces
  north-south heliospheric asymmetry — heliosphere already known to be nose-tail asymmetric
- Bladek & Ratkiewicz (2023, arXiv:2309.16345): heliopause nose direction depends on
  interstellar magnetic field; nose always perpendicular to maximum ISMF intensity
- Strumik et al. (2014, arXiv:1401.7607): LISM plasma penetration across reconnecting
  heliopause — ISM material regularly enters the heliosphere
- Heliosphere in time (Muller et al. 2008, arXiv:0810.0441): heliosphere size varies with
  ISM density; Sun spends ~99.4% of time in warm low-density ISM (appropriate for large domain)

### Interstellar objects and meteors
- CRITICAL: Siraj & Loeb (2022, arXiv:2209.09905): IM1 and IM2 ranked #1 and #3 in material
  strength among 273 CNEOS fireballs; 3.5 and 2.6 sigma outliers. P(by chance) ~ 10^{-4}.
- Cloete & Loeb (2026, arXiv:2602.08956): CNEOS-22 at 8.7 sigma, CNEOS-25 at 5.5 sigma
  — two new confirmed interstellar meteors with full velocity calibration
- Siraj & Loeb (2019, arXiv:1904.07224): IM1 identification and number density estimate;
  interstellar population is large
- 'Oumuamua non-gravitational acceleration (Spada 2023, arXiv:2304.06964): confirms r^{-1}
  to r^{-2} scaling, radially directed — no standard explanation satisfactory
- 'Oumuamua outgassing limits (Trilling et al. 2018, arXiv:1811.08072): strict upper limits
  on CO/CO2 — rules out standard cometary explanation for non-gravitational acceleration
- 'Oumuamua spin/outgassing incompatibility (Rafikov 2018, arXiv:1809.06389): outgassing
  torques would disrupt spin state; non-gravitational acceleration not from outgassing
- Galactic trajectories of 1I/2I/3I (Kakharov & Loeb 2024, arXiv:2408.02739): 1I from
  young (~1 Gyr) system; 2I from intermediate (~3.8 Gyr) system; 3I/ATLAS from old thick-disk
  (~9.6 Gyr) system — different stellar ages → potentially different C12 phase histories
- Vaubaillon (2022, arXiv:2211.02305): skeptical view of IM1 interstellar claim — velocity
  accuracy concerns. Note: superseded by DoD confirmation.

### Relevant observational gaps (where the COG prediction is open)
1. No search for solar apex dipole in SK/Borexino/SNO solar neutrino residuals
2. No systematic directional analysis of CNEOS catalog vs solar apex vector
3. No study of interstellar meteor fragmentation light-curve vs solar neutrino column density
4. No re-analysis of 'Oumuamua acceleration under phase-exchange force model

All four gaps represent immediately actionable observational tests.

---

## 11. Decision Gate

Proceed to dedicated implementation scripts only after this lock:

1. `build_v3_solar_apex_anisotropy_probe_v1.py` — load SK/Borexino public data, fit M0/M1/M2,
   compute A3 and DeltaBIC
2. `build_v3_interstellar_meteor_directional_v1.py` — load CNEOS catalog, compute apex angle
   for each trajectory, fit N0/N1/N2 models, compute Z3 fraction statistics
3. `build_v3_oumuamua_rephasing_force_fit_v1.py` — fit 'Oumuamua non-gravitational
   acceleration profile to SM neutrino force model with phase-exchange cross-section

Output contract per script:
1. Machine-readable coefficient table + uncertainties
2. Pre-reg pass/fail table for P1-P6
3. One-paragraph executive verdict

---

## 12. Notes on Interpretation Discipline

1. This RFC locks predictions BEFORE fitting.
2. The existing evidence (Section 3) is flagged as post-hoc and carries reduced weight.
3. Null results must be reported and are informative.
4. If primary signals fail, mechanism is downgraded or replaced; no post-hoc reinterpretation
   without a new RFC with explicit label RFC-027-Amendment.
5. The frame-relativity of "Gen1" (Section 2.1) is a STRUCTURAL claim about the model, not
   a prediction. It cannot be falsified directly, only the downstream predictions can.
6. The SM-compatible Ghosh et al. mechanism (Section 2.3) is relevant regardless of whether
   the COG model is correct — the directional neutrino force from the Sun on interstellar
   objects is a real SM prediction. If 'Oumuamua's acceleration matches r^{-2} with the right
   amplitude for this force, that is evidence for the SM mechanism whether or not COG is right.
