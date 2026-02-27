# COG Glossary and Thesaurus
# Intuition-First Reference for the Causal Octonion Graph Framework

Status: Living draft (2026-02-27)
Audience: Research Director, workers, curious readers
Purpose: Overstuffed reference to jog physical intuition. Every entry lists
standard names, better/alternative names, and multiple framings of what the
thing actually IS in the COG model.

---

## How to Read This Document

Each entry has:
- **Standard name** — the term used in mainstream physics or mathematics
- **COG name(s)** — what we call it here, or what it really is
- **The kernel sentence** — one sentence that strips away all abstraction
- **Extended intuition** — multiple framings, analogies, and cross-links
- **What it is NOT** — common misconceptions in the COG context

Entries are grouped thematically, not alphabetically, because meaning comes
from context.

---

## Part I: Space

---

### Space

**Standard names:** space, spatial dimensions, 3D, position, location, extent

**COG names:** graph separation, causal distance, edge count, topological reach,
adjacency depth, connection density, relational gap

**Kernel sentence:**
Space is the count of hops you need to traverse the causal graph to get from
one node to another.

**Extended intuition:**

1. There is no container. Space is not a box that particles sit inside. Space
   IS the relationship structure of the graph. Two nodes that are directly
   connected by an edge are "touching." Two nodes with no path between them
   are not in causal contact at all.

2. Space is a noun we use for a verb. "Being in space" means "being reachable
   from here via some finite chain of edges." Space is the reachability
   structure.

3. Distance is dynamic. The edge count between two nodes can change as new
   edges are created by spawning (D4). A particle that "moves" is a motif
   that recruits new adjacencies on one side and loses them on the other.

4. Dimension is emergent, not postulated. That we observe 3 large spatial
   dimensions means that the causal graph has a characteristic branching
   structure such that the number of nodes within hop-distance r grows roughly
   as r^3. It need not have been 3.

5. Locality means graph-locality. Two nodes interact only if they share an
   edge (or are at hop-distance 1). There is no action at a distance. "Nearby"
   means small edge count, not small coordinate difference.

6. Better names for space that convey its real nature:
   - The adjacency web
   - The reachability field
   - The connection fabric
   - Relational distance
   - The hop metric

**What it is NOT:**
Not a continuous manifold. Not a background. Not independent of its contents.
You cannot have space without nodes and edges.

---

### Distance

**Standard names:** distance, length, spatial separation, metric, norm

**COG names:** edge-count gap, hop distance, causal separation, graph geodesic,
interaction path length, next-interaction node gap (RFC-035)

**Kernel sentence:**
Distance is the minimum number of causal edges a message must traverse to
travel from node A to node B.

**Extended intuition:**

1. Distance is quantised. The minimum non-zero distance is 1 (adjacent nodes).
   There is no half-edge. The Planck length is the edge length.

2. Distance is asymmetric in the DAG. Because edges are directed, there may
   be a shorter path from A to B than from B to A (or no return path at all).
   This asymmetry is the arrow of causality.

3. Two-body distance policy (RFC-035): one hop per tick, impulse at arrival,
   topology/distance updated every tick. Observable: distance_delta =
   future_edge_distance - past_edge_distance. Positive = repulsion, negative
   = attraction.

4. Distance to interaction: the most operationally useful distance is not
   "where am I" but "how long until the next message arrives." Distance is
   a countdown, not a coordinate.

---

### Dimension

**Standard names:** spatial dimension, degrees of freedom, dimensionality

**COG names:** branching exponent, growth order of the ball, coordination
number regime, graph regularity class

**Kernel sentence:**
Dimension is the exponent d such that the number of nodes within hop-distance r
grows like r^d in the large-r limit.

**Extended intuition:**

1. Dimension need not be integer. Fractal or hierarchical graphs can have
   non-integer effective dimension. The fact that we observe d=3 is a
   dynamical claim about the actual graph, not a postulate.

2. Why 3+1? D4 triality selects 4 dimensions as special (the four normed
   division algebra dimensions are 1,2,4,8). The octonion structure naturally
   foliates the 4D graph into 3 spatial + 1 temporal because e7 (the vacuum
   axis) plays a qualitatively different role from e1...e6.

3. Compactified dimensions are just tight cycles. Extra dimensions that we
   cannot resolve macroscopically are subgraphs that wrap around quickly at
   scale smaller than the Planck length (= 1 hop).

---

## Part II: Time

---

### Time

**Standard names:** time, temporal dimension, duration, the t coordinate,
the direction of increasing entropy

**COG names:** tick depth, evaluation order, non-associativity sequence,
cocycle forced ordering, update round number, causal layer index

**Kernel sentence:**
Time is the forced sequential ordering that emerges because octonion
multiplication is non-associative: (a·b)·c ≠ a·(b·c), so you cannot
postpone or reorder operations.

**Extended intuition:**

1. Time is not a dimension added to space. It is the output of the algebra
   itself. If the algebra were associative (quaternions = 4D), you could
   reorder operations freely — no preferred sequence, no time. Non-
   associativity makes order matter.

2. Two clocks, not one:
   - topoDepth: position in the global causal DAG. How many layers deep from
     the initial node. This is "cosmological time" or "causal depth." Global.
   - tickCount: how many local update rounds a node has undergone. This is
     "proper time." Local. Two nodes at the same causal depth can have
     different tick counts if one has been busy (high interaction rate).

3. Time is a cocycle choice. The 7 directed Fano cycles could have been
   oriented 2^7 = 128 different ways. Each orientation defines a different
   "arrow of time." Our universe chose one. That choice is the initial
   condition of physics, not derived from anything deeper.

4. The temporal commit operator is T(psi) = e7 * psi. This is not a metaphor.
   It is a literal multiplication of the node state by the vacuum axis basis
   element. One tick = one left-multiplication by e7.

5. Better names for time that convey its real nature:
   - The cocycle sequence
   - Forced evaluation order
   - Non-associativity depth
   - Update round number
   - The algebra's tick
   - Sequential commitment depth

**What it is NOT:**
Not a background parameter t ∈ ℝ. Not smooth. Not reversible in general
(because the DAG is acyclic — you cannot traverse an edge backwards).
Not the fourth spatial dimension.

---

### The Arrow of Time

**Standard names:** arrow of time, time asymmetry, irreversibility,
second law, entropy increase

**COG names:** cocycle orientation, Fano direction, acyclicity of the DAG,
non-invertibility of the update rule, causal one-wayness

**Kernel sentence:**
Time has a direction because the 7 Fano cycles are oriented (each triple
eᵢeⱼeₖ has a designated forward direction), and the DAG has no backward edges.

**Extended intuition:**

1. The arrow is baked into the multiplication table, not derived from
   thermodynamics. You cannot "reverse" an octonion product because the
   sign would flip: eⱼeᵢ = -eᵢeⱼ. Anti-commutativity IS irreversibility
   at the algebraic level.

2. XOR tells you which basis element results from a product. The 2-cocycle
   (the sign) tells you which direction the cycle runs. These are two separate
   facts. The XOR is symmetric; the orientation is not.

3. Entropy increase follows from motif stability. Most perturbations of a
   stable motif lead to less-stable states. The dynamics tends toward
   attractors. This is the statistical origin of entropy, derived from the
   graph dynamics rather than postulated.

---

### Causality

**Standard names:** causality, causal structure, light cone, causal order

**COG names:** DAG structure, edge directionality, forward reachability,
causal cone, ancestral graph, topological ordering constraint

**Kernel sentence:**
Causality is the directed edge structure: node A can influence node B only if
there exists a directed path from A to B in the causal graph.

**Extended intuition:**

1. The light cone is the forward reachability set. All nodes reachable from A
   in exactly n hops form a discrete sphere of causal influence at radius n.

2. Spacelike separation means no directed path in either direction.
   Two nodes are "simultaneous" if neither can reach the other.

3. There is no global time coordinate forced on you — only the partial order
   given by the DAG. Different foliations of the DAG into "time slices"
   correspond to different reference frames.

---

### Tick

**Standard names:** elementary time step, Planck time, fundamental period

**COG names:** tick, update round, local clock increment, evaluation step,
temporal commit, one application of T

**Kernel sentence:**
One tick is one application of the update rule U to a node: its state advances
from psi_t to psi_{t+1} = U(T(psi_t), incoming_messages, trace).

**Extended intuition:**

1. The Planck time IS one tick. It is not a derived quantity; it is the
   primitive unit of local time.

2. Ticks are not synchronised globally. Node A at tick 47 and node B at tick
   47 are not "simultaneous" unless they happen to be at the same causal
   depth.

3. The temporal commit T(psi) = e7 * psi precedes all other operations in
   each tick. It is the universal "clock pulse" that all nodes receive from
   the vacuum.

---

## Part III: Matter and Mass

---

### Matter

**Standard names:** matter, substance, stuff, particles, material content,
fermions

**COG names:** stable motifs, persistent patterns, attractor cycles, non-vacuum
node configurations, self-sustaining state sequences

**Kernel sentence:**
Matter is a pattern in the causal graph that repeats itself across ticks —
a motif that resists the vacuum drive and maintains its identity over time.

**Extended intuition:**

1. There is no "stuff." Matter is not made of anything. It is a distinguished
   recurring configuration, the way a standing wave is not made of something
   different from the water — it is just water doing a particular thing
   persistently.

2. Stability is the criterion. A motif is matter if it is an attractor of the
   dynamics. Random noise is not matter; it disperses. A particle is a noise
   pattern that happens to be self-reinforcing under the local update rule.

3. Matter vs vacuum: the vacuum is the background tick (T(psi) = e7*psi for
   all nodes). Matter is any configuration that deviates from the vacuum
   and sustains that deviation.

4. Better names for matter:
   - Stable motif
   - Attractor pattern
   - Persistent deviation from vacuum
   - Self-reinforcing cycle
   - Computational invariant
   - Locked-in repetition

---

### Mass

**Standard names:** mass, rest mass, inertia, m, gravitational charge

**COG names:** computational drag, self-collision rate, scalar channel
accumulation frequency, e0 generation rate, update resistance,
state-change reluctance

**Kernel sentence:**
Mass is how often a node self-interacts (eᵢ·eᵢ = -e0), piling amplitude
into the scalar e0 channel, creating a kind of computational inertia that
resists being kicked out of its current pattern.

**Extended intuition:**

1. The e0 channel is where mass lives. Recall that eᵢ·eᵢ = -e0 for all
   imaginary basis elements i=1..7. Every self-interaction produces e0.
   A node that cycles through many Fano interactions per tick accumulates
   a lot of e0 amplitude. That accumulation IS mass.

2. Mass is a frequency. A heavier particle is one whose motif returns to
   a high-e0 state more frequently. Mass ~ (self-collision rate per tick).

3. Mass as computational drag: a heavier node is harder to perturb because
   its motif has more "inertia" — the high e0 amplitude weights the
   multiplicative fold toward the identity, resisting changes.

4. m=0 means no self-collisions. A photon (vacuum phase pulse) traverses the
   graph without accumulating e0 because it never cycles back through the
   same basis element twice.

5. The Koide formula (if derived here) would follow from the specific
   self-collision rates of the three charged lepton motifs being linked by
   the Witt pair structure.

6. Better names for mass:
   - Computational drag
   - Self-collision frequency
   - e0 accumulation rate
   - Update inertia
   - Scalar saturation density
   - Motif return frequency to identity

---

### Energy

**Standard names:** energy, E, Hamiltonian, total energy, kinetic + potential

**COG names:** update rate, state change intensity, interaction throughput,
message flux density, tick-work rate, departure-from-vacuum magnitude

**Kernel sentence:**
Energy is how much the current node state differs from the vacuum state per
tick, i.e., the rate of doing non-trivial computation.

**Extended intuition:**

1. E=0 is the vacuum. A node whose state matches the vacuum trajectory
   (T(psi) = e7*psi with no deviation) has zero energy. Any deviation costs
   work to maintain.

2. Energy is not conserved at individual nodes; it is conserved globally
   across the interaction fold. When two nodes exchange a message, the total
   departure-from-vacuum is preserved (by the fold law D3).

3. Kinetic vs potential energy: kinetic energy is the state-change intensity
   of a motif in motion (shifting adjacencies per tick). Potential energy is
   the accumulated edge-structure tension between two nodes (a function of
   their relative phase at arrival time).

4. E=mc² follows here from: energy (update rate) scales with mass (self-
   collision frequency) times the square of the propagation speed (1 edge/tick
   = c). More collisions per tick means more state change per tick.

5. Better names for energy:
   - Update intensity
   - Non-vacuum departure rate
   - Computational work rate
   - State change budget per tick
   - Interaction flux

---

### Momentum

**Standard names:** momentum, p, mv, linear momentum, translational inertia

**COG names:** directed update bias, motif drift rate, adjacency shift
velocity, graph traversal direction, net edge-gain rate

**Kernel sentence:**
Momentum is the net rate at which a motif is recruiting new adjacencies on
one side of its extent and shedding them on the other — i.e., how fast the
motif is "walking" through the graph.

**Extended intuition:**

1. A motif at rest (p=0) gains and loses adjacencies symmetrically.
   A moving motif (p≠0) gains adjacencies in one direction systematically.

2. p=mv: a heavier motif (high self-collision rate) carries more momentum at
   the same drift speed because each of its self-collisions deposits amplitude
   in e0, making each adjacency-shift more "loaded."

3. Conservation of momentum is the statement that the total drift rate of
   all interacting motifs is preserved across message exchanges. This follows
   from the D1 (multiplicative combine) rule and the locality of interactions.

---

## Part IV: Forces and Interactions

---

### Force / Interaction

**Standard names:** force, interaction, fundamental force, field force,
F = ma

**COG names:** edge-mediated state shift, message content, impulse at arrival,
interaction kick, boundary message fold, phase disruption

**Kernel sentence:**
A force is a message arriving at a node via a causal edge that shifts the
node's state away from its free trajectory.

**Extended intuition:**

1. There are no force fields in a background space. Forces are messages —
   state vectors transmitted along specific edges at specific ticks.

2. The "strength" of a force is the magnitude of the message content relative
   to the node's own state. A strong force sends a message whose amplitude
   is comparable to the receiver's amplitude. A weak force sends a small
   perturbation.

3. Repulsion vs attraction from phase: the relative phase of sender and
   receiver at message arrival determines the sign of the distance_delta.
   Like-phase: receiver is pushed away (repulsion). Opposite-phase:
   receiver is pulled in (attraction). This is the microscopic origin
   of charge-sign interaction.

4. Force carrier = message type. The photon is a vacuum phase message (e7
   channel). The gluon is a color-exchange message (Fano-line specific).
   The W/Z bosons are phase-rotation messages.

5. Better names for force:
   - Message content
   - Edge-delivered kick
   - Arrival impulse
   - Phase perturbation
   - Interaction packet
   - State redirect

---

### Charge

**Standard names:** electric charge, charge, q, ±e

**COG names:** XOR multiplication handedness, left-right sign asymmetry,
Fano orientation index, interaction sign class, phase winding direction

**Kernel sentence:**
Charge is which "hand" a motif uses when multiplying — whether it left-
multiplies or right-multiplies the incoming state, which flips the sign of
the result for imaginary basis interactions.

**Extended intuition:**

1. Left-hit vs right-hit: for two distinct imaginary basis elements eᵢ, eⱼ
   (i≠j), left multiplication (eᵢ·ψ) and right multiplication (ψ·eᵢ) give
   the same output INDEX (XOR) but OPPOSITE SIGNS. This sign asymmetry is
   charge.

2. Charge quantisation is automatic. Because the XOR table is finite (8
   basis elements), there are only finitely many sign patterns. Charge cannot
   be 0.7e — only integer multiples of the elementary sign flip.

3. Charge conservation is the statement that the handedness of a motif's
   interaction sequence is preserved under free propagation. It changes only
   when a charge-carrying message is absorbed.

4. Antiparticle = sign flip. The antiparticle of a motif is the same motif
   with the interaction handedness reversed. The 2-cocycle sign for each
   Fano product flips, so positive and negative "charge" map onto ± sign
   in the multiplication law.

5. The Furey construction makes this precise: the minimal left ideal gives
   all charge-1/3 and charge-2/3 states from the same Witt raising operators,
   with the charge value being the eigenvalue of the U(1) generator.

6. Better names for charge:
   - Interaction handedness
   - Sign class
   - Multiplication orientation
   - Left-right asymmetry index
   - Fano cycle winding number

---

### Color Charge

**Standard names:** color charge, strong color, red/green/blue, SU(3) charge

**COG names:** Witt pair index, ideal generator label, Furey channel number,
octonion pair slot, raising operator subscript

**Kernel sentence:**
Color charge is which of the three Witt pairs (e6,e1), (e2,e5), (e3,e4) a
quark motif is "spinning in" — its identity as an excitation in one of the
three independent quaternionic subplanes of the octonion algebra.

**Extended intuition:**

1. The octonion algebra contains three independent quaternionic subalgebras,
   each spanned by a Witt pair and e0. The three colors are the three
   channels of this triple structure.

2. Color confinement means that only combinations of Witt-pair excitations
   that cancel to the vacuum (e7 axis) are stable in isolation. A single
   quark carries one Witt pair slot open; three quarks close all three;
   a meson pairs a slot with its conjugate.

3. Color "charge" cannot be seen individually because the three Witt pairs
   are entangled via the Fano plane — each pair participates in products
   with both other pairs, so a single-color state would immediately generate
   the others in the next tick. Confinement is not "gluons making a bag";
   it is algebraic inevitability.

4. There are exactly 3 colors because there are exactly 3 Witt pairs in
   O (for the 6 imaginary basis elements e1..e6, the vacuum axis e7 excluded).
   This is not tunable.

5. Better names for color charge:
   - Witt pair slot
   - Ideal generator index
   - Octonion subplane label
   - Furey raising index
   - Quaternionic sub-channel

---

### Spin

**Standard names:** spin, intrinsic angular momentum, s=1/2, spinor

**COG names:** phase cycle period, orbit length under T, motif rotation
period, temporal handedness, half-turn symmetry class

**Kernel sentence:**
Spin-1/2 means the motif returns to its original state after applying the
temporal operator T twice (period 4 under T, but phase-equivalent after 2) —
it takes two full "ticks" to complete one identity cycle.

**Extended intuition:**

1. The temporal operator T(psi) = e7*psi has period 4: T⁴(psi) = psi for
   the vacuum orbit. A spin-1/2 object uses T² = −1 as its identity, so
   geometrically it needs 4π of "rotation" to return, while a spin-1 object
   needs only 2π.

2. Spinor vs vector: a vector motif (spin-1) returns to itself after one
   full application of the vacuum drive cycle. A spinor motif (spin-1/2)
   returns to itself (up to sign) after one cycle, and to itself without
   sign flip after two cycles. The 4-periodicity of e7 multiplication is
   exactly this.

3. The Furey minimal left ideal gives spinors automatically. The Witt raising
   operators α† act on the vacuum ω and produce spin-1/2 states (νe, e⁻, u,
   d quarks) with no additional input.

4. Better names for spin:
   - Phase cycle period
   - Temporal orbit class
   - T-periodicity
   - Half-turn class
   - Rotation order under vacuum driver

---

## Part V: The Vacuum

---

### Vacuum

**Standard names:** vacuum, empty space, ground state, zero-point field,
quantum vacuum

**COG names:** background tick, temporal substrate, vacuum drive state,
ground hum, the default trajectory, zero-deviation state

**Kernel sentence:**
The vacuum is the state in which every node simply tracks the temporal
commit operator: psi_{t+1} = T(psi_t) = e7*psi_t, with no messages and
no interaction, cycling endlessly through the 4-periodic vacuum orbit.

**Extended intuition:**

1. The vacuum is not empty. It is maximally active — every node is doing
   the full temporal commit every tick. "Empty space" is the state of
   maximum background computation with zero net information content.

2. The vacuum orbit: 2ω = e0 + i·e7 is the vacuum idempotent in the
   Furey/Witt construction. The vacuum state cycles through a period-4
   orbit under repeated T application. This 4-cycle IS the background
   "ticking" of the universe.

3. Vacuum fluctuations in standard QFT correspond here to small coherent
   perturbations of nodes away from their vacuum trajectory that do not
   sustain long enough to form a stable motif. They are real computational
   events, not probability clouds.

4. The photon propagates as a vacuum phase pulse — a coherent ripple in
   the vacuum orbit that transmits the phase of one region of the graph
   to another without depositing any e0 amplitude (no mass).

5. Better names for the vacuum:
   - Background tick
   - Default trajectory
   - The ground hum
   - Zero-information substrate
   - Temporal carrier field
   - The ether tick (but not the luminiferous ether!)

---

### Vacuum Axis (e7)

**Standard names:** (no standard name — specific to this framework)

**COG names:** temporal commit direction, vacuum driver, e7, binary 111,
the universal tick, the master clock element

**Kernel sentence:**
e7 = the octonion basis element labeled 111 in binary; it is the only
imaginary basis element at Hamming distance 1 from all other imaginary
elements, and the operator T(psi) = e7*psi implements one temporal tick.

**Extended intuition:**

1. e7 is the most "central" imaginary octonion in the binary labeling:
   e1=001, e2=010, e3=011, e4=100, e5=101, e6=110, e7=111. XOR-ing 111
   with any other 3-bit label flips all bits that are different — it has
   Hamming distance 3 from e0=000 and distance 1 from e1..e6.

2. e7 is the only imaginary element that anti-commutes with ALL other
   imaginary elements: e7·eᵢ = -eᵢ·e7 for all i≠7. It is "orthogonal
   to everything."

3. e7 is the vacuum axis in the Witt basis: (e6,e1), (e2,e5), (e3,e4)
   are the three Witt pairs, and e7 sits at the apex as the pairing
   reference. The 24-cell packing in 4D centers on e7.

4. In XOR arithmetic: e7 acts as the universal complement (flips all
   three bits). It maps each basis element to the one element it would
   need to XOR with to produce itself. In this sense it is the "complement
   operator" of the octonion space.

---

## Part VI: Quantum Phenomena (Reinterpreted)

---

### Uncertainty Principle

**Standard names:** Heisenberg uncertainty, Δx·Δp ≥ ℏ/2,
quantum indeterminacy

**COG names:** light-cone incompleteness, causal horizon fog, missing
information from outside the reachable graph, sub-Planck inaccessibility

**Kernel sentence:**
You cannot simultaneously know exact position and momentum of a motif
because "knowing exact position" requires resolving sub-Planck structure
(below the edge length) and "knowing exact momentum" requires resolving
global drift over many hops — and those two observation scales are
incompatible.

**Extended intuition:**

1. The uncertainty principle is NOT a statement about the universe being
   fundamentally random. It is a statement about what an observer at one
   node can KNOW about a motif at another node given only the information
   that has arrived via causal edges.

2. Sub-Planck structure doesn't exist. You cannot localise a particle to
   less than one edge length because there is nothing below the edge length.
   The discreteness resolves the paradox: "perfect position knowledge" is
   simply not a coherent concept.

3. Momentum requires averaging over many ticks. To measure drift rate
   precisely, you need to observe over many ticks, during which the position
   is spreading across multiple hops. The two measurements compete for
   the same information budget.

4. Better names for the uncertainty principle:
   - Causal resolution limit
   - Observer graph-horizon bound
   - Planck-scale inaccessibility
   - Information incompleteness bound

---

### Superposition

**Standard names:** quantum superposition, wave function, state vector,
linear combination of eigenstates

**COG names:** observer state estimate, light-cone shadow, projected
epistemic state, incomplete causal information

**Kernel sentence:**
Superposition is not a physical state of the universe — it is the
description of reality from the perspective of an observer who does not
yet have all the causal information needed to determine the actual state.

**Extended intuition:**

1. The universe is superdeterministic. Given exact initial microstate and
   the update rule, every future state is fixed. There is no fundamental
   probability. The "wavefunction" is not an ontological object.

2. "Superposition" is what the universe looks like to an observer inside it
   who only has access to the information that has reached them via causal
   edges (their past light cone). They cannot determine which of several
   consistent states is actual.

3. The amplitude for each classical outcome is the projection of the
   observer's state onto the subspace consistent with each outcome, given
   the causal information available. Born rule follows from the structure
   of the D5 projection contract.

4. Collapse is not collapse. When an observer "measures" and gets a definite
   answer, nothing happens to the universe — a new causal edge is created
   between the measuring apparatus and the particle, bringing the missing
   information into the observer's light cone.

5. Better names for superposition:
   - Observer epistemic state
   - Causal horizon shadow
   - Light-cone projection
   - Missing-information state

---

### Entanglement

**Standard names:** quantum entanglement, nonlocal correlations,
EPR correlations, Bell inequality violation

**COG names:** shared causal ancestry, common-ancestor correlation,
correlated initial conditions, DAG sibling correlation

**Kernel sentence:**
Entanglement is the correlation between two nodes that originated from a
common ancestor in the causal DAG — their states are correlated because
they were produced by the same event, not because they are connected now.

**Extended intuition:**

1. No nonlocal signalling. The correlations in entanglement cannot be used
   to send information faster than c because doing so would require
   creating a causal edge between two spacelike-separated nodes, which
   violates the DAG structure.

2. The correlation is real. Two nodes that split from a common source carry
   complementary state information from that split event. When one is
   "measured" (a new edge arrives), the correlations with the other
   are constrained by what the common source state was.

3. The Bell inequalities are violated in COG because the DAG allows
   common-ancestor correlations that are stronger than classical local-
   hidden-variable theories. The common ancestor IS the hidden variable,
   but it is in the DAG structure, not in any local variable attached
   to the particles.

4. Better names for entanglement:
   - Common-ancestry correlation
   - DAG sibling relation
   - Shared origin signature
   - Split-event memory

---

### Wave-Particle Duality

**Standard names:** wave-particle duality, de Broglie wave, dual nature

**COG names:** motif-message duality, node-edge description switch,
particle-propagator duality

**Kernel sentence:**
"Wave" is the description of a motif when you focus on how it propagates
its influence across many nodes (edge/message picture). "Particle" is the
description when you focus on its localised stable node configuration.
Same object, different observational framing.

**Extended intuition:**

1. The "wave" IS the message propagating along edges. When a particle emits
   a photon, a message propagates along causal edges. That message has a
   periodic structure (the vacuum orbit phase) that produces interference.

2. The "particle" IS the attractor motif sitting at a set of nodes.
   It is localised in the sense that it occupies a specific subset of
   the graph.

3. Double-slit experiment: the message propagates along ALL causal paths
   simultaneously (it is simply a message traveling along edges, which
   can branch). The interference comes from the phase of the message along
   different paths combining at the detector node. No mystery.

---

### The Wave Function

**Standard names:** wave function, ψ, state vector, probability amplitude

**COG names:** D5 projection state, observer causal shadow, epistemic state
vector, light-cone projection amplitude, causal information encoding

**Kernel sentence:**
The wave function is the encoding of everything an observer can predict
about a system, given the messages that have arrived at the observer's
node from inside their past light cone.

**Extended intuition:**

1. The wave function is not a field in space. It is an information-
   theoretic object — the observer's best summary of the world given
   their available causal information.

2. It is complex because the fundamental algebra is complex octonionic
   (ℂ⊗𝕆). The real and imaginary parts track the two independent
   phase channels (e0 and i·e0) of the projected state.

3. Its amplitude squared gives probabilities via the Born rule, which
   follows from the D5 projection contract (the rule for computing
   observable quantities from the full microstate).

---

## Part VII: Light and Radiation

---

### Light

**Standard names:** light, electromagnetic radiation, photon, c

**COG names:** vacuum phase pulse, e7-propagation packet, causal wave front,
massless state ripple, background-phase messenger

**Kernel sentence:**
Light is a coherent ripple in the vacuum phase that propagates at one hop
per tick (the maximum causal speed) by pure edge traversal, without
accumulating e0 amplitude (no mass, no self-collision).

**Extended intuition:**

1. c = 1 hop/tick. This is a definition, not a measured constant. The speed
   of light is the maximum causal propagation speed because information can
   only travel along edges, one edge per tick. Any slower object has a motif
   that "stops" at some hops to self-interact.

2. Light has no mass because a photon motif never revisits the same basis
   element in sequence: it propagates through the Fano structure without
   looping back, so it never computes eᵢ·eᵢ = -e0. Zero e0 accumulation
   = zero mass.

3. Frequency of light = phase winding rate of the vacuum orbit per unit
   causal distance. Higher frequency = tighter phase winding = more e0
   equivalent energy per message packet.

4. Polarisation = the orientation of the e7-propagation in the Fano plane.
   Linear polarisation = a fixed Fano direction. Circular polarisation =
   a rotating Fano direction.

5. The photon is not yet a first-class object in the current COG
   implementation. It is approximated by vacuum phase propagation effects.
   Full photon = explicit emission/propagation/detection lifecycle in the
   event engine (near-term work item).

6. Better names for light:
   - Vacuum ripple
   - Phase wave front
   - e7 messenger
   - Causal propagation packet
   - Background phase messenger

---

### Speed of Light

**Standard names:** c, speed of light, 299,792,458 m/s

**COG names:** causal edge rate, maximum propagation speed, 1 hop per tick,
the graph velocity ceiling

**Kernel sentence:**
c = 1 hop per tick. It is not a measured constant of nature but the
definition of the unit of speed in a graph where the edge length is the
Planck length and the tick is the Planck time.

**Extended intuition:**

1. Nothing travels "faster than light" because there is no mechanism to
   traverse an edge in fewer than one tick. The DAG edge is the indivisible
   unit of causal connection.

2. c appears dimensionful (m/s) only because we chose to measure distance in
   meters and time in seconds rather than in hops and ticks. In natural units
   (Planck length = Planck time = 1), c = 1.

3. Massive objects travel at v < c because their motif spends some ticks
   doing self-interactions (eᵢ·eᵢ = -e0) rather than traversing edges. The
   fraction of ticks spent traversing vs self-interacting gives v/c.

---

## Part VIII: The Algebra

---

### The Fano Plane

**Standard names:** Fano plane, PG(2,2), projective plane of order 2,
octonion multiplication mnemonic

**COG names:** the 7-point interaction map, the multiplication index table,
the triad structure, the Fano sign lattice

**Kernel sentence:**
The Fano plane is a diagram of 7 points and 7 lines (each line through
3 points) encoding which octonion basis elements interact and which basis
element their product produces.

**Extended intuition:**

1. Every product eᵢ·eⱼ (for i,j ∈ 1..7, i≠j) is determined by the Fano
   plane: the third point on the line through i and j gives the output
   index k, and the orientation of the line (clockwise/counter-clockwise)
   gives the sign.

2. The Fano plane encodes the STRUCTURE of the interaction network. It is
   not just a mnemonic; it IS the physics. The 7 lines of the Fano plane
   are the 7 independent Fano cycles / lines of the projective geometry.

3. The XOR rule: binary labeling e1=001, e2=010, e3=011, e4=100, e5=101,
   e6=110, e7=111. For any two imaginary basis elements eᵢ, eⱼ: the index
   of their product is i XOR j. This works for all 42 directed products.

4. The 2-cocycle: the XOR rule gives the index but not the sign. The sign
   requires the Fano orientation (which way each directed triple runs).
   There are 2^7 = 128 consistent orientation choices. We fix one by the
   CONVENTIONS.md lock.

5. Better names for the Fano plane:
   - The interaction topology
   - The 7-point multiplication map
   - The octonion interaction lattice
   - The triad diagram

---

### Non-Associativity

**Standard names:** non-associativity, failure of associativity,
(a·b)·c ≠ a·(b·c)

**COG names:** forced evaluation order, sequential commitment, time-generator,
order-dependence of multiplication, irreversibility kernel

**Kernel sentence:**
Non-associativity means that the order in which you combine three basis
elements matters — there is no way to "batch" three operations together —
and this forced sequential ordering IS the origin of time.

**Extended intuition:**

1. Associative algebras (reals, complex, quaternions) can be evaluated in
   any order. No preferred sequence = no intrinsic time. The moment you add
   a third pair to the Fano plane (going from quaternions to octonions),
   you lose associativity and gain time.

2. Alternativity saves you from chaos. Octonions are not fully associative
   but they ARE alternative: a·(a·b) = (a·a)·b and (a·b)·a = a·(b·a).
   This means self-consistency is maintained even though order matters.

3. The associator [a,b,c] = (a·b)·c - a·(b·c) measures "how much time
   you are in." For associative algebras the associator is zero (frozen
   time). For octonions it is nonzero exactly for the 42 directed Fano
   products.

4. Better names for non-associativity:
   - Time generator
   - Order sensitivity
   - Sequential commitment requirement
   - Evaluation irreversibility
   - Three-body non-linearity

---

### XOR

**Standard names:** XOR, exclusive-or, bitwise XOR, ⊕

**COG names:** octonion index rule, product channel selector, binary
addition mod 2, the timeless skeleton of multiplication

**Kernel sentence:**
XOR is the rule that determines WHICH basis element results from multiplying
two imaginary octonion basis elements — the sign is separate (and contains
all the physics of time).

**Extended intuition:**

1. XOR is associative, commutative, and forms the group (ℤ/2)³. In
   isolation it defines a timeless algebra — the group algebra of (ℤ/2)³.
   No physics yet.

2. XOR + 2-cocycle = octonions. The XOR rule picks the output channel.
   The Fano 2-cocycle (the 7 oriented cycles) picks the sign. The cocycle
   breaks both commutativity (relative sign flips) and associativity
   (the ordered triple orientation). This is where time enters.

3. Conservation law: for any valid Fano product eᵢ·eⱼ = ±eₖ, we have
   i XOR j XOR k = 0 (the three indices XOR to zero). This is the discrete
   analogue of conservation of a ℤ/2 quantum number.

4. Better names for XOR in this context:
   - Index selector
   - Channel mapper
   - Binary product rule
   - The timeless skeleton

---

### Triality (D4)

**Standard names:** triality, SO(8) triality, D4 triality, outer automorphism

**COG names:** three-way symmetry, spinor-vector equivalence, the octonion
generator, three-generation origin

**Kernel sentence:**
Triality is the 3-fold symmetry of the D4 Lie algebra that permutes its
three inequivalent 8-dimensional representations (one vector, two spinors)
into each other — and this is exactly the algebraic structure needed to
construct the octonion multiplication.

**Extended intuition:**

1. In 4D, the Dynkin diagram D4 has a symmetry group S3 (order 6) instead
   of the usual Z2. This extra symmetry is triality. No other dimension has
   it.

2. The three 8-dimensional representations of D4 are: the SO(8) vector rep,
   the left-spinor rep, and the right-spinor rep. Triality cycles them. This
   maps onto: spacetime direction / matter particle / antimatter particle.

3. The octonion algebra is constructed from D4 triality: the trilinear form
   V × S₊ × S₋ → ℝ satisfying the triality condition IS the octonion
   multiplication table.

4. Three quark generations arise because there are three Witt pairs and
   triality relates them. The three copies of the Furey ideal chain
   (one per Witt orientation) give three generations with the same charges
   but different masses (different self-collision rates).

5. Better names for triality:
   - Three-way symmetry
   - Spinor-vector-spinor cycle
   - The generation rotator
   - D4 outer symmetry
   - Octonion construction key

---

## Part IX: Particles

---

### Particle

**Standard names:** particle, elementary particle, fundamental particle,
point particle

**COG names:** stable motif, attractor cycle, persistent pattern,
orbit-closed configuration, lock-in state, non-dispersing excitation

**Kernel sentence:**
A particle is a configuration of node states that repeats itself across
ticks (period p under the update rule) and that resists perturbation by
returning to the same orbit after a small push.

**Extended intuition:**

1. "Elementary" means lowest-energy stable motif in its charge class.
   An electron is the lightest stable motif with charge -1 (negative
   interaction handedness). It is elementary not because it has no parts
   but because no smaller stable configuration carries that charge.

2. Composite particles are motifs of motifs. A proton is a three-node
   motif (three quark sub-motifs) whose combined Witt indices close
   (color neutral) and whose combined charges add to +1.

3. Particle identity is the orbit, not the nodes. If two motifs have
   identical orbit structures under the update rule, they are identical
   particles. There is no "this particular electron" distinguished from
   "that particular electron."

4. Better names for particle:
   - Stable motif
   - Attractor cycle
   - Self-sustaining pattern
   - Locked orbit
   - Persistent deviation from vacuum

---

### Electron

**Standard names:** electron, e⁻, lepton, fundamental fermion

**COG names:** minimal charged Furey ideal excitation, lightest spin-1/2
motif with unit negative interaction handedness, e6-e1 Witt chain terminus

**Kernel sentence:**
The electron is the stable motif produced by applying the Witt raising
operator α₁† to the vacuum ω in the minimal left ideal of ℂ⊗𝕆, having
charge -1 from its interaction handedness and mass from its self-collision
frequency in the e0 channel.

**Extended intuition:**

1. The electron charge is -1 because it uses the "negative" interaction
   handedness (right-multiplication dominates in the Furey chain).

2. The electron mass is the smallest of the charged leptons because its
   self-collision rate (e0 accumulation frequency) is lowest — it has the
   simplest Witt chain structure, occupying only one Witt pair slot.

3. The positron (e⁺) is the same motif with the interaction handedness
   flipped. It is not a separate object; it is the charge conjugate.

---

### Neutrino

**Standard names:** neutrino, ν, neutral lepton, ghostly particle

**COG names:** neutral Furey ideal state, Witt chain vacuum direction,
non-interacting ideal excitation, zero-charge spin-1/2 motif

**Kernel sentence:**
The neutrino is the Furey ideal excitation that sits in the "vacuum
direction" of the Witt chain — it has the same spin-1/2 character as
the electron but zero interaction handedness (no charge).

**Extended intuition:**

1. Neutrinos interact weakly because their ideal state does not carry
   the U(1) eigenvalue that couples to photons. They ride the Fano
   structure without triggering the sign-flip interaction.

2. Neutrino mass (tiny but nonzero) comes from a small e0 accumulation
   rate from the vacuum drive T acting on their Witt-chain state.

3. The three neutrino flavors correspond to the three Witt pair
   orientations, just as the three charged leptons do.

---

### Quark

**Standard names:** quark, up/down/strange/charm/bottom/top, color charge,
confined particle

**COG names:** Witt-channel sub-motif, fractional-charge Furey excitation,
confined color-channel state, SU(3) triplet component

**Kernel sentence:**
A quark is an excitation in ONE of the three Witt pair channels of the
Furey ideal, carrying a fractional charge (±1/3 or ±2/3) and a color
index (which Witt pair) that must be combined with two other quarks to
form a color-neutral (all-three-Witt-pairs-closed) hadron.

**Extended intuition:**

1. Fractional charges arise from the Furey construction. The U(1)_em
   generator assigns charge +2/3 to u quarks and -1/3 to d quarks by
   acting on the specific Witt components of the ideal chain.

2. Three colors arise because there are three Witt pairs. Each quark
   is an excitation in exactly one of the three.

3. Confinement: the three-Witt-pair structure means single-quark states
   always "leak" into the other channels on the next tick, destabilizing
   unless two or three quarks are present to close the algebra.

---

### Photon

**Standard names:** photon, γ, light quantum, force carrier of electromagnetism

**COG names:** vacuum phase pulse, e7 propagation packet, massless vector
messenger, phase ripple carrier

**Kernel sentence:**
A photon is a directed phase ripple in the vacuum orbit that propagates
at c = 1 hop/tick, carries energy proportional to its phase winding rate,
and couples to charged motifs by depositing a phase kick proportional
to the charge.

---

## Part X: Fields and Gravity

---

### Field

**Standard names:** field, quantum field, classical field, background field

**COG names:** distributed motif pattern, node-state density map,
message flux distribution, graph-wide state correlation

**Kernel sentence:**
A field is a pattern of correlations across many nodes of the causal graph
— a description of what state the graph is in over a large region,
averaged over many nodes.

**Extended intuition:**

1. Fields are not fundamental. In COG, the fundamental objects are nodes,
   edges, and states. A "field value at point x" is shorthand for "the
   average state of all nodes in the region near x."

2. The electromagnetic field is the distribution of photon messages flowing
   through the graph. Where the message density is high, the field is strong.

3. Quantum field theory's creation/annihilation operators correspond to:
   spawning (D4) a new node in a motif state (creation) and having a node
   decay out of its motif (annihilation).

---

### Gravity

**Standard names:** gravity, gravitation, curvature of spacetime, G,
general relativity

**COG names:** computational drag field, mass-density slowdown, causal graph
curvature, update-rate distortion, tick-rate differential, edge-density bias

**Kernel sentence:**
Gravity is the distortion of the causal graph structure near high-mass
(high-self-collision-rate) nodes: dense matter slows down the local update
rate and curves the local adjacency structure, making nearby motifs drift
inward.

**Extended intuition:**

1. Spacetime curvature = causal graph distortion. Near a massive object,
   the graph has more edges per volume (higher local connectivity) and
   lower effective update rate (mass consumes ticks for self-collision).
   This is the discrete analogue of spacetime curvature.

2. Gravitational attraction: a motif drifting toward a massive node finds
   that the effective "shortest path" to anything curves toward the mass,
   because the mass-dense region has more nodes per hop and thus shorter
   graph geodesics. The motif "falls" because the geodesic curves.

3. Gravitational redshift: a photon climbing out of a gravitational well
   has to traverse more edges per unit of observer time (the graph is denser
   near the mass), so its effective phase winding rate (frequency) appears
   lower to a distant observer.

4. Not yet quantitatively derived in COG (blocked on scale calibration,
   RFC-030, RFC-052). Current status: conceptual proxy only.

5. Better names for gravity:
   - Computational drag field
   - Mass-density curvature
   - Tick-rate distortion
   - Causal graph geometry
   - Edge-density bias

---

## Part XI: Observables and Measurement

---

### Observable

**Standard names:** observable, measurable quantity, Hermitian operator,
expectation value

**COG names:** D5 projection, causal read-out, graph-state extraction,
light-cone projection value, microstate coarse-graining

**Kernel sentence:**
An observable is a function of the full microstate that can be evaluated
from the information available in the observer's past light cone, as
defined by the D5 projection contract.

**Extended intuition:**

1. Not all properties of a node are observable. The full microstate (all
   16 integer components of ψ ∈ ℂ⊗𝕆 at each node) is in principle
   complete, but an observer can only access the projection onto the
   subspace consistent with the messages they have received.

2. D5 defines which projections are physical. The minimal projection
   (piObsMinimal) and extended projection (piObsExtended) are the two
   currently defined profiles. Choosing a projection profile is choosing
   which properties are "real" for this measurement.

3. Permutation invariance: a valid observable must not depend on the
   arbitrary labeling of nodes. This is the discrete analogue of
   diffeomorphism invariance in general relativity.

---

### Measurement

**Standard names:** measurement, observation, quantum measurement,
collapse of wave function, von Neumann measurement

**COG names:** causal edge creation, information channel opening,
light-cone expansion, new-adjacency event

**Kernel sentence:**
Measurement is the creation of a new causal edge between the measuring
apparatus node and the measured system node — it brings previously
unavailable microstate information into the observer's light cone.

**Extended intuition:**

1. No collapse needed. The system was always in a definite state. The
   measurement just reveals which state it was in by establishing a
   causal connection.

2. Measurement is irreversible because it creates a new DAG edge. Directed
   acyclic graph edges cannot be undone. Once you have "seen" a result,
   the causal history is permanently altered.

3. The "measurement problem" of standard quantum mechanics dissolves
   because there is no wave function to collapse — the wave function was
   always just the observer's epistemic state, and measurement updates it
   by providing new causal information.

---

## Part XII: Conservation Laws and Symmetries

---

### Conservation Law

**Standard names:** conservation law, conserved quantity, Noether's theorem,
symmetry implies conservation

**COG names:** motif invariant, orbit closure, fold-law preservation,
XOR conservation, interaction-round symmetry

**Kernel sentence:**
A conserved quantity is a property of a motif (or set of motifs) that
the update rule never changes — either because it is algebraically fixed
by the multiplication table or because the interaction fold law preserves it.

**Extended intuition:**

1. Energy conservation: the total departure-from-vacuum amplitude across
   all interacting nodes is preserved by the multiplicative fold (D1+D3).

2. Charge conservation: the interaction handedness (XOR orientation) of a
   motif is unchanged by any message that does not itself carry opposite
   handedness. Charge can only change if a charged message is absorbed.

3. Baryon number conservation: the three-Witt-pair closure is preserved
   by the color interaction. A proton cannot decay unless all three Witt
   channels simultaneously flip, which requires an energy scale above any
   message available in normal conditions.

4. The XOR conservation law: for any Fano product eᵢ·eⱼ = ±eₖ, we have
   i ⊕ j ⊕ k = 0. This is a genuine conserved (ℤ/2)³ quantum number.

---

### Symmetry

**Standard names:** symmetry, gauge symmetry, global symmetry, Lie group

**COG names:** update-rule invariance, motif orbit equivalence, relabeling
freedom, interaction-pattern equivalence class

**Kernel sentence:**
A symmetry is a transformation of the node labels or state components that
leaves the update rule U completely unchanged.

**Extended intuition:**

1. Gauge symmetry is labeling freedom. If you relabel which Witt pair
   is "red" vs "green" vs "blue," the physics doesn't change because
   the Fano interaction structure is symmetric under permutations of
   the color channels. Gauge freedom is not a deep property of reality;
   it is a statement about our labeling choices.

2. Lorentz symmetry (to be derived): in the large-scale limit, the causal
   DAG should exhibit approximate Lorentz covariance. This is a claim
   about the effective description of the graph at scales much larger than
   the hop length.

3. CPT: charge conjugation (flip interaction handedness) + parity (flip
   Fano orientation) + time reversal (flip DAG edge direction) is a
   symmetry of the fundamental update rule. Individual C, P, T are not
   separately symmetries (as observed in the weak interaction).

---

## Appendix: Quick Reference Name Table

| Standard Term | COG / Better Name(s) |
|---|---|
| Space | Graph separation, adjacency web, hop metric |
| Time | Tick depth, cocycle sequence, evaluation order |
| Mass | Computational drag, self-collision rate, e0 accumulation |
| Energy | Update intensity, non-vacuum departure rate |
| Momentum | Motif drift rate, adjacency shift velocity |
| Charge | Interaction handedness, XOR orientation, sign class |
| Spin | Phase cycle period, T-periodicity, orbit length |
| Force | Message content, edge-delivered kick, arrival impulse |
| Vacuum | Background tick, ground hum, default trajectory |
| Light | Vacuum phase pulse, causal wave front, e7 propagation |
| c (speed) | Causal edge rate, 1 hop per tick |
| Particle | Stable motif, attractor cycle, persistent pattern |
| Field | Distributed motif density, node-state correlation |
| Gravity | Computational drag field, causal graph curvature |
| Superposition | Observer epistemic state, light-cone shadow |
| Entanglement | Common-ancestry correlation, DAG sibling relation |
| Measurement | Causal edge creation, light-cone expansion |
| Wave function | D5 projection, causal shadow encoding |
| Collapse | Causal determination, new-edge information reveal |
| Uncertainty | Causal resolution limit, observer horizon bound |
| Color charge | Witt pair slot, ideal generator index |
| Fano plane | 7-point interaction map, triad structure |
| Non-associativity | Forced evaluation order, time generator |
| XOR | Index selector, channel mapper, timeless skeleton |
| Triality | Three-way symmetry, generation rotator |
| e7 (basis element) | Vacuum axis, temporal commit direction, master clock |
| e0 (basis element) | Scalar vacuum, mass accumulator, identity channel |
| Electron | Minimal charged Furey excitation, lightest charge-1 motif |
| Quark | Witt-channel sub-motif, fractional-charge confined state |
| Photon | Vacuum ripple, phase wave front, e7 messenger |
| Neutrino | Neutral ideal excitation, Witt-vacuum direction |
| Big Bang | The Root Node, causal graph origin, primal spawn event |
| Black hole | Topological sink, isolated sub-DAG, terminal edge-cluster |
| Singularity | Maximum-density clique, saturation point, edge-count ceiling |
| Dark energy | Background spawn rate, vacuum volume inflation |
| Dark matter | Sterile high-inertia motif, pure-e0 accumulator |
| Fermion | Half-turn motif, spinor-class attractor |
| Boson | Phase-shift messenger, vacuum-synchronous wave |
| Antimatter | Fano-inverted motif, reverse-handed cycle |
| Strong force | Witt-pair binding, color-channel cross-talk |
| Weak force | Witt-pair rotation, ideal-channel swap |

---

*This document is a living draft. Add entries as new physical mechanisms are
identified. Priority: anything that standard physics names badly.*

---

## Part XIII: Cosmology and the Macroscopic Graph

---

### The Big Bang

**Standard names:** Big Bang, initial singularity, cosmic origin, t=0

**COG names:** the Root Node, causal graph origin, tick zero, the initial
state vector, the primal spawn event, the first tick, the lone ancestor

**Kernel sentence:**
The Big Bang is the single ancestral root node of the directed acyclic graph
from which all subsequent nodes, edges, and tick depths recursively spawned
via the D4 update and spawn rules.

**Extended intuition:**

1. There is no "before." Time (tick depth) is a measure of causal hops away
   from the root node. "Before the Big Bang" is a grammatical construction
   that has no referent in the DAG — it asks for a node with tick depth < 0,
   which does not exist. The question dissolves, not gets answered.

2. The universe did not expand into anything. The root node began executing
   the temporal commit operator T(psi) = e7*psi, triggering the D4 spawn
   rules, which generated new nodes, and built the adjacency web from
   scratch. There was no pre-existing space to expand into — the edges ARE
   space.

3. CMB uniformity is automatic. The early graph had a very small maximum
   hop-distance. Everything was tightly connected and algebraically correlated
   before the graph grew large enough to effectively isolate different regions.
   No inflation mechanism needed: small graph = everything in causal contact
   = uniform background.

4. The initial state vector is the one free parameter. We do not derive the
   root node's state from anything deeper — it is the initial condition.
   All physics is downstream of that one 16-integer assignment.

5. Better names for the Big Bang:
   - The Root Node
   - Tick zero
   - The primal spawn event
   - The first execution
   - DAG genesis

**What it is NOT:**
Not an explosion in space. Not a point of infinite density. Not a
singularity in any meaningful sense — it is simply the topological
start of the DAG, the node with no ancestors.

---

### The Singularity (Does Not Exist)

**Standard names:** singularity, point of infinite density, Penrose
singularity, Big Bang singularity, black hole singularity

**COG names:** edge-count ceiling, maximum-density clique, saturation
point, complete-subgraph limit, Planck-scale cap

**Kernel sentence:**
A singularity cannot exist in a discrete graph because density is bounded
above by the complete clique: n nodes can have at most n(n-1)/2 edges,
which is a large but finite number, never infinity.

**Extended intuition:**

1. Infinity is a continuum artifact. Singularities appear in general
   relativity because the differential equations are written on a smooth
   manifold, and smooth manifolds permit arbitrarily small volumes and
   thus arbitrarily high densities. In a discrete graph, the minimum
   volume is one node and the maximum edge density per node is the number
   of neighbours — finite.

2. What happens instead: as mass accumulates in a region, the local graph
   becomes more densely connected (more edges per node). At some point every
   node in the region is adjacent to every other node — a complete clique.
   This is maximum density. The system cannot get denser. Curvature saturates.

3. The GR singularity is where the approximation breaks. The continuum
   description of spacetime is valid down to some scale. Below the Planck
   length (= 1 hop), the continuum approximation breaks down, and the
   discrete graph takes over. The "singularity" is precisely the point
   where you hit the Planck-scale discreteness. It was never real.

4. Better names for what a singularity actually is:
   - The edge-count ceiling
   - Maximum-density clique
   - The Planck saturation point
   - Where the continuum approximation expires
   - The complete-subgraph limit

**What it is NOT:**
Not a real physical location. Not a place where physics breaks down.
The physics is fine — the continuum description breaks down, revealing
the underlying discrete structure that was always there.

---

### Black Hole

**Standard names:** black hole, event horizon, singularity,
Schwarzschild radius, gravitational collapse

**COG names:** topological sink, infinite-drag region, causal cul-de-sac,
isolated sub-DAG, terminal edge-cluster, one-way information valve,
maximum-clique region, inward-only directed subgraph

**Kernel sentence:**
A black hole is a region of the causal graph where the mass-induced edge
density is so extreme that all forward-directed paths point exclusively
inward — no causal edge exits the region, severing it from the rest of
the network.

**Extended intuition:**

1. There is no singularity inside. The interior is a maximally dense
   complete (or near-complete) clique of nodes churning through the vacuum
   drive at maximum rate. The self-collision rate is saturated. Density
   is finite and maximal, not infinite.

2. The event horizon is a topological boundary, not a physical surface.
   It is the set of nodes from which no directed path reaches the exterior.
   It has no material existence — you cannot touch it, it has no substance.
   It is a property of the graph's directed structure.

3. Inside the horizon, time still runs. Nodes inside still tick, still
   apply T(psi) = e7*psi, still interact with their neighbours. They are
   just causally disconnected from the exterior. Local physics is unchanged.

4. Hawking radiation: boundary nodes — those sitting at the topological
   edge of the black hole, adjacent to both interior and exterior nodes —
   occasionally spawn new outward-directed edges as part of the vacuum
   drive. A vacuum phase pulse (e7 message) leaks out. Over astronomically
   long times, this slowly depletes the black hole's node count. The
   radiation is thermal because the interior state information is scrambled
   by the dense clique dynamics.

5. Black hole information paradox: in COG there is no paradox. The
   information is preserved in the node states inside the clique. It is
   causally inaccessible to the exterior but not destroyed. The DAG is
   deterministic and invertible in principle (given the full microstate).

6. Merger: when two black holes merge, two isolated sub-DAGs become
   mutually adjacent, briefly creating a larger dense cluster before
   settling to a new maximal-clique equilibrium.

7. Better names for a black hole:
   - Topological sink
   - Causal cul-de-sac
   - One-way information valve
   - Maximum-density clique region
   - Inward-only subgraph

**What it is NOT:**
Not a hole in space. Not a point. Not infinite density. Not a place
where physics stops — the local physics inside is ordinary graph
dynamics, just causally isolated.

---

### Dark Energy

**Standard names:** dark energy, cosmological constant, Lambda,
metric expansion of space, vacuum energy

**COG names:** background spawn rate, baseline D4 node-generation,
vacuum volume inflation, default edge-creation bias, intrinsic graph
growth rate, tick-driven adjacency expansion

**Kernel sentence:**
Dark energy is the intrinsic, constant baseline rate at which the temporal
commit operator spontaneously generates new nodes and edges even in the
vacuum — inflating the hop-distance between unconnected motifs over time.

**Extended intuition:**

1. Dark energy is not a substance. It is a property of the update rule D4
   (the spawn rule). At every tick, there is a small but nonzero probability
   that the vacuum drive spontaneously creates new nodes in the interstices
   of the graph. These new nodes increase the hop-distance between existing
   nodes.

2. Space expands because new nodes are inserted into the adjacency web. If
   two galaxies are separated by N hops, and the vacuum between them spawns
   new nodes, their hop-distance increases to N+k even if neither galaxy has
   shifted its adjacencies (no momentum). This is Hubble expansion.

3. It appears as a "repulsive force" at macroscopic scales, but locally
   the spawn rate is so small it is easily overwhelmed by the dense edge-
   clustering of massive motifs (gravity). At short ranges gravity wins;
   at cosmological ranges expansion wins.

4. The cosmological constant is just the spawn rate parameter of D4. It
   is dimensionless in COG units: (new nodes per existing node per tick).
   Its observed value is tiny (~10^-122 in Planck units) — a small but
   nonzero bias in the D4 rule.

5. Better names for dark energy:
   - Background spawn rate
   - Vacuum volume inflation
   - Tick-driven graph growth
   - Intrinsic D4 bias
   - Default adjacency expansion

---

### Dark Matter

**Standard names:** dark matter, non-baryonic mass, WIMPs, axions,
hidden sector, missing mass

**COG names:** sterile high-inertia motifs, disconnected Furey channel,
pure-e0 accumulators, photon-decoupled attractors, non-EM-coupling motifs

**Kernel sentence:**
Dark matter consists of stable motifs that accumulate e0 amplitude heavily
(generating mass and curving the causal graph) but lack the specific Witt-
pair interaction handedness required to couple to e7 vacuum phase pulses
(light).

**Extended intuition:**

1. Gravity without light. Dark matter cycles heavily through self-
   interactions (eᵢ·eᵢ = -e0), creating computational drag and distorting
   the local causal graph — this is gravity. But it does not carry the
   Witt-pair XOR signature needed to generate or absorb an e7 message
   (photon), so it is electromagnetically invisible.

2. Dark matter is not exotic. It is just a motif class that sits in a
   different sector of the Furey ideal structure from ordinary matter — one
   that couples to the vacuum drive (hence mass and gravity) but not to
   the EM channel. This is entirely natural in a framework with multiple
   Witt pair structures.

3. Candidate structure: a motif whose ideal generator sits in the
   e0 + e7 subspace only — the scalar-vacuum combination — rather than
   in any Witt pair. Such a motif accumulates e0 via self-collision but
   never sources an off-axis phase flip, so it never couples to the
   Witt-pair channels (color, EM).

4. Better names for dark matter:
   - Sterile high-inertia motif
   - Pure-e0 accumulator
   - Photon-decoupled attractor
   - Vacuum-only coupling motif
   - Non-EM Furey sector

---

### Inflation

**Standard names:** cosmic inflation, inflationary epoch, exponential
expansion, inflaton field

**COG names:** early high-spawn-rate epoch, root-node cascade, rapid D4
amplification, initial edge-burst, dense-DAG bootstrap phase

**Kernel sentence:**
Inflation is the period immediately after the root-node creation when the
D4 spawn rate was orders of magnitude higher than its current value —
a transient burst of node generation that rapidly expanded the causal
graph before settling to the present low-rate expansion.

**Extended intuition:**

1. No inflaton field needed. The high early spawn rate is a transient
   property of the initial state vector, not a separate field. The root
   node began in a high-energy state (high e0 amplitude) that drove
   rapid spawning, which decayed as the energy distributed across
   the growing graph.

2. Inflation solves the horizon problem automatically. During the high-
   spawn phase, new nodes were created already correlated with their
   neighbours (they inherit state from the spawning node). The CMB
   uniformity comes from this shared parentage, not from causal contact
   during inflation.

---

## Part XIV: Motif Classifications

---

### Fermion

**Standard names:** fermion, half-integer spin, matter particle,
Pauli exclusion adherent, s = 1/2

**COG names:** half-turn motif, sign-flipping cycle, spinor-class attractor,
period-4 temporal orbit, T²=-1 class, two-loop identity

**Kernel sentence:**
A fermion is a motif that requires two full applications of the vacuum
driver cycle to return to its original state — it acquires a sign flip
after one loop (T² = -1), so only after T⁴ is identity restored.

**Extended intuition:**

1. The sign flip is physical. After one vacuum driver cycle (T² applied
   once), the fermion state is -psi, not +psi. Its "clock" runs at half
   the rate of the vacuum. This half-rate is spin-1/2.

2. Pauli exclusion from XOR cancellation. Two identical fermions occupying
   the exact same node state would have their combined state = psi XOR psi
   = 0 (annihilation). The algebra forbids two identical fermions from
   occupying the same state. This is not a postulate; it falls out of the
   structure automatically.

3. All matter is fermionic because the Furey minimal left ideal construction
   produces T² = -1 states (spinors) for the electron, neutrino, and quark
   families. The construction predicts fermions, not bosons, as stable matter.

4. Better names for fermion:
   - Half-turn motif
   - Two-loop identity cycle
   - Sign-flip matter
   - Spinor-class attractor

---

### Boson

**Standard names:** boson, integer spin, force carrier, field quantum,
s = 0 or 1

**COG names:** phase-shift messenger, integer-period motif, vacuum-synchronous
wave, edge-traversing state redirect, T²=+1 class, single-loop identity

**Kernel sentence:**
A boson is a motif or message that completes its temporal identity cycle
in a single vacuum driver loop — T² = +1, no sign flip — meaning any
number of identical bosonic states can stack constructively.

**Extended intuition:**

1. No sign flip = no exclusion. Because T² applied to a boson returns +psi
   (not -psi), two identical bosons at the same state combine to 2*psi, not
   0. Amplitude adds. This is Bose-Einstein statistics — any number of
   bosons can occupy the same state.

2. Force carriers are bosons because messages (edges) can carry arbitrary
   amplitude. The electromagnetic field is strong because many photons can
   pile onto the same edge, constructively adding their phase kicks.

3. The photon (spin-1) is the simplest boson: a vacuum phase pulse that
   propagates at c with T² = +1. The Higgs (spin-0) is a scalar boson:
   it does not rotate under T at all (period 1).

4. Better names for boson:
   - Single-loop identity motif
   - Constructive-stack messenger
   - Phase-shift carrier
   - T²=+1 class

---

### Antimatter

**Standard names:** antimatter, antiparticle, charge conjugate,
positron, antiproton

**COG names:** Fano-inverted motif, reverse-handed cycle, conjugate ideal
excitation, opposite-cocycle state, sign-flipped Furey chain

**Kernel sentence:**
Antimatter is the same structural motif as matter executing with the opposite
Fano 2-cocycle orientation — every product sign is flipped, reversing all
charge-type quantum numbers while leaving mass and spin unchanged.

**Extended intuition:**

1. Antimatter does NOT travel backward in time. Tick depth is strictly
   non-decreasing in the DAG. The antiparticle propagates forward in tick
   depth just like its matter counterpart. What is reversed is the algebra:
   the 2-cocycle orientation (the Fano directed cycles) is flipped.

2. Annihilation is algebraic cancellation. When a motif and its Fano-
   inverted partner meet at the same node, their states satisfy:
   psi + psi_conjugate = 2 * Re(psi). The imaginary (Fano-charged) parts
   cancel exactly, and all the accumulated e0 amplitude is ejected as
   massless e7 messages (photon pairs).

3. Why more matter than antimatter: the initial root node state vector
   was not symmetric between the two cocycle orientations. This broken
   symmetry at tick zero propagates forward: a slight excess of one Fano
   orientation over the other through the entire causal history.

4. Better names for antimatter:
   - Fano-inverted motif
   - Reverse-cocycle state
   - Conjugate ideal excitation
   - Sign-flipped interaction partner

---

## Part XV: The Complete Force Picture

---

### The Strong Force

**Standard names:** strong nuclear force, color force, QCD,
gluon exchange, asymptotic freedom, confinement

**COG names:** Witt-pair binding, color-channel cross-talk, Fano-line
enforcement, algebraic confinement, inter-ideal coupling, three-channel
closure requirement

**Kernel sentence:**
The strong force is the inevitable algebraic cross-talk between the three
Witt pairs: because they share the Fano plane, an open fractional excitation
in one channel violently drives messages in the others until all three channels
close into a color-neutral state.

**Extended intuition:**

1. It is "strong" because it is the primary structural requirement of the
   octonion algebra, not a perturbative correction. You cannot have a quark
   in isolation — the algebra immediately generates compensating messages
   in the other Witt pair channels, with message amplitude comparable to
   the quark's own state amplitude.

2. Asymptotic freedom: at very short distances (few hops), the inter-quark
   messages are weak (the quarks are tightly co-located and the algebraic
   "tension" is low). At large distances (many hops), the tension grows
   because the Fano cross-coupling must span more edges. This is the running
   coupling, derived from the hop-scale dependence of the message amplitude.

3. Confinement: a lone quark (an open Witt slot) is algebraically unstable.
   Each tick it generates state-change intensity (energy) in the adjacent
   Witt channels. The system reaches minimum computational drag only when
   all three Witt channels are closed (baryon) or a channel is paired with
   its conjugate (meson). The confinement energy is the accumulated cross-
   talk cost of maintaining an open slot.

4. Gluons are the color-exchange messages — Fano-line-specific state packets
   passed rapidly between quarks to continuously rebalance the color-neutral
   total. They carry color charge themselves (they are superpositions of
   Witt-pair messages) which is why gluons interact with each other.

5. Better names for the strong force:
   - Witt-pair binding
   - Color-channel cross-talk
   - Algebraic confinement pressure
   - Fano-line enforcement
   - Three-channel closure tension

---

### The Weak Force

**Standard names:** weak nuclear force, weak interaction, flavor changing,
W and Z bosons, beta decay, radioactive decay

**COG names:** Witt-pair rotation message, ideal-channel swap, generation-
shifting kick, triality-phase disruption, flavor-rewriting message,
cocycle-rotation carrier

**Kernel sentence:**
The weak force is a massive phase-rotation message (the W/Z boson) that
interacts with the Furey ideal structure of a motif, algebraically pivoting
it from one Witt-pair configuration (flavor) into another, fundamentally
changing the particle's identity.

**Extended intuition:**

1. The weak force re-writes particles; the others redirect them. The EM
   force pushes a charged motif (changes momentum). The strong force
   binds color-charged motifs (changes adjacency). The weak force changes
   what a particle IS — up quark becomes down quark, electron becomes
   neutrino — by rotating the Furey ideal chain within the Witt structure.

2. It is "weak" because the W and Z bosons are massive (high e0 accumulation
   rate). A force carrier that is heavy can only propagate a few hops before
   its computational drag causes it to self-interact back to vacuum. Short
   range follows from high mass: range ~ 1/mass in hop units.

3. Parity violation: the weak force exclusively couples to one-handed
   (left-handed) fermion states — specifically, the left-chiral component
   of the Furey ideal excitation. This is not mysterious in COG: the W
   boson message has a definite Fano orientation that only phase-matches
   one chirality of the spinor-class motif. Right-handed fermions do not
   have the matching XOR signature to absorb a W message.

4. Beta decay: in beta-minus decay, a d quark (Witt-pair slot with charge
   -1/3) absorbs a virtual W⁻ message (Witt rotation) and becomes a u quark
   (Witt-pair slot with charge +2/3). The W⁻ then decays to an electron plus
   antineutrino — the e0 amplitude of the W deposited into the lightest
   available charged Furey excitation (electron) plus its neutral counterpart.

5. CKM mixing: quarks from different generations can absorb a W message
   because the W couples to all three Witt pair orientations (all three
   generations), with different amplitudes set by the overlap integrals
   of the Witt-pair states. The CKM matrix is the table of these overlaps.

6. Better names for the weak force:
   - Witt-pair rotation message
   - Ideal-channel swap
   - Flavor rewriter
   - Generation-shifting kick
   - Left-chirality phase disruptor

---

### The Electromagnetic Force

**Standard names:** electromagnetism, EM force, Coulomb force,
Lorentz force, Maxwell's equations

**COG names:** e7-phase messenger exchange, charge-sign kick, photon-mediated
sign interaction, Fano-orientation matching force, phase-winding interaction

**Kernel sentence:**
The electromagnetic force is the exchange of e7 vacuum phase pulses (photons)
between motifs with nonzero interaction handedness (charge) — the photon
deposits a phase kick proportional to the charge and inversely proportional
to the hop distance.

**Extended intuition:**

1. Like charges repel, opposite attract — from phase matching. A photon
   carries a definite phase orientation. When absorbed by a same-sign charge,
   the phase adds constructively to the repulsive component. When absorbed
   by opposite-sign charge, it adds constructively to the attractive component.
   The charge-sign matrix is the XOR-overlap between sender and receiver
   Witt states.

2. The 1/r² law: the photon message spreads outward from the source along
   all available causal edges. In a 3D graph, the number of edges at hop
   distance r grows as r². The message amplitude per edge therefore falls
   as 1/r², giving Coulomb's law. It is a counting argument about how
   edges spread in 3D, not a mysterious action at a distance.

3. Magnetic force: when a charged motif is drifting (has momentum), its
   outgoing photon messages carry a directional bias (the photon's Fano
   orientation is tilted by the drift). This directional bias creates a
   net force on other drifting charges that is perpendicular to both their
   velocities — the magnetic force.

4. The fine structure constant alpha ~ 1/137: the ratio of the EM coupling
   strength to the vacuum drive strength. In COG it should arise from a
   counting argument: the number of Fano-plane paths that support EM
   coupling divided by the total number of paths. RFC-061 is exploring
   this derivation.

---

### Gravity (Extended)

**Standard names:** gravity, general relativity, spacetime curvature,
gravitational waves, equivalence principle

**COG names:** computational drag field, causal graph curvature, tick-rate
differential, edge-density gradient, update-rate distortion, geodesic bending

**Extended intuition (additional):**

1. Equivalence principle: in COG, a uniformly accelerating subgraph (one
   where new nodes are being inserted preferentially on one side, giving a
   drift rate = acceleration) is locally indistinguishable from a subgraph
   sitting in a dense-node region (gravitational field). Both distort the
   local hop metric in the same way. The equivalence is exact in the
   discrete model.

2. Gravitational waves: oscillations in the edge-density of a region
   propagating outward at c = 1 hop/tick. When two black holes (dense
   cliques) merge, the resulting edge-density oscillation propagates as a
   wave through the causal graph, stretching and compressing hop-distances
   periodically. This is the COG description of gravitational radiation.

3. Black hole entropy (Bekenstein-Hawking): the entropy of a black hole
   scales with its surface area (number of boundary nodes), not its volume.
   In COG this is natural: the information content accessible to the outside
   is encoded in the boundary nodes (the interface between the inward-only
   interior and the exterior), not the interior nodes which are causally
   inaccessible.

---
