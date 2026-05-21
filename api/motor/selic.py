"""
Selic — consulta a taxa Selic meta vigente no Banco Central do Brasil.

Fonte: API pública do BCB (série 432), sem autenticação.
Cache em memória por 24h para não sobrecarregar a API.
"""

from __future__ import annotations

import time
import httpx

BCB_SELIC_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"

# Cache em memória: (valor, timestamp)
_cache: dict[str, tuple[float, float]] = {}
CACHE_TTL = 86400  # 24 horas


async def get_selic_anual() -> float:
    """
    Retorna a taxa Selic meta anual vigente (ex: 14.50 para 14,50% a.a.).
    Cacheia o resultado por 24h.
    Fallback: 14.25% se a API estiver indisponível.
    """
    now = time.time()
    cached = _cache.get("selic")
    if cached and (now - cached[1]) < CACHE_TTL:
        return cached[0]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(BCB_SELIC_URL)
            resp.raise_for_status()
            data = resp.json()
            valor = float(data[0]["valor"])
            _cache["selic"] = (valor, now)
            return valor
    except Exception:
        # Fallback conservador se BCB estiver fora
        return _cache.get("selic", (14.25, 0))[0]


async def get_selic_mensal() -> float:
    """Retorna a Selic convertida para taxa mensal equivalente."""
    anual = await get_selic_anual()
    return (1 + anual / 100) ** (1 / 12) - 1


def taxa_range_from_selic(selic_anual: float) -> tuple[float, float]:
    """
    Retorna o range razoável de taxa mensal de financiamento imobiliário
    dado a Selic vigente.

    Financiamentos imobiliários no Brasil tipicamente têm:
    - Piso: Selic - 3pp (Minha Casa subsidiado)
    - Teto: Selic + 4pp (financiamento caro, carteira hipotecária)

    Retorna: (taxa_mensal_min, taxa_mensal_max) em decimal.
    """
    piso_aa = max(5.0, selic_anual - 3.0)
    teto_aa = selic_anual + 4.0

    piso_mensal = (1 + piso_aa / 100) ** (1 / 12) - 1
    teto_mensal = (1 + teto_aa / 100) ** (1 / 12) - 1

    return (round(piso_mensal, 6), round(teto_mensal, 6))
