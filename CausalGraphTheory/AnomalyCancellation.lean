import Mathlib.Data.Fin.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

namespace AnomalyCancellation

open Finset BigOperators

def cogCharges : Fin 7 -> Int :=
  ![1, 1, 1, -1, -1, -1, 0]

theorem linear_anomaly_cancels :
    Finset.univ.sum cogCharges = 0 := by native_decide

theorem cubic_anomaly_cancels :
    Finset.univ.sum (fun i => cogCharges i ^ 3) = 0 := by native_decide

theorem anomaly_free :
    Finset.univ.sum cogCharges = 0 /\
    Finset.univ.sum (fun i => cogCharges i ^ 3) = 0 :=
  And.intro linear_anomaly_cancels cubic_anomaly_cancels

end AnomalyCancellation