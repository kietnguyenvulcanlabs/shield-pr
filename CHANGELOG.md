# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-26

### Added
- Initial release of Code Review Assistant CLI
- Platform-specific code review chains (Android, iOS, AI/ML, Frontend, Backend)
- Auto-detection of programming platforms from file patterns
- Multiple output formats (Markdown, JSON, GitHub, GitLab, Slack)
- Git integration (staged changes, branch diffs, PR reviews)
- Configuration via YAML file and environment variables
- Rich terminal output with syntax highlighting
- Intelligent caching for LLM responses
- File filtering (gitignore, size limits, binary detection)
- Pull request fetching from GitHub and GitLab APIs

### Commands
- `shield-pr review` - Review code files with AI analysis
- `shield-pr review-diff` - Review git staged changes
- `cra pr` - Review pull requests
- `shield-pr init` - Initialize configuration
- `shield-pr platforms` - List supported platforms
- `shield-pr version` - Show version information

### Configuration
- Support for Gemini API key configuration
- Configurable review depth (quick, standard, deep)
- Platform selection (auto-detect or manual)
- Output format selection

[Unreleased]: https://github.com/kietnguyenvulcanlabs/shield-pr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kietnguyenvulcanlabs/shield-pr/releases/tag/v0.1.0
