"""
CodeCoR: An LLM-Based Self-Reflective Multi-Agent Framework for Code Generation.

Paper: https://arxiv.org/abs/2501.07811
Authors: Ruwei Pan, Hongyu Zhang, Chao Liu (Chongqing University)
"""

from codecor.framework import CodeCoR, CodeCoRConfig
from codecor.llm import LLMClient

__version__ = "1.0.0"
__all__ = ["CodeCoR", "CodeCoRConfig", "LLMClient"]
