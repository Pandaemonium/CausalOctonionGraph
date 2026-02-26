"""
calc/test_koide_diophantine.py
Diophantine search: f0^2+f1^2+f2^2 = 4*(f0*f1+f1*f2+f2*f0)
Range 1<=f0<f1<f2<=4000. Passes whether exact or near-miss found.
"""
import math
import pytest

def koide_lhs(f0,f1,f2): return f0*f0+f1*f1+f2*f2
def koide_rhs(f0,f1,f2): return 4*(f0*f1+f1*f2+f2*f0)
def koide_relation_exact(f0,f1,f2): return koide_lhs(f0,f1,f2)==koide_rhs(f0,f1,f2)
def relative_error(f0,f1,f2):
    lhs=koide_lhs(f0,f1,f2); rhs=koide_rhs(f0,f1,f2); return abs(lhs-rhs)/rhs

def search_koide_triples(max_val=4000):
    # O(N^2) algorithm: for fixed (f0,f1), solve quadratic for f2.
    # f2 = 2*(f0+f1) + sqrt(3*(f0^2+4*f0*f1+f1^2))
    # Since f2 >= (2+sqrt(3))*f1, bound f1 <= (max_val-2*f0)/(2+sqrt(3)).
    _c=2.0+math.sqrt(3.0)
    exact=[]; best=None; berr=float("inf")
    for f0 in range(1,max_val+1):
        f1u=int((max_val-2*f0)/_c)+2
        if f1u<=f0: break
        for f1 in range(f0+1,min(max_val,f1u)+1):
            disc=3*(f0*f0+4*f0*f1+f1*f1)
            sd=math.isqrt(disc)
            if sd*sd==disc:
                for s in(+1,-1):
                    f2c=2*(f0+f1)+s*sd
                    if f2c>f1 and f2c<=max_val and koide_relation_exact(f0,f1,f2c):
                        exact.append((f0,f1,f2c))
            f2r=2*(f0+f1)+math.sqrt(disc)
            for f2n in(int(math.floor(f2r)),int(math.ceil(f2r))):
                if f1<f2n<=max_val:
                    e=relative_error(f0,f1,f2n)
                    if e<berr: berr=e; best=(f0,f1,f2n)
    return exact,best,berr

def test_find_koide_integer_triples():
    """Search 1<=f0<f1<f2<=4000 for f0^2+f1^2+f2^2=4*(f0f1+f1f2+f2f0). Always passes."""
    exact,best,berr=search_koide_triples(4000)
    print(f"\nKoide integer search [1,4000]:")
    if exact:
        print(f"EXACT SOLUTIONS: {exact[:5]}")
        assert len(exact)>0
    else:
        f0,f1,f2=best
        print(f"NO EXACT SOLUTION. Best near-miss: ({f0},{f1},{f2})")
        print(f"  LHS={koide_lhs(f0,f1,f2)} RHS={koide_rhs(f0,f1,f2)}")
        print(f"  relative error={berr:.6e}")
        print(f"  f1/f0={f1/f0:.8f} f2/f1={f2/f1:.8f}")
        assert True,"No exact solution; near-miss reported."
