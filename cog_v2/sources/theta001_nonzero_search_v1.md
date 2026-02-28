# THETA-001 Nonzero Search (v1)

- Claim: `THETA-001`
- Replay hash: `c033a0f96a29b4a699b374122260d881371a40d3aa827f9dcd56880d54ffa874`
- RNG seed: `20260228`
- Samples: `512`
- Op depth: `36`

## Summary
- weak_squared_all_zero: `True`
- ckm_squared_all_zero: `True`
- weak_nonzero_excluding_t0_count: `505` (0.986)
- ckm_nonzero_excluding_t0_count: `507` (0.990)
- weak_max_abs_excluding_t0: `2250`
- ckm_max_abs_excluding_t0: `2740`

## Top Weak Nonzero Cases (excluding t0)
- sample=166, weak_kick=11, res=2250, sq=0
- sample=59, weak_kick=-7, res=1728, sq=0
- sample=298, weak_kick=11, res=-1670, sq=0
- sample=95, weak_kick=11, res=1666, sq=0
- sample=251, weak_kick=11, res=-1566, sq=0
- sample=423, weak_kick=11, res=1476, sq=0
- sample=220, weak_kick=-9, res=-1344, sq=0
- sample=204, weak_kick=-11, res=1296, sq=0
- sample=152, weak_kick=9, res=1264, sq=0
- sample=234, weak_kick=5, res=1236, sq=0

## Top CKM Nonzero Cases (excluding t0)
- sample=185, weak_kick=11, phase=7, period=3, res=2740, sq=0
- sample=40, weak_kick=7, phase=5, period=2, res=2198, sq=0
- sample=251, weak_kick=11, phase=-1, period=2, res=1932, sq=0
- sample=340, weak_kick=9, phase=-1, period=5, res=1896, sq=0
- sample=373, weak_kick=9, phase=7, period=5, res=1692, sq=0
- sample=206, weak_kick=11, phase=1, period=2, res=-1564, sq=0
- sample=107, weak_kick=-9, phase=1, period=2, res=1530, sq=0
- sample=178, weak_kick=9, phase=1, period=6, res=-1374, sq=0
- sample=396, weak_kick=11, phase=-3, period=3, res=-1284, sq=0
- sample=122, weak_kick=-7, phase=5, period=5, res=1222, sq=0

## Limits
- Search lane is exploratory and does not alter THETA-001 claim status.
- Observable here is oriented_fano_cubic_cp_odd_v1, not the currently promoted squared residual lane.
- Promotion impact requires preregistration and independent skeptical review.
