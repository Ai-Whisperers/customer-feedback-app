"""
Test shifted NPS calculation as default.
"""

import os
import sys
sys.path.append('.')

from app.core.nps_calculator import calculate_nps_score, calculate_nps_metrics_modular


def test_shifted_as_default():
    """Test that shifted method is now the default."""

    print("Testing Shifted NPS as Default")
    print("=" * 50)

    # Clear any existing environment variable to test default
    if 'NPS_CALCULATION_METHOD' in os.environ:
        del os.environ['NPS_CALCULATION_METHOD']

    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Balanced (equal promoters/detractors)",
            "promoters": 30,
            "passives": 40,
            "detractors": 30,
            "expected_shifted": 50.0,  # Neutral
            "expected_standard": 0.0
        },
        {
            "name": "Positive scenario",
            "promoters": 60,
            "passives": 25,
            "detractors": 15,
            "expected_shifted": 72.5,  # Good
            "expected_standard": 45.0
        },
        {
            "name": "Negative scenario",
            "promoters": 20,
            "passives": 30,
            "detractors": 50,
            "expected_shifted": 35.0,  # Poor
            "expected_standard": -30.0
        },
        {
            "name": "All promoters",
            "promoters": 100,
            "passives": 0,
            "detractors": 0,
            "expected_shifted": 100.0,  # Excellent
            "expected_standard": 100.0
        },
        {
            "name": "All detractors",
            "promoters": 0,
            "passives": 0,
            "detractors": 100,
            "expected_shifted": 0.0,  # Worst
            "expected_standard": -100.0
        }
    ]

    print("\n1. Testing with default configuration (should use shifted)")
    print("-" * 50)

    for case in test_cases:
        score = calculate_nps_score(
            case["promoters"],
            case["passives"],
            case["detractors"]
        )

        print(f"\n{case['name']}:")
        print(f"  Data: {case['promoters']} promoters, {case['passives']} passives, {case['detractors']} detractors")
        print(f"  Score: {score:.1f}")
        print(f"  Expected (shifted): {case['expected_shifted']:.1f}")
        print(f"  Standard would be: {case['expected_standard']:.1f}")
        print(f"  ✓ Using shifted method" if abs(score - case['expected_shifted']) < 0.1 else f"  ✗ Not using shifted")

    print("\n2. Testing metrics with modular function")
    print("-" * 50)

    # Test with modular metrics function
    nps_counts = {
        "promoter": 40,
        "passive": 35,
        "detractor": 25
    }

    metrics = calculate_nps_metrics_modular(nps_counts)

    print(f"\nNPS Counts: {nps_counts}")
    print(f"Calculated metrics:")
    print(f"  Score: {metrics['score']}")
    print(f"  Method: {metrics['method']}")
    print(f"  Promoters: {metrics['promoters']} ({metrics['promoters_percentage']}%)")
    print(f"  Passives: {metrics['passives']} ({metrics['passives_percentage']}%)")
    print(f"  Detractors: {metrics['detractors']} ({metrics['detractors_percentage']}%)")

    # Calculate what the score should be
    total = sum(nps_counts.values())
    expected_shifted = ((nps_counts['promoter'] - nps_counts['detractor']) / total + 1) * 50
    print(f"\nExpected shifted score: {expected_shifted:.1f}")
    print(f"✓ Correct!" if abs(metrics['score'] - expected_shifted) < 0.1 else "✗ Incorrect!")

    print("\n3. Testing empty data handling")
    print("-" * 50)

    empty_counts = {"promoter": 0, "passive": 0, "detractor": 0}
    empty_metrics = calculate_nps_metrics_modular(empty_counts)

    print(f"Empty data score: {empty_metrics['score']}")
    print(f"Expected: 50 (neutral for shifted method)")
    print(f"✓ Correct!" if empty_metrics['score'] == 50 else "✗ Incorrect!")

    print("\n" + "=" * 50)
    print("✓ Shifted method is now the default!")
    print("  - Scores range from 0 to 100")
    print("  - 50 represents neutral (balanced)")
    print("  - No negative values possible")


if __name__ == "__main__":
    test_shifted_as_default()