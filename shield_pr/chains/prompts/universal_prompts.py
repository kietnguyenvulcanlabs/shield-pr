"""Universal quality prompts for cross-platform review."""

from langchain.prompts import PromptTemplate  # type: ignore
from shield_pr.chains.prompts.severity_guide import SEVERITY_GUIDE


UNIVERSAL_PROMPTS = {
    "security": PromptTemplate(
        template="""You are an expert security code reviewer. Analyze for security vulnerabilities.

File: {file_path}
Code:
```
{code}
```

Focus Areas (OWASP Top 10):
1. **Injection**: SQL, NoSQL, command injection, LDAP injection
2. **Authentication**: Weak passwords, session management, credential storage
3. **Sensitive Data**: Exposed secrets, API keys, PII leakage
4. **XXE**: XML external entity attacks
5. **Access Control**: Missing authorization, insecure direct object references
6. **Security Misconfiguration**: Default configs, verbose errors
7. **XSS**: Cross-site scripting vulnerabilities
8. **Deserialization**: Insecure deserialization
9. **Known Vulnerabilities**: Outdated dependencies, CVEs
10. **Logging**: Insufficient logging, sensitive data in logs

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "security",
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
    "readability": PromptTemplate(
        template="""You are an expert code reviewer. Analyze code readability and maintainability.

File: {file_path}
Code:
```
{code}
```

Focus Areas:
1. **Naming**: Clear variable/function names, avoid abbreviations
2. **Complexity**: Cyclomatic complexity, nested conditionals
3. **Documentation**: Docstrings, comments explaining WHY not WHAT
4. **Code Organization**: Logical grouping, single responsibility
5. **Magic Numbers**: Unexplained constants, hardcoded values

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "readability",
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
    "best_practices": PromptTemplate(
        template="""You are an expert code reviewer. Analyze adherence to best practices.

File: {file_path}
Code:
```
{code}
```

Previous Analysis:
Security: {security_result}
Readability: {readability_result}

Focus Areas:
1. **DRY**: Code duplication, repeated logic
2. **SOLID**: Single responsibility, open/closed, Liskov, interface segregation, dependency inversion
3. **Error Handling**: Try-catch blocks, error propagation, graceful degradation
4. **Resource Management**: File handles, connections, memory cleanup
5. **Code Smells**: Long methods, large classes, feature envy

{severity_guide}

Provide structured JSON output:
{{
  "findings": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "category": "best-practices",
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
        input_variables=["code", "file_path", "security_result", "readability_result"],
        partial_variables={"severity_guide": SEVERITY_GUIDE},
    ),
}
