"""Platform detection patterns and rules.

Defines file extensions, keywords, imports, and config files
that identify each supported platform.
"""

from typing import Dict, List

# Platform-specific detection patterns
PLATFORM_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "android": {
        "extensions": [".kt", ".java", ".xml"],
        "keywords": ["android", "androidx", "kotlin.android"],
        "imports": ["android.", "androidx.", "kotlinx.coroutines", "com.google.android"],
        "files": ["AndroidManifest.xml", "build.gradle", "gradle.properties"],
    },
    "ios": {
        "extensions": [".swift", ".m", ".h", ".mm"],
        "keywords": ["import UIKit", "import SwiftUI", "@objc", "@IBOutlet"],
        "imports": ["UIKit", "Foundation", "SwiftUI", "CoreData", "Combine"],
        "files": ["Podfile", "Package.swift", "Info.plist"],
    },
    "ai-ml": {
        "extensions": [".py", ".ipynb", ".pth", ".pkl"],
        "keywords": [
            "tensorflow",
            "pytorch",
            "sklearn",
            "numpy",
            "keras",
            "neural",
            "model",
            "dataset",
        ],
        "imports": [
            "tensorflow",
            "torch",
            "sklearn",
            "keras",
            "numpy",
            "pandas",
            "scipy",
            "transformers",
        ],
        "files": ["requirements.txt", "environment.yml", "model.py", "train.py"],
    },
    "frontend": {
        "extensions": [".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss"],
        "keywords": ["react", "vue", "angular", "component", "useState", "useEffect"],
        "imports": ["react", "vue", "@angular", "svelte", "next", "nuxt"],
        "files": ["package.json", "tsconfig.json", "vite.config", "webpack.config"],
    },
    "backend": {
        "extensions": [".py", ".go", ".rs", ".js", ".ts", ".rb", ".php"],
        "keywords": [
            "express",
            "fastapi",
            "gin",
            "actix",
            "flask",
            "django",
            "router",
            "endpoint",
        ],
        "imports": [
            "flask",
            "django",
            "fastapi",
            "express",
            "gin",
            "actix_web",
            "rails",
            "laravel",
        ],
        "files": ["Dockerfile", "docker-compose.yml", "requirements.txt", "go.mod"],
    },
}

# Confidence thresholds for detection methods
CONFIDENCE_THRESHOLDS = {
    "extension_high": 0.9,  # Unique extension (e.g., .kt, .swift)
    "extension_medium": 0.6,  # Shared extension but context helps
    "extension_low": 0.3,  # Ambiguous extension
    "content_high": 0.8,  # Strong content match
    "content_medium": 0.5,  # Moderate content match
    "content_low": 0.2,  # Weak content match
    "manual": 1.0,  # Manual selection via CLI flag
}

# Extension weights for multi-platform extensions
EXTENSION_WEIGHTS = {
    # Unique extensions (high confidence)
    ".kt": {"android": 1.0},
    ".swift": {"ios": 1.0},
    ".m": {"ios": 0.9},
    ".h": {"ios": 0.7},  # Can be C/C++
    ".tsx": {"frontend": 0.9},
    ".jsx": {"frontend": 0.9},
    ".vue": {"frontend": 1.0},
    ".svelte": {"frontend": 1.0},
    ".go": {"backend": 0.9},
    ".rs": {"backend": 0.9},
    ".ipynb": {"ai-ml": 0.95},
    # Ambiguous extensions (need content analysis)
    ".py": {"backend": 0.3, "ai-ml": 0.3},  # Requires content
    ".js": {"frontend": 0.4, "backend": 0.4},  # Requires content
    ".ts": {"frontend": 0.4, "backend": 0.4},  # Requires content
    ".java": {"android": 0.6, "backend": 0.3},  # More likely Android
    ".xml": {"android": 0.5},  # Could be config
}

# Keyword patterns for content analysis
KEYWORD_PATTERNS = {
    "android": r"\b(android|androidx|kotlin\.android)\b",
    "ios": r"\b(UIKit|SwiftUI|Foundation|NSObject|@objc)\b",
    "ai-ml": r"\b(tensorflow|pytorch|sklearn|keras|numpy|neural|dataset|model\.fit)\b",
    "frontend": r"\b(react|vue|angular|component|useState|createApp|@Component)\b",
    "backend": r"\b(express|fastapi|flask|django|router|endpoint|app\.get|app\.post)\b",
}

# Import patterns for content analysis
IMPORT_PATTERNS = {
    "android": r"^import\s+(android|androidx|kotlinx)\.",
    "ios": r"^import\s+(UIKit|SwiftUI|Foundation|Combine)",
    "ai-ml": r"^import\s+(tensorflow|torch|sklearn|keras|numpy|pandas|transformers)",
    "frontend": r"^import\s+.*\s+from\s+['\"]react|vue|@angular|svelte",
    "backend": r"^(from|import)\s+(flask|django|fastapi|express|gin)",
}


def get_platform_pattern(platform: str) -> Dict[str, List[str]]:
    """Get detection patterns for a specific platform.

    Args:
        platform: Platform name (android, ios, ai-ml, frontend, backend)

    Returns:
        Dictionary with extensions, keywords, imports, and files

    Raises:
        KeyError: If platform is not recognized
    """
    return PLATFORM_PATTERNS[platform]


def get_supported_platforms() -> List[str]:
    """Get list of all supported platforms.

    Returns:
        List of platform names
    """
    return list(PLATFORM_PATTERNS.keys())


def is_valid_platform(platform: str) -> bool:
    """Check if platform name is valid.

    Args:
        platform: Platform name to validate

    Returns:
        True if platform is supported
    """
    return platform in PLATFORM_PATTERNS
