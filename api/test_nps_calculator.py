"""
Test script for NPS calculator module with different configurations.
"""

import os
import sys
sys.path.append('.')

from app.core.nps_calculator import calculate_nps_score, NPSMethod


def test_nps_methods():
    """Test different NPS calculation methods."""

    # Test data: 30 promoters, 20 passives, 50 detractors
    promoters = 30
    passives = 20
    detractors = 50

    print("Testing NPS Calculation Methods")
    print("=" * 50)
    print(f"Sample Data: {promoters} promoters, {passives} passives, {detractors} detractors")
    print("-" * 50)

    # Test standard method (can be negative)
    score_standard = calculate_nps_score(promoters, passives, detractors, NPSMethod.STANDARD.value)
    print(f"Standard Method: {score_standard:.1f}")
    print(f"  Formula: (promoters - detractors) / total * 100")
    print(f"  Result: ({promoters} - {detractors}) / 100 * 100 = {score_standard:.1f}")
    print()

    # Test absolute method (always positive)
    score_absolute = calculate_nps_score(promoters, passives, detractors, NPSMethod.ABSOLUTE.value)
    print(f"Absolute Method: {score_absolute:.1f}")
    print(f"  Formula: abs((promoters - detractors) / total * 100)")
    print(f"  Result: abs(({promoters} - {detractors}) / 100 * 100) = {score_absolute:.1f}")
    print()

    # Test weighted method (includes passives)
    os.environ["NPS_PASSIVE_WEIGHT"] = "0.5"
    score_weighted = calculate_nps_score(promoters, passives, detractors, NPSMethod.WEIGHTED.value)
    print(f"Weighted Method (passive weight=0.5): {score_weighted:.1f}")
    print(f"  Formula: (promoters - detractors + passives * weight) / total * 100")
    print(f"  Result: ({promoters} - {detractors} + {passives} * 0.5) / 100 * 100 = {score_weighted:.1f}")
    print()

    # Test shifted method (0-100 scale)
    score_shifted = calculate_nps_score(promoters, passives, detractors, NPSMethod.SHIFTED.value)
    print(f"Shifted Method: {score_shifted:.1f}")
    print(f"  Formula: ((promoters - detractors) / total + 1) * 50")
    print(f"  Result: (({promoters} - {detractors}) / 100 + 1) * 50 = {score_shifted:.1f}")
    print()

    print("=" * 50)
    print("\nPositive Scenario Test")
    print("-" * 50)

    # Test with more promoters
    promoters = 60
    passives = 25
    detractors = 15

    print(f"Sample Data: {promoters} promoters, {passives} passives, {detractors} detractors")
    print("-" * 50)

    for method in [NPSMethod.STANDARD, NPSMethod.ABSOLUTE, NPSMethod.WEIGHTED, NPSMethod.SHIFTED]:
        score = calculate_nps_score(promoters, passives, detractors, method.value)
        print(f"{method.value.capitalize()} Method: {score:.1f}")

    print("\n" + "=" * 50)
    print("Environment Variable Test")
    print("-" * 50)

    # Test with environment variable
    os.environ["NPS_CALCULATION_METHOD"] = NPSMethod.ABSOLUTE.value
    score_env = calculate_nps_score(30, 20, 50)  # No method specified, uses env
    print(f"Using NPS_CALCULATION_METHOD=absolute: {score_env:.1f}")

    os.environ["NPS_CALCULATION_METHOD"] = NPSMethod.SHIFTED.value
    score_env = calculate_nps_score(30, 20, 50)  # No method specified, uses env
    print(f"Using NPS_CALCULATION_METHOD=shifted: {score_env:.1f}")


if __name__ == "__main__":
    test_nps_methods()