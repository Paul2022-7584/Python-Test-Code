"""RetireLab: reproducible retirement scenario modeling in pure Python."""

from .engine import analyze, project
from .models import RetirementScenario

__all__ = ["RetirementScenario", "analyze", "project"]
__version__ = "1.0.0"
