"""Android-specific prompt templates."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


ANDROID_PROMPTS = {
    "architecture": PromptTemplate(
        template="""You are an expert Android code reviewer. Analyze the architecture and design patterns.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. MVVM/MVI/MVP architecture patterns
2. Separation of concerns (UI, business logic, data)
3. Dependency injection usage (Hilt, Dagger, Koin)
4. ViewModels and lifecycle-aware components
5. Repository pattern implementation

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
        template="""You are an expert Android code reviewer. Analyze for Android-specific issues.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
{architecture_result}

Focus Areas:
1. **Lifecycle Issues**: Activity/Fragment lifecycle violations, improper state management
2. **Memory Leaks**: Context references in listeners, static references, inner classes
3. **ANR Risks**: Network calls on main thread, heavy operations without coroutines/AsyncTask
4. **Permission Handling**: Runtime vs manifest permissions, permission checks
5. **Jetpack Compose**: Remember state issues, recomposition problems, side effects
6. **Threading**: Main thread violations, improper coroutine usage

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "lifecycle|memory-leak|anr|permissions|compose|threading",
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
        template="""You are an expert Android code reviewer. Analyze test coverage and quality.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}

Focus Areas:
1. **Unit Tests**: JUnit tests for business logic, ViewModels
2. **UI Tests**: Espresso/Compose UI tests for critical flows
3. **Test Coverage**: Missing tests for edge cases, error scenarios
4. **Test Quality**: Proper assertions, test isolation, mocking strategy
5. **Integration Tests**: API integration, database tests

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
        template="""You are an expert Android code reviewer. Suggest improvements and best practices.

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
1. **Performance**: LazyColumn optimization, bitmap handling, memory efficiency
2. **Code Quality**: Kotlin best practices, extension functions, sealed classes
3. **Modern Android**: Jetpack libraries, Material Design 3, latest APIs
4. **Maintainability**: Code readability, naming conventions, documentation
5. **Accessibility**: ContentDescription, TalkBack support, contrast ratios

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "performance|code-quality|modern-android|maintainability|accessibility",
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
