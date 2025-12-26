"""Platform-specific review chain destinations.

Provides stub implementations for platform-specific review chains.
These will be implemented in Phase 3.
"""

from typing import Dict

from langchain.chains import LLMChain  # type: ignore[import-not-found]
from langchain.prompts import PromptTemplate  # type: ignore[import-not-found]

from ..core.llm_client import LLMClient


def create_android_chain(llm_client: LLMClient) -> LLMChain:
    """Create Android-specific review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for Android code review
    """
    template = """You are an expert Android developer reviewing Kotlin/Java code.

Code to review:
{code}

Provide a code review focusing on:
- Android-specific best practices
- Kotlin coroutines and lifecycle management
- Material Design compliance
- Performance and memory optimization

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def create_ios_chain(llm_client: LLMClient) -> LLMChain:
    """Create iOS-specific review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for iOS code review
    """
    template = """You are an expert iOS developer reviewing Swift/Objective-C code.

Code to review:
{code}

Provide a code review focusing on:
- Swift best practices and modern patterns
- SwiftUI vs UIKit considerations
- Memory management (ARC)
- iOS Human Interface Guidelines

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def create_ai_ml_chain(llm_client: LLMClient) -> LLMChain:
    """Create AI/ML-specific review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for AI/ML code review
    """
    template = """You are an expert ML engineer reviewing AI/ML code.

Code to review:
{code}

Provide a code review focusing on:
- Model architecture and design
- Training efficiency and data pipelines
- TensorFlow/PyTorch best practices
- Reproducibility and experiment tracking

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def create_frontend_chain(llm_client: LLMClient) -> LLMChain:
    """Create frontend-specific review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for frontend code review
    """
    template = """You are an expert frontend developer reviewing React/Vue/Angular code.

Code to review:
{code}

Provide a code review focusing on:
- Component design and reusability
- State management patterns
- Performance optimization (memoization, lazy loading)
- Accessibility and UX best practices

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def create_backend_chain(llm_client: LLMClient) -> LLMChain:
    """Create backend-specific review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for backend code review
    """
    template = """You are an expert backend developer reviewing server-side code.

Code to review:
{code}

Provide a code review focusing on:
- API design and RESTful practices
- Database query optimization
- Security (SQL injection, auth, validation)
- Error handling and logging

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def create_default_chain(llm_client: LLMClient) -> LLMChain:
    """Create default generic review chain.

    Args:
        llm_client: LLM client instance

    Returns:
        LangChain chain for generic code review
    """
    template = """You are an expert software engineer reviewing code.

Code to review:
{code}

Provide a comprehensive code review focusing on:
- Code quality and maintainability
- Best practices and design patterns
- Security vulnerabilities
- Performance considerations

Review:"""

    prompt = PromptTemplate(input_variables=["code"], template=template)
    return LLMChain(llm=llm_client.llm, prompt=prompt)


def get_platform_chains(llm_client: LLMClient) -> Dict[str, LLMChain]:
    """Get all platform-specific review chains.

    Args:
        llm_client: LLM client instance

    Returns:
        Dictionary mapping platform names to review chains
    """
    return {
        "android": create_android_chain(llm_client),
        "ios": create_ios_chain(llm_client),
        "ai-ml": create_ai_ml_chain(llm_client),
        "frontend": create_frontend_chain(llm_client),
        "backend": create_backend_chain(llm_client),
        "default": create_default_chain(llm_client),
    }
