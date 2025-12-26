"""Unit tests for confidence scoring.

Tests confidence calculation, score aggregation, and LLM fallback decisions.
"""

import pytest

from shield_pr.detection.confidence import (
    aggregate_scores,
    calculate_confidence,
    should_use_llm_fallback,
)


class TestCalculateConfidence:
    """Test confidence calculation from multiple signals."""

    def test_no_detection(self):
        """Should return None when no platform detected."""
        platform, confidence, reasoning = calculate_confidence(None, 0.0, None, 0.0)
        assert platform is None
        assert confidence == 0.0
        assert "No platform detected" in reasoning

    def test_extension_only(self):
        """Should use extension when only extension detected."""
        platform, confidence, reasoning = calculate_confidence(
            "android", 0.9, None, 0.0
        )
        assert platform == "android"
        assert confidence == 0.9
        assert "file extension" in reasoning

    def test_content_only(self):
        """Should use content when only content detected."""
        platform, confidence, reasoning = calculate_confidence(
            None, 0.0, "frontend", 0.7
        )
        assert platform == "frontend"
        assert confidence == 0.7
        assert "content analysis" in reasoning

    def test_agreement_boosts_confidence(self):
        """Should boost confidence when extension and content agree."""
        platform, confidence, reasoning = calculate_confidence(
            "android", 0.8, "android", 0.6
        )
        assert platform == "android"
        assert confidence > 0.8  # Boosted
        assert confidence <= 1.0  # Capped
        assert "agree" in reasoning

    def test_disagreement_higher_extension(self):
        """Should prefer extension when it has higher confidence."""
        platform, confidence, reasoning = calculate_confidence(
            "android", 0.9, "backend", 0.5
        )
        assert platform == "android"
        assert confidence == 0.9
        assert "overrides" in reasoning

    def test_disagreement_higher_content(self):
        """Should prefer content when it has higher confidence."""
        platform, confidence, reasoning = calculate_confidence(
            "backend", 0.3, "ai-ml", 0.8
        )
        assert platform == "ai-ml"
        assert confidence == 0.8
        assert "overrides" in reasoning

    def test_confidence_capped_at_one(self):
        """Should cap combined confidence at 1.0."""
        platform, confidence, reasoning = calculate_confidence(
            "ios", 0.95, "ios", 0.9
        )
        assert confidence <= 1.0

    def test_equal_confidence_prefers_content(self):
        """Should prefer content when confidences are equal."""
        platform, confidence, reasoning = calculate_confidence(
            "frontend", 0.5, "backend", 0.5
        )
        assert platform == "backend"


class TestAggregateScores:
    """Test score aggregation from multiple platforms."""

    def test_empty_scores(self):
        """Should return None for empty scores."""
        platform, confidence = aggregate_scores({})
        assert platform is None
        assert confidence == 0.0

    def test_single_platform(self):
        """Should return single platform score."""
        scores = {"android": 0.85}
        platform, confidence = aggregate_scores(scores)
        assert platform == "android"
        assert confidence == 0.85

    def test_multiple_platforms_highest_wins(self):
        """Should return platform with highest score."""
        scores = {"android": 0.6, "backend": 0.8, "frontend": 0.4}
        platform, confidence = aggregate_scores(scores)
        assert platform == "backend"
        assert confidence == 0.8

    def test_tie_returns_one_platform(self):
        """Should return one platform when scores tie."""
        scores = {"android": 0.7, "ios": 0.7}
        platform, confidence = aggregate_scores(scores)
        assert platform in ["android", "ios"]
        assert confidence == 0.7


class TestShouldUseLLMFallback:
    """Test LLM fallback decision logic."""

    def test_low_confidence_triggers_fallback(self):
        """Should use LLM when confidence below threshold."""
        assert should_use_llm_fallback(0.3, threshold=0.5) is True
        assert should_use_llm_fallback(0.4, threshold=0.5) is True

    def test_high_confidence_skips_fallback(self):
        """Should not use LLM when confidence above threshold."""
        assert should_use_llm_fallback(0.6, threshold=0.5) is False
        assert should_use_llm_fallback(0.9, threshold=0.5) is False

    def test_exact_threshold_skips_fallback(self):
        """Should not use LLM when confidence equals threshold."""
        assert should_use_llm_fallback(0.5, threshold=0.5) is False

    def test_zero_confidence_triggers_fallback(self):
        """Should use LLM when confidence is zero."""
        assert should_use_llm_fallback(0.0, threshold=0.5) is True

    def test_perfect_confidence_skips_fallback(self):
        """Should not use LLM when confidence is 1.0."""
        assert should_use_llm_fallback(1.0, threshold=0.5) is False

    def test_custom_threshold(self):
        """Should respect custom threshold values."""
        assert should_use_llm_fallback(0.6, threshold=0.7) is True
        assert should_use_llm_fallback(0.6, threshold=0.5) is False

    def test_high_threshold(self):
        """Should work with high thresholds."""
        assert should_use_llm_fallback(0.85, threshold=0.9) is True
        assert should_use_llm_fallback(0.95, threshold=0.9) is False


class TestConfidenceEdgeCases:
    """Test edge cases in confidence calculation."""

    def test_very_low_scores(self):
        """Should handle very low confidence scores."""
        platform, confidence, reasoning = calculate_confidence(
            "android", 0.01, "backend", 0.02
        )
        assert platform == "backend"
        assert confidence == 0.02

    def test_perfect_scores(self):
        """Should handle perfect confidence scores."""
        platform, confidence, reasoning = calculate_confidence(
            "ios", 1.0, "ios", 1.0
        )
        assert platform == "ios"
        assert confidence == 1.0

    def test_negative_zero(self):
        """Should handle negative zero properly."""
        platform, confidence, reasoning = calculate_confidence(
            "android", -0.0, None, 0.0
        )
        # -0.0 equals 0.0, so extension has no confidence
        assert platform is None or confidence == 0.0
