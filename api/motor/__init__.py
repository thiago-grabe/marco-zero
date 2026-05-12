"""
Motor de cálculo Tenor — SAC / PRICE / Itaú

Funções puras, sem I/O, sem side effects.
Testáveis unitariamente com pytest.
"""

from .itau import detect_itau_mode
from .sac import (
    add_months,
    compare_scenarios,
    compute_installment,
    compute_pro_rata,
    project_scenario,
    simulate_amortization,
)

__all__ = [
    "add_months",
    "compare_scenarios",
    "compute_installment",
    "compute_pro_rata",
    "detect_itau_mode",
    "project_scenario",
    "simulate_amortization",
]
