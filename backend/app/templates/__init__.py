"""Template registry.

Maps template keys to their module-level objects so the agent and router
can work with any template by key alone.
"""

from __future__ import annotations

from app.templates import (
    comprehensive_exam,
    emergency_exam,
    recall_exam,
    soap_comprehensive,
    soap_emergency,
    soap_summarize,
    summarize,
)

_MODULES = {
    "comprehensive_exam": comprehensive_exam,
    "emergency_exam": emergency_exam,
    "recall_exam": recall_exam,
    "soap_comprehensive": soap_comprehensive,
    "soap_emergency": soap_emergency,
    "soap_summarize": soap_summarize,
    "summarize": summarize,
}

DEFAULT_TEMPLATE_KEY = "comprehensive_exam"

TEMPLATE_LIST = [
    {"key": key, "name": mod.TEMPLATE_NAME}
    for key, mod in _MODULES.items()
]


def get_template(key: str | None = None):
    """Return the template module for the given key (or the default)."""
    return _MODULES.get(key or DEFAULT_TEMPLATE_KEY, comprehensive_exam)
