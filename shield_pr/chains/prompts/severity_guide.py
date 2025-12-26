"""Severity rating calibration guide for consistent findings."""

SEVERITY_GUIDE = """
## Severity Rating Guidelines

**HIGH**: Security risk, data loss, production outage, crash, type error
  Examples:
  - SQL injection vulnerability
  - Unhandled exception on critical path
  - Memory leak causing app crash
  - ANR (Application Not Responding)
  - Data exposure or privacy violation

**MEDIUM**: Performance degradation, maintainability issue, potential bug
  Examples:
  - N+1 query pattern
  - Unclear variable naming
  - Listener not released properly
  - Inefficient algorithm
  - Missing null checks
  - Deprecated API usage

**LOW**: Code style, documentation, optimization opportunity
  Examples:
  - Inconsistent code formatting
  - Missing documentation
  - Suboptimal but working code
  - Minor refactoring suggestions
  - TODO comments without context
"""
