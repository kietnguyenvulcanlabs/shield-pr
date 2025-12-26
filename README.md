# ShieldPR

> AI-powered code review CLI tool using LangChain and Google Gemini API

[![PyPI](https://img.shields.io/pypi/v/shield-pr)](https://pypi.org/project/shield-pr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🤖 **AI-Powered Analysis** - Uses Google Gemini 1.5 Pro for intelligent code reviews
- 🎯 **Platform-Specific** - Specialized chains for Android, iOS, AI/ML, Frontend, Backend
- 🔄 **Git Integration** - Review staged changes, branch diffs, and pull requests
- 📊 **Multiple Formats** - Output as Markdown, JSON, GitHub, GitLab, or Slack
- ⚡ **Intelligent Caching** - Fast reviews with smart prompt caching
- 🔒 **Secure** - API key masking, no data storage
- 📝 **Flexible Depth** - Quick, standard, or deep review modes

## Installation

### pip (Recommended)
```bash
pip install shield-pr
```

### conda-forge
```bash
conda install -c conda-forge shield-pr
```

### Docker
```bash
docker pull ghcr.io/kietnguyenvulcanlabs/shield-pr:latest
```

### Homebrew (macOS)
```bash
brew tap kietnguyenvulcanlabs/tap
brew install shield-pr
```

### pipx (Isolated)
```bash
pipx install shield-pr
```

[→ Full Installation Guide](docs/installation.md)

## Quick Start

1. **Get Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Set API Key**:
```bash
export CRA_API_KEY='your-gemini-api-key'
```

3. **Review Code**:
```bash
shield-pr review src/app.py
```

## Usage

### Basic Review

```bash
# Review single file
shield-pr review app.py

# Review directory
shield-pr review src/

# Review with platform
shield-pr review --platform android app/src/**/*.kt

# Deep review with JSON output
shield-pr review --depth deep --format json api/*.py
```

### Git Integration

```bash
# Review staged changes
shield-pr review-diff

# Compare to branch
shield-pr review-diff --branch main

# Review PR by URL
shield-pr pr --url https://github.com/org/repo/pull/123

# Compare branches locally
shield-pr pr --branch main
```

### Output Formats

```bash
# Markdown (default)
shield-pr review src/

# JSON for automation
shield-pr review --format json src/ > report.json

# GitHub format for PR comments
shield-pr review --format github src/

# GitLab format for MR comments
shield-pr review --format gitlab src/

# Slack message format
shield-pr review --format slack src/
```

## Configuration

Create `~/.config/shield-pr/config.yaml`:

```yaml
api:
  api_key: your-gemini-api-key
  model: gemini-1.5-pro
  temperature: 0.35
  max_tokens: 2048

review:
  depth: standard
  platforms: []  # auto-detect
  focus_areas:
    - security
    - performance
    - maintainability

output:
  format: markdown
```

Or use environment variables:
```bash
export CRA_API_KEY='your-api-key'
export CRA_MODEL='gemini-1.5-pro'
export CRA_TEMPERATURE='0.35'
export CRA_MAX_TOKENS='2048'
```

## Supported Platforms

| Platform | Languages | Detection |
|----------|-----------|-----------|
| **Android** | Kotlin, Java | `*.kt`, `*.java`, `AndroidManifest.xml` |
| **iOS** | Swift, Objective-C | `*.swift`, `*.m`, `Info.plist` |
| **AI/ML** | Python | TensorFlow, PyTorch, scikit-learn imports |
| **Frontend** | React, Vue, Angular | `*.jsx`, `*.tsx`, `*.vue`, `package.json` |
| **Backend** | Python, Node.js, Go | Flask, Django, Express, FastAPI |

[→ Platform Details](docs/platforms.md)

## CLI Commands

| Command | Description |
|---------|-------------|
| `shield-pr review` | Review code files |
| `shield-pr review-diff` | Review git staged changes |
| `cra pr` | Review pull requests |
| `cra init` | Initialize configuration |
| `cra platforms` | List supported platforms |
| `cra version` | Show version info |

## Docker Usage

```bash
# Pull image
docker pull ghcr.io/kietnguyenvulcanlabs/shield-pr:latest

# Review current directory
docker run --rm -v $(pwd):/workspace \
  -e CRA_API_KEY=$CRA_API_KEY \
  ghcr.io/kietnguyenvulcanlabs/shield-pr:latest review .

# Using docker-compose
docker-compose run review
```

[→ Docker Guide](docs/docker.md)

## Development

```bash
# Clone repository
git clone https://github.com/kietnguyenvulcanlabs/shield-pr.git
cd shield-pr

# Install with dev dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Type checking
poetry run mypy shield_pr/

# Format code
poetry run black shield_pr/ tests/
```

[→ Contributing Guide](docs/contributing.md)

## Documentation

- [Installation Guide](docs/installation.md) - All installation methods
- [Usage Guide](docs/usage.md) - Command reference and examples
- [Platform Support](docs/platforms.md) - Platform-specific details
- [Docker Guide](docs/docker.md) - Container usage
- [Contributing](docs/contributing.md) - Development setup

## License

MIT © 2025 Kiet Nguyen

---

**Made with ❤️ by [Kiet Nguyen](https://github.com/kietnguyenvulcanlabs)**

**ShieldPR** - The code review assistant for professional developers.
