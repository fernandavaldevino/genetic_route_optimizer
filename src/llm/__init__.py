"""
Módulo de integração com LLMs para geração de instruções e relatórios especializados baseados em rotas otimizadas.
"""

from .providers import (
    BaseLLMProvider,
    OpenAIProvider,
    OllamaProvider,
    create_llm_provider,
    get_available_providers
)

from .generators import (
    ManualGenerator,
    ItineraryGenerator,
    QAGenerator,
    RouteGenerator,
    QASystem
)

__version__ = "1.0.0"

__all__ = [
    # Providers
    'BaseLLMProvider',
    'OpenAIProvider',
    'OllamaProvider',
    'create_llm_provider',
    'get_available_providers',
    # Generators
    'ManualGenerator',
    'ItineraryGenerator',
    'QAGenerator',
    'RouteGenerator',
    'QASystem'
]