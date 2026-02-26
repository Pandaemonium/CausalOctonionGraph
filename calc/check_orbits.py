import itertools

# Fano plane lines
lines = [
    {1,2,3}, # L0 (L1 in task)
    {1,4,5}, # L1
    {1,7,6}, # L2
    {2,4,6}, # L3
    {2,5,7}, # L4
    {3,4,7}, # L5
    {3,5,6}  # L6
]
# Convert to sorted tuples for hashing
line_tuples = [tuple(sorted(list(l))) for l in lines]
L1 = line_tuples[0] # (1,2,3)
others = set(line_tuples[1:])

# Find Aut(Fano)
# Permutations of 1..7
points = [1,2,3,4,5,6,7]
automorphisms = []

for p in itertools.permutations(points):
    # Check if this permutation maps lines to lines
    # Map each line
    mapped_lines = []
    is_auto = True
    for l in line_tuples:
        mapped = tuple(sorted([p[x-1] for x in l]))
        if mapped not in line_tuples:
            is_auto = False
            break
        mapped_lines.append(mapped)
    
    if is_auto:
        automorphisms.append((p, mapped_lines))

print(f"Total automorphisms: {len(automorphisms)}")

# Find Stab(L1)
stab_L1 = []
for p, mapped in automorphisms:
    # Check if L1 maps to L1
    # L1 is lines[0]
    l1_mapped = tuple(sorted([p[x-1] for x in L1]))
    if l1_mapped == L1:
        stab_L1.append((p, mapped))

print(f"Size of Stab(L1): {len(stab_L1)}")

# Compute orbits of remaining lines under Stab(L1)
# Remaining lines: indices 1..6
# We act on the *set* of remaining lines
# But we want the orbits of the lines themselves
# i.e. which lines can be mapped to which?

orbits = []
visited = set()

# lines[1] is (1,4,5) (L2)
remaining_indices = [1,2,3,4,5,6]

for i in remaining_indices:
    l_start = line_tuples[i]
    if l_start in visited:
        continue
    
    orbit = {l_start}
    # Apply all g in Stab(L1)
    for p, mapped in stab_L1:
        # Find where l_start maps to
        # l_start is the i-th line in the original list? No.
        # mapped is a list of lines in the same order? No.
        # We need to apply p to l_start directly
        l_mapped = tuple(sorted([p[x-1] for x in l_start]))
        orbit.add(l_mapped)
    
    print(f"Orbit containing L{i+1}: {orbit}")
    visited.update(orbit)
    orbits.append(orbit)

print(f"Number of orbits: {len(orbits)}")