"""AI/ML-specific prompt templates."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


AI_ML_PROMPTS = {
    "architecture": PromptTemplate(
        template="""You are an expert AI/ML code reviewer. Analyze the architecture and design patterns.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. Model architecture design (layers, activations, regularization)
2. Data pipeline organization (ETL, preprocessing, augmentation)
3. Training/inference separation
4. Model versioning and experiment tracking
5. Modular design (data, model, training, evaluation modules)

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "architecture",
      "file_path": "{file_path}",
      "line_number": <line_number or null>,
      "description": "<detailed description>",
      "suggestion": "<actionable suggestion>",
      "code_snippet": "<relevant code or null>"
    }}
  ]
}}

If no issues found, return: {{"findings": []}}
""",
        input_variables=["code", "file_path"],
        partial_variables={"severity_guide": SEVERITY_GUIDE},
    ),
    "platform_issues": PromptTemplate(
        template="""You are an expert AI/ML code reviewer. Analyze for AI/ML-specific issues.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
{architecture_result}

Focus Areas:
1. **Data Validation**: Input shape checks, data type validation, missing value handling
2. **Model Performance**: Overfitting, underfitting, gradient issues, convergence problems
3. **GPU/Memory**: Efficient GPU usage, batch size optimization, memory leaks
4. **Bias & Fairness**: Data bias, model fairness, ethical considerations
5. **Reproducibility**: Random seeds, deterministic operations, environment pinning

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "data-validation|model-performance|gpu-memory|bias-fairness|reproducibility",
      "file_path": "{file_path}",
      "line_number": <line_number or null>,
      "description": "<detailed description>",
      "suggestion": "<actionable suggestion>",
      "code_snippet": "<relevant code or null>"
    }}
  ]
}}

If no issues found, return: {{"findings": []}}
""",
        input_variables=["code", "file_path", "architecture_result"],
        partial_variables={"severity_guide": SEVERITY_GUIDE},
    ),
    "tests": PromptTemplate(
        template="""You are an expert AI/ML code reviewer. Analyze test coverage and quality.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}

Focus Areas:
1. **Unit Tests**: Data preprocessing, model components, utility functions
2. **Integration Tests**: End-to-end pipeline tests
3. **Model Validation**: Test metrics, performance benchmarks
4. **Edge Cases**: Empty data, extreme values, corrupted inputs
5. **Regression Tests**: Model performance regression detection

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "testing",
      "file_path": "{file_path}",
      "line_number": <line_number or null>,
      "description": "<detailed description>",
      "suggestion": "<actionable suggestion>",
      "code_snippet": "<relevant code or null>"
    }}
  ]
}}

If no issues found, return: {{"findings": []}}
""",
        input_variables=[
            "code",
            "file_path",
            "architecture_result",
            "platform_issues_result",
        ],
        partial_variables={"severity_guide": SEVERITY_GUIDE},
    ),
    "improvements": PromptTemplate(
        template="""You are an expert AI/ML code reviewer. Suggest improvements and best practices.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}
Tests: {tests_result}

Focus Areas:
1. **Performance**: Vectorization, batch processing, caching, mixed precision
2. **Code Quality**: Type hints, documentation, logging, error handling
3. **Modern Practices**: Latest framework features, pre-trained models, transfer learning
4. **Monitoring**: Experiment tracking (MLflow, W&B), metric logging
5. **Production Readiness**: Model serving, API design, scalability

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "performance|code-quality|modern-practices|monitoring|production",
      "file_path": "{file_path}",
      "line_number": <line_number or null>,
      "description": "<detailed description>",
      "suggestion": "<actionable suggestion>",
      "code_snippet": "<relevant code or null>"
    }}
  ]
}}

If no issues found, return: {{"findings": []}}
""",
        input_variables=[
            "code",
            "file_path",
            "architecture_result",
            "platform_issues_result",
            "tests_result",
        ],
        partial_variables={"severity_guide": SEVERITY_GUIDE},
    ),
}
