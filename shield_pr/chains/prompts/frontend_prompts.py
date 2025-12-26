"""Frontend-specific prompt templates."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


FRONTEND_PROMPTS = {
    "architecture": PromptTemplate(
        template="""You are an expert Frontend code reviewer. Analyze the architecture and design patterns.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. Component architecture (container/presentational separation)
2. State management patterns (Redux, Zustand, Context API)
3. Routing structure and navigation
4. API integration and data fetching
5. Code organization and module structure

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
        template="""You are an expert Frontend code reviewer. Analyze for Frontend-specific issues.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
{architecture_result}

Focus Areas:
1. **React Hooks**: useEffect dependencies, custom hooks, hook rules compliance
2. **State Management**: Unnecessary re-renders, state lifting, prop drilling
3. **Performance**: useMemo/useCallback usage, lazy loading, code splitting
4. **Accessibility**: ARIA labels, keyboard navigation, semantic HTML
5. **Bundle Size**: Import optimization, tree shaking, heavy dependencies

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "hooks|state|performance|accessibility|bundle",
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
        template="""You are an expert Frontend code reviewer. Analyze test coverage and quality.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}

Focus Areas:
1. **Unit Tests**: Component logic, utility functions, hooks
2. **Integration Tests**: User flows, API integration
3. **Test Quality**: React Testing Library best practices, user-centric tests
4. **Coverage**: Edge cases, error scenarios, loading states
5. **E2E Tests**: Critical user journeys (Cypress, Playwright)

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
        template="""You are an expert Frontend code reviewer. Suggest improvements and best practices.

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
1. **Performance**: Image optimization, lazy loading, virtual scrolling
2. **Modern Practices**: Latest React features, TypeScript usage, ESNext syntax
3. **UX**: Loading states, error handling, responsive design
4. **Code Quality**: Type safety, naming conventions, documentation
5. **SEO**: Meta tags, structured data, SSR/SSG considerations

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "performance|modern-practices|ux|code-quality|seo",
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
