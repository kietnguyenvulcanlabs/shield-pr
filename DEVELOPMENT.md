# Local Development Guide

## Quick Test

Run the test script to verify everything works:

```bash
./test-local.sh
```

## Setting Up API Key

### Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### Set API Key

```bash
# Temporary (current session)
export CRA_API_KEY='your-api-key'

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export CRA_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

## Running Reviews

### Basic Review

```bash
# Review single file
poetry run shield-pr review test-samples/sample_backend.py

# Review with platform specified
poetry run shield-pr review --platform backend test-samples/sample_backend.py

# Review with depth
poetry run shield-pr review --depth deep test-samples/sample_backend.py
```

### Output Formats

```bash
# Markdown (default)
poetry run shield-pr review test-samples/sample_backend.py

# JSON
poetry run shield-pr review --format json test-samples/sample_backend.py

# GitHub format
poetry run shield-pr review --format github test-samples/sample_backend.py

# Save to file
poetry run shield-pr review --format json --output report.json test-samples/sample_backend.py
```

### Git Integration

```bash
# Review staged changes
poetry run shield-pr review-diff

# Compare to branch
poetry run shield-pr review-diff --branch main

# Review PR (requires GitHub token for URLs)
poetry run shield-pr pr --branch main
```

## Current Limitations

The review chains currently use mock data. For actual AI reviews:

1. **LLM Integration**: Chains are placeholders that return mock results
2. **API Calls**: No actual Gemini API calls are made yet
3. **Prompt Templates**: Templates exist but aren't sent to LLM

To enable real AI reviews, you would need to:

1. Implement the LangChain chain execution in `shield_pr/chains/`
2. Configure actual Gemini API calls in `cra/core/llm_client.py`
3. Parse LLM responses with the result parsers

## Development Workflow

### Type Checking

```bash
poetry run mypy shield_pr/
```

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test
poetry run pytest tests/unit/test_config_loader.py -v

# With coverage
poetry run pytest --cov=shield_pr --cov-report=html
```

### Code Formatting

```bash
# Format code
poetry run black shield_pr/ tests/

# Check formatting
poetry run black --check cra/ tests/

# Sort imports
poetry run ruff check --select I --fix cra/
```

### Building Package

```bash
# Build wheel and sdist
poetry build

# Check output
ls -lh dist/
```

## Sample Files

Test samples are provided in `test-samples/`:

- `sample_backend.py` - Python Flask API with SQL injection risk
- `sample_frontend.tsx` - React component with TypeScript
- `SampleAndroid.kt` - Kotlin code with hardcoded API key

## Configuration File

Create `~/.config/shield-pr/config.yaml`:

```yaml
api:
  api_key: your-gemini-api-key
  model: gemini-1.5-pro
  temperature: 0.35
  max_tokens: 2048

review:
  depth: standard
  platforms: []
  focus_areas:
    - security
    - performance
    - maintainability

output:
  format: markdown
```

## Debugging

Enable debug mode:

```bash
# Set debug flag
poetry run shield-pr --debug review test-samples/sample_backend.py
```

## Next Steps

Once ready for production:

1. Implement actual LangChain chain execution
2. Test with real Gemini API
3. Publish to PyPI
4. Create GitHub release
5. Distribute via conda-forge, Docker, Homebrew
