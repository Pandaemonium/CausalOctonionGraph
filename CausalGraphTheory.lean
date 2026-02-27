-- This module serves as the root of the `CausalGraphTheory` library.
-- Import modules here that should be built as part of the library.
import CausalGraphTheory.Basic

-- Phase 1: Algebraic foundations
import CausalGraphTheory.Algebra
import CausalGraphTheory.Fano
import CausalGraphTheory.FanoMul
import CausalGraphTheory.Octonion
import CausalGraphTheory.OctonionAlt
import CausalGraphTheory.OctonionNonAssoc
import CausalGraphTheory.ComplexOctonion
import CausalGraphTheory.WittBasis
import CausalGraphTheory.WittPairSymmetry
import CausalGraphTheory.VacuumStabilizerAction
import CausalGraphTheory.VacuumStabilizerQuotient
import CausalGraphTheory.VacuumStabilizerStructure
import CausalGraphTheory.VacuumStabilizerS4
import CausalGraphTheory.KoideGroupBridge
import CausalGraphTheory.SubalgebraDetect
import CausalGraphTheory.Spinors
import CausalGraphTheory.FureyChain
import CausalGraphTheory.GenerationSeparation
import CausalGraphTheory.PhotonMasslessness

-- Phase 1.5: Constants and gauge foundations
import CausalGraphTheory.Constants
import CausalGraphTheory.PhaseClock
import CausalGraphTheory.GaugeGroup
import CausalGraphTheory.GaugeObservables
import CausalGraphTheory.WeakMixingObservable
import CausalGraphTheory.Koide

-- Phase 2: Graph structure (V1 causal DAG, legacy path; non-canonical for active physics claims)
import CausalGraphTheory.State
import CausalGraphTheory.Tick
import CausalGraphTheory.Update
import CausalGraphTheory.RaceCondition
import CausalGraphTheory.CausalOrder
import CausalGraphTheory.DAGProof

-- Phase 3: Kernel v2 and locked update rule (RFC-028)
import CausalGraphTheory.KernelV2
import CausalGraphTheory.UpdateRule
import CausalGraphTheory.XorGate

-- Phase 4: Derived physical quantities
import CausalGraphTheory.Mass
import CausalGraphTheory.Distance
import CausalGraphTheory.Vacuum

-- Phase 5: Interaction semantics (e-e interaction, RFC-028 scoped)
import CausalGraphTheory.TwoNodeSystem

-- ExportOracle defines its own `main`; built as a standalone executable
-- via [[lean_exe]] in lakefile.toml — not imported into the library root.
