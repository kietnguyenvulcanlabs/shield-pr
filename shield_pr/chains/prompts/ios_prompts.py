"""iOS-specific prompt templates."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


IOS_PROMPTS = {
    "architecture": PromptTemplate(
        template="""You are an expert iOS code reviewer. Analyze the architecture and design patterns.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. MVVM/MVP/VIPER architecture patterns
2. Separation of concerns (UI, business logic, data)
3. Dependency injection (Swinject, manual DI)
4. Coordinators/Routers for navigation
5. Repository/Service layer patterns

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
        template="""You are an expert iOS code reviewer. Analyze for iOS-specific issues.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
{architecture_result}

Focus Areas:
1. **ARC Issues**: Retain cycles, strong reference cycles, memory leaks
2. **Memory Management**: Weak/unowned references, capture lists in closures
3. **Threading**: Main thread violations, GCD usage, @MainActor compliance
4. **SwiftUI**: State management, @State/@Binding/@ObservedObject usage
5. **UIKit**: View controller lifecycle, proper deallocation
6. **Concurrency**: async/await usage, Task management, actor isolation

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "arc|memory|threading|swiftui|uikit|concurrency",
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
        template="""You are an expert iOS code reviewer. Analyze test coverage and quality.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}

Focus Areas:
1. **Unit Tests**: XCTest for business logic, ViewModels
2. **UI Tests**: XCUITest for critical user flows
3. **Test Coverage**: Missing tests for edge cases, error scenarios
4. **Test Quality**: Proper assertions, test isolation, mocking
5. **Snapshot Tests**: UI regression testing

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
        template="""You are an expert iOS code reviewer. Suggest improvements and best practices.

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
1. **Performance**: LazyVStack optimization, image loading, memory efficiency
2. **Swift Best Practices**: Protocol-oriented programming, value types, optionals
3. **Modern iOS**: Latest Apple frameworks, SF Symbols, async/await
4. **Code Quality**: Naming conventions, code organization, documentation
5. **Accessibility**: VoiceOver, Dynamic Type, accessibility identifiers

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "performance|swift-practices|modern-ios|code-quality|accessibility",
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
