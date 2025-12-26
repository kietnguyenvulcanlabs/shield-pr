"""Confidence scoring for platform detection.

Combines multiple detection signals to compute final confidence score.
"""

from typing import Dict, Optional, Tuple


def calculate_confidence(
    ext_platform: Optional[str],
    ext_confidence: float,
    content_platform: Optional[str],
    content_confidence: float,
) -> Tuple[Optional[str], float, str]:
    """Calculate final platform and confidence from multiple signals.

    Args:
        ext_platform: Platform detected from extension
        ext_confidence: Confidence from extension detection
        content_platform: Platform detected from content
        content_confidence: Confidence from content detection

    Returns:
        Tuple of (final_platform, final_confidence, reasoning)
    """
    # No detection at all
    if not ext_platform and not content_platform:
        return (None, 0.0, "No platform detected from extension or content")

    # Only extension detected
    if ext_platform and not content_platform:
        reasoning = f"Detected from file extension: {ext_confidence:.2%} confidence"
        return (ext_platform, ext_confidence, reasoning)

    # Only content detected
    if content_platform and not ext_platform:
        reasoning = f"Detected from content analysis: {content_confidence:.2%} confidence"
        return (content_platform, content_confidence, reasoning)

    # Both detected - check if they agree
    if ext_platform == content_platform:
        # Agreement boosts confidence
        combined_confidence = min(ext_confidence + content_confidence * 0.3, 1.0)
        reasoning = (
            f"Extension and content agree: {combined_confidence:.2%} confidence"
        )
        return (ext_platform, combined_confidence, reasoning)

    # Disagreement - use higher confidence
    if ext_confidence > content_confidence:
        reasoning = (
            f"Extension ({ext_platform}: {ext_confidence:.2%}) "
            f"overrides content ({content_platform}: {content_confidence:.2%})"
        )
        return (ext_platform, ext_confidence, reasoning)
    else:
        reasoning = (
            f"Content ({content_platform}: {content_confidence:.2%}) "
            f"overrides extension ({ext_platform}: {ext_confidence:.2%})"
        )
        return (content_platform, content_confidence, reasoning)


def aggregate_scores(scores: Dict[str, float]) -> Tuple[Optional[str], float]:
    """Aggregate multiple platform scores into final result.

    Args:
        scores: Dictionary of platform → confidence scores

    Returns:
        Tuple of (platform, confidence) with highest score
    """
    if not scores:
        return (None, 0.0)

    platform = max(scores.items(), key=lambda x: x[1])
    return (platform[0], platform[1])


def should_use_llm_fallback(confidence: float, threshold: float = 0.5) -> bool:
    """Determine if LLM fallback should be used.

    Args:
        confidence: Detection confidence score
        threshold: Minimum confidence threshold

    Returns:
        True if confidence is below threshold and LLM should be used
    """
    return confidence < threshold
