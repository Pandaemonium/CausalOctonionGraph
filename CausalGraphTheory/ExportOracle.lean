import CausalGraphTheory.Fano
import CausalGraphTheory.FanoMul
import CausalGraphTheory.Octonion
import CausalGraphTheory.WittBasis
import Lean.Data.Json

open Lean Json

def fanoCycleToJson (l : FanoLine) : Json :=
  Json.arr #[num (fanoCycles l 0).val, num (fanoCycles l 1).val, num (fanoCycles l 2).val]

def complexOctonionToJson {R} [CommRing R] [ToString R] (x : ComplexOctonion R) : Json :=
  -- Just export as list of pairs [re, im] for each component
  let coeffs := (List.finRange 8).map fun i =>
    let c := x.c i
    Json.arr #[str (toString c.re), str (toString c.im)]
  Json.arr (List.toArray coeffs)

def main : IO Unit := do
  let cycles := (List.finRange 7).map fun l => fanoCycleToJson l
  
  -- Export Fano Cycles
  let fanoJson := Json.mkObj [("cycles", Json.arr (List.toArray cycles))]

  -- Export Witt Basis (doubled)
  -- We use integer coefficients for exactness
  let witt0 := WittBasis.wittLowerDoubled (R := Int) 0
  let witt0_dag := WittBasis.wittRaiseDoubled (R := Int) 0
  
  let wittJson := Json.mkObj [
    ("alpha0", complexOctonionToJson witt0),
    ("alpha0_dag", complexOctonionToJson witt0_dag)
  ]

  let finalJson := Json.mkObj [
    ("fano", fanoJson),
    ("witt", wittJson)
  ]
  
  IO.FS.writeFile "calc/lean_outputs.json" (finalJson.pretty)
  IO.println "Exported calc/lean_outputs.json"
