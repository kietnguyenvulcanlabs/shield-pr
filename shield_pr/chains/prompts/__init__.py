"""Prompt templates for review chains."""

from shield_pr.chains.prompts.android_prompts import ANDROID_PROMPTS
from shield_pr.chains.prompts.ios_prompts import IOS_PROMPTS
from shield_pr.chains.prompts.ai_ml_prompts import AI_ML_PROMPTS
from shield_pr.chains.prompts.frontend_prompts import FRONTEND_PROMPTS
from shield_pr.chains.prompts.backend_prompts import BACKEND_PROMPTS
from shield_pr.chains.prompts.universal_prompts import UNIVERSAL_PROMPTS
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE

__all__ = [
    "ANDROID_PROMPTS",
    "IOS_PROMPTS",
    "AI_ML_PROMPTS",
    "FRONTEND_PROMPTS",
    "BACKEND_PROMPTS",
    "UNIVERSAL_PROMPTS",
    "SEVERITY_GUIDE",
]
