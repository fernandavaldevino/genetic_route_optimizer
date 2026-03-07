"""
Templates de prompts para geração de conteúdo
"""

from .manual_templates import (
    MANUAL_SYSTEM_MESSAGE,
    MANUAL_GENERATION_TEMPLATE,
    format_route_for_manual
)

from .route_templates import (
    ROUTE_SYSTEM_MESSAGE,
    ROUTE_GENERATION_TEMPLATE,
    format_points_for_route
)

from .qa_templates import (
    QA_SYSTEM_MESSAGE,
    QA_CONTEXT_TEMPLATE,
    COMMON_QUESTIONS,
    format_route_context
)

__all__ = [
    'MANUAL_SYSTEM_MESSAGE',
    'MANUAL_GENERATION_TEMPLATE',
    'format_route_for_manual',
    'ROUTE_SYSTEM_MESSAGE',
    'ROUTE_GENERATION_TEMPLATE',
    'format_points_for_route',
    'QA_SYSTEM_MESSAGE',
    'QA_CONTEXT_TEMPLATE',
    'COMMON_QUESTIONS',
    'format_route_context'
]