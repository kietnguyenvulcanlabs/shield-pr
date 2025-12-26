"""
Default ignore patterns for file filtering.
"""

# Default ignore patterns
default_ignore_patterns = [
    # Build artifacts
    'dist/',
    'build/',
    'out/',
    '*.egg-info/',
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',

    # Dependency directories
    'node_modules/',
    'vendor/',
    '.venv/',
    'venv/',
    '.virtualenv/',

    # Generated files
    '*.lock',
    '*.min.js',
    '*.min.css',
    '*.bundle.js',
    '*.snapshot.tsx',

    # Lock files
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    'Poetry.lock',

    # IDE
    '.idea/',
    '.vscode/',
    '*.swp',
    '*.swo',
    '*~',

    # OS
    '.DS_Store',
    'Thumbs.db',
]
