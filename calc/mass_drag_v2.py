"""
Gate-Density Simulation (Gate 2) — RFC-009 §7b.10
MU-001: Proton-to-electron mass ratio via non-associative gate counting.

State: (oct_idx, sign) where oct_idx in 0..6 (Fano imaginary units e1..e7)
and sign in {+1, -1}.

Proton motif: 3 quarks Q0, Q1, Q2 in strictly cyclic exchange schedule.
  Tick 1: Q0 emits to Q1  (u1 -> u2)
  Tick 2: Q1 emits to Q2  (u2 -> d1)
  Tick 3: Q2 emits to Q0  (d1 -> u1)
  Repeat.
  Quarks initialized with distinct Fano colors: e1(0), e2(1), e4(3).
  These form a non-associative triad (NOT on the same Fano line).

Electron motif: 3 components c0, c1, c2 in same cyclic schedule.
  Initial states: e1(0), e2(1), e3(2) — associative quaternion triad.
  Expected gate density: 0 (since {e1,e2,e3} lies in quaternion subalgebra H c O).

Gate = non-associative bracket mismatch:
  gate fires if (S*G)*W != S*(G*W)
  where S=emitter, G=gluon, W=witness (third quark).
"""

import sys
import pathlib
import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent))

# ---- Inline Fano tables (same as conftest.py) --------------------------------
# rfc/CONVENTIONS.md §2: 0-indexed Fano lines
FANO_CYCLES = [
    (0, 1, 2),  # e1*e2=+e3
    (0, 3, 4),  # e1*e4=+e5
    (0, 6, 5),  # e1*e7=+e6  (note: reversed from naive order)
    (1, 3, 5),  # e2*e4=+e6
    (1, 4, 6),  # e2*e5=+e7
    (2, 3, 6),  # e3*e4=+e7
    (2, 5, 4),  # e3*e6=+e5
]

FANO_SIGN: dict = {}
FANO_THIRD: dict = {}

for _a, _b, _c in FANO_CYCLES:
    # Cyclic positive:   a*b=+c,  b*c=+a,  c*a=+b
    FANO_SIGN[(_a, _b)] = +1;  FANO_THIRD[(_a, _b)] = _c
    FANO_SIGN[(_b, _c)] = +1;  FANO_THIRD[(_b, _c)] = _a
    FANO_SIGN[(_c, _a)] = +1;  FANO_THIRD[(_c, _a)] = _b
    # Anti-cyclic negative:  b*a=-c,  c*b=-a,  a*c=-b
    FANO_SIGN[(_b, _a)] = -1;  FANO_THIRD[(_b, _a)] = _c
    FANO_SIGN[(_c, _b)] = -1;  FANO_THIRD[(_c, _b)] = _a
    FANO_SIGN[(_a, _c)] = -1;  FANO_THIRD[(_a, _c)] = _b


def oct_mul(a_idx, a_sign, b_idx, b_sign):
    """Multiply two octonion imaginary units with signs.
    Returns (result_idx, result_sign).
    Special case: ei*ei = -1, encoded as (idx=-1, sign=-combined_sign).
    If indices not on a common Fano line, returns (-1, 0).
    """
    combined_sign = a_sign * b_sign
    if a_idx == b_idx:
        return (-1, -combined_sign)
    key = (a_idx, b_idx)
    if key in FANO_SIGN:
        return (FANO_THIRD[key], combined_sign * FANO_SIGN[key])
    # Not on same Fano line
    return (-1, 0)


def bracket_left(s_idx, s_sign, g_idx, g_sign, t_idx, t_sign):
    """Compute (S * G) * T"""
    sg_idx, sg_sign = oct_mul(s_idx, s_sign, g_idx, g_sign)
    if sg_idx == -1:
        # S*G = scalar: scalar * T = sign * T
        return (t_idx, sg_sign * t_sign)
    return oct_mul(sg_idx, sg_sign, t_idx, t_sign)


def bracket_right(s_idx, s_sign, g_idx, g_sign, t_idx, t_sign):
    """Compute S * (G * T)"""
    gt_idx, gt_sign = oct_mul(g_idx, g_sign, t_idx, t_sign)
    if gt_idx == -1:
        # G*T = scalar: S * scalar = sign * S
        return (s_idx, gt_sign * s_sign)
    return oct_mul(s_idx, s_sign, gt_idx, gt_sign)


def is_gate(s_idx, s_sign, g_idx, g_sign, t_idx, t_sign):
    """Returns True if (S*G)*T != S*(G*T) — non-associative gate fires."""
    lhs = bracket_left(s_idx, s_sign, g_idx, g_sign, t_idx, t_sign)
    rhs = bracket_right(s_idx, s_sign, g_idx, g_sign, t_idx, t_sign)
    return lhs != rhs


def gluon(source_idx, target_idx):
    """The gluon = third Fano point on the line through source and target.
    Witt-pair triality rule (rfc/CONVENTIONS.md §5.2):
    If quark transitions from color A to color B, gluon is the third point C.
    Falls back to (source_idx, +1) if no shared Fano line.
    """
    key = (source_idx, target_idx)
    if key in FANO_THIRD:
        return (FANO_THIRD[key], FANO_SIGN[key])
    # Not on same Fano line — no valid gluon
    return (source_idx, +1)


def run_proton(N: int) -> int:
    """Run proton motif (uud: e1=idx0, e2=idx1, e4=idx3 — non-associative triad) for N ticks.
    Returns total non-associative gate count.
    """
    proton_states = [(0, +1), (1, +1), (3, +1)]
    gates, _ = run_simulation(proton_states, N, "PROTON motif [u1=e1(0), u2=e2(1), d1=e4(3)]")
    return gates


def run_electron(N: int) -> int:
    """Run electron motif (e1=idx0, e2=idx1, e3=idx2 — associative quaternion triad) for N ticks.
    Returns total non-associative gate count (expected 0).
    """
    electron_states = [(0, +1), (1, +1), (2, +1)]
    gates, _ = run_simulation(
        electron_states, N, "ELECTRON motif [c1=e1(0), c2=e2(1), c3=e3(2)]"
    )
    return gates


def run_simulation(states, N, label):
    """
    Run N ticks of the cyclic exchange simulation.
    states: list of 3 (idx, sign) tuples
    Returns (total_nonassoc_gates, gate_density)
    """
    particles = list(states)
    total_gates = 0

    for tick in range(N):
        # Cyclic schedule: tick%3 -> (tick+1)%3, witness is (tick+2)%3
        emitter_i = tick % 3
        target_i = (tick + 1) % 3
        witness_i = (tick + 2) % 3

        s_idx, s_sign = particles[emitter_i]
        t_idx, t_sign = particles[target_i]
        w_idx, w_sign = particles[witness_i]

        # Compute gluon from source to target (Witt-pair rule)
        g_idx, g_sign = gluon(s_idx, t_idx)

        # Check non-associativity: (S*G)*W vs S*(G*W)
        if is_gate(s_idx, s_sign, g_idx, g_sign, w_idx, w_sign):
            total_gates += 1

        # Update target state: t' = g * t
        new_t_idx, new_t_sign = oct_mul(g_idx, g_sign, t_idx, t_sign)
        if new_t_idx == -1:
            # g*t = scalar, keep index but flip sign
            particles[target_i] = (t_idx, new_t_sign * t_sign if new_t_sign != 0 else t_sign)
        else:
            particles[target_i] = (new_t_idx, new_t_sign)

    gate_density = total_gates / N
    print(f"\n[{label}]")
    print(f"  Steps:                    {N}")
    print(f"  Total non-assoc gates:    {total_gates}")
    print(f"  Gate density:             {gate_density:.6f}")
    return total_gates, gate_density


def append_yaml_record(record):
    """Append a simulation record to claims/proton_electron_ratio.yml
    using pure string manipulation to avoid reformatting the whole file."""
    claims_path = pathlib.Path(__file__).parent.parent / "claims" / "proton_electron_ratio.yml"

    if not claims_path.exists():
        print(f"WARNING: {claims_path} not found; skipping persistence.")
        return

    # Read existing content
    content = claims_path.read_text(encoding="utf-8")

    # Build the new YAML block to append
    ratio_str = (
        f'"{record["ratio"]}"' if isinstance(record["ratio"], str)
        else str(record["ratio"])
    )
    block = f"""
simulation_records:
  - date: "{record['date']}"
    method: "{record['method']}"
    steps: {record['steps']}
    proton_nonassoc_gates: {record['proton_nonassoc_gates']}
    proton_density: {record['proton_density']}
    electron_nonassoc_gates: {record['electron_nonassoc_gates']}
    electron_density: {record['electron_density']}
    ratio: {ratio_str}
    note: "{record['note']}"
"""

    # Check if simulation_records section already exists
    if "simulation_records:" in content:
        # Find the last entry and append after it
        # We'll just append a new list item
        new_item = f"""  - date: "{record['date']}"
    method: "{record['method']}"
    steps: {record['steps']}
    proton_nonassoc_gates: {record['proton_nonassoc_gates']}
    proton_density: {record['proton_density']}
    electron_nonassoc_gates: {record['electron_nonassoc_gates']}
    electron_density: {record['electron_density']}
    ratio: {ratio_str}
    note: "{record['note']}"
"""
        # Append to end of file
        with open(claims_path, "a", encoding="utf-8") as f:
            f.write(new_item)
    else:
        # Append new section at end
        with open(claims_path, "a", encoding="utf-8") as f:
            f.write(block)

    print(f"\nRecord appended to: {claims_path}")


def main():
    N = 10000

    print("=" * 60)
    print("MU-001 Gate-Density Simulation (Gate 2) — RFC-009 §7b.10")
    print("=" * 60)

    # --- Proton motif ---
    # u1=e1(idx=0), u2=e2(idx=1), d1=e4(idx=3)
    # e1 and e4 are NOT on the same Fano line as e2, giving non-associative interactions
    proton_states = [(0, +1), (1, +1), (3, +1)]

    # --- Electron motif ---
    # c1=e1(idx=0), c2=e2(idx=1), c3=e3(idx=2)
    # {e1,e2,e3} on Fano line (0,1,2) => associative quaternion subalgebra H subset O
    electron_states = [(0, +1), (1, +1), (2, +1)]

    p_gates, p_density = run_simulation(
        proton_states, N,
        "PROTON motif [u1=e1(0), u2=e2(1), d1=e4(3)]"
    )
    e_gates, e_density = run_simulation(
        electron_states, N,
        "ELECTRON motif [c1=e1(0), c2=e2(1), c3=e3(2)]"
    )

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Proton  gate density:  {p_density:.6f}  ({p_gates}/{N} gates)")
    print(f"  Electron gate density: {e_density:.6f}  ({e_gates}/{N} gates)")

    if e_density == 0.0:
        print("\nRESULT: DEGENERATE (Electron is associative)")
        print("  Electron gate density = 0 confirms {e1,e2,e3} c H (quaternion subalgebra)")
        print("  Proton/electron ratio is undefined (infinity) — degenerate denominator")
        ratio_value = "infinity"
        note = ("Electron motif lies in associative quaternion subalgebra H subset O. "
                "Gate density = 0. Ratio proton/electron = infinity (degenerate per RFC-009 §7b.10).")
    else:
        ratio_value = round(p_density / e_density, 6)
        note = f"Ratio = proton_density / electron_density = {ratio_value}"
        print(f"\n  Ratio (proton/electron): {ratio_value}")

    print("=" * 60)

    # Persist record
    record = {
        "date": datetime.date.today().isoformat(),
        "method": "gate_density_v2",
        "steps": N,
        "proton_nonassoc_gates": p_gates,
        "proton_density": round(p_density, 6),
        "electron_nonassoc_gates": e_gates,
        "electron_density": round(e_density, 6),
        "ratio": ratio_value,
        "note": note,
    }

    append_yaml_record(record)
    print(f"Record: {record}")

    return 0


if __name__ == "__main__":
    sys.exit(main())