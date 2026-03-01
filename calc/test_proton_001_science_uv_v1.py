# Test script for checking e000 channel occupancy in proton stability simulation
import json
from fractions import Fraction

# Function to extract e000 channel occupancy from result
# Assuming result JSON will contain a key 'final_state_occupancy' mapped to channel counts
def extract_e000_occupancy(result_path):
    with open(result_path, 'r') as file:
        data = json.load(file)
        # Extract the channel state counts - assuming a specific structure exists
        final_counts = data['channel_counts']
        e000_occupancy = final_counts.get('e000', 0)
        total_count = sum(final_counts.values())
        return Fraction(e000_occupancy, total_count)


def test_proton_stability():
    result_path = 'cog_v2/python/experiments/proton_001_science_result_v1.json'
    occupancy_fraction = extract_e000_occupancy(result_path)
    assert occupancy_fraction == Fraction(0, 1), 'Proton stability test failed!'


if __name__ == '__main__':
    test_proton_stability()

# Signed-by: Evelyn Carter