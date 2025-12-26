"""Backend-specific prompt templates."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


BACKEND_PROMPTS = {
    "architecture": PromptTemplate(
        template="""You are an expert Backend code reviewer. Analyze the architecture and design patterns.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. Layered architecture (controller/service/repository)
2. Dependency injection and inversion of control
3. API design (RESTful, GraphQL) and versioning
4. Database access patterns and ORM usage
5. Microservices patterns (if applicable)

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
        template="""You are an expert Backend code reviewer. Analyze for Backend-specific issues.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
{architecture_result}

Focus Areas:
1. **Security**: SQL injection, XSS, CSRF, authentication/authorization
2. **Database**: N+1 queries, missing indexes, connection pooling
3. **Error Handling**: Exception handling, logging, error responses
4. **Rate Limiting**: API throttling, DDoS protection
5. **Concurrency**: Thread safety, race conditions, deadlocks

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "security|database|error-handling|rate-limiting|concurrency",
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
        template="""You are an expert Backend code reviewer. Analyze test coverage and quality.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Architecture: {architecture_result}
Platform Issues: {platform_issues_result}

Focus Areas:
1. **Unit Tests**: Service layer, business logic, utility functions
2. **Integration Tests**: API endpoints, database operations
3. **Test Coverage**: Edge cases, error scenarios, validation
4. **Test Quality**: Mocking strategy, test isolation, fixtures
5. **Load Tests**: Performance testing, stress testing

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
        template="""You are an expert Backend code reviewer. Suggest improvements and best practices.

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
1. **Performance**: Caching, query optimization, async processing
2. **Scalability**: Horizontal scaling, stateless design, distributed systems
3. **Monitoring**: Logging, metrics, tracing, health checks
4. **Code Quality**: Type hints, documentation, SOLID principles
5. **API Design**: RESTful best practices, pagination, filtering

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "performance|scalability|monitoring|code-quality|api-design",
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
