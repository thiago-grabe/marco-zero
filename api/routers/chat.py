"""
Router /chat — SSE streaming do ChatAgent.

POST /chat
  body: { contract_id, message }
  response: text/event-stream

Eventos SSE:
  event: context     → dados do contrato injetados como contexto
  event: tool_call   → agente chamou uma ferramenta
  event: tool_result → resultado da ferramenta
  event: text        → chunk de texto da resposta
  event: done        → fim do stream
  event: error       → erro
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents import Runner
from agents.items import MessageOutputItem, ToolCallItem, ToolCallOutputItem
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent

from mz_agents.chat import create_chat_agent
from db.models.contract import Contract
from db.rls import get_rls_session
from middleware.auth import get_current_user_id

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    contract_id: str
    message: str
    mode: str = "massa"  # "massa" (tradutor) ou "nicho" (analista)


def _sse(event: str, data: dict | str) -> str:
    """Formata uma linha SSE."""
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("")
async def chat(
    body: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> StreamingResponse:
    # Buscar contrato
    result = await session.execute(
        select(Contract).where(
            Contract.id == uuid.UUID(body.contract_id),
            Contract.user_id == uuid.UUID(user_id),
        )
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # Montar contexto do contrato para o system prompt
    taxa_aa = round((1 + float(contract.taxa_mensal)) ** 12 - 1, 6)
    juros = round(float(contract.saldo_devedor) * float(contract.taxa_mensal), 2)
    seguros = round(float(contract.mip_mensal) + float(contract.dfi_mensal), 2)
    parcela = round(float(contract.amortizacao_mensal) + juros + seguros, 2)

    contract_context = (
        f"## Dados do contrato do usuário\n"
        f"- Banco: {contract.banco}\n"
        f"- Sistema: {contract.sistema_amortizacao}\n"
        f"- Taxa mensal: {float(contract.taxa_mensal)} ({taxa_aa * 100:.2f}% a.a.)\n"
        f"- Saldo devedor: R$ {float(contract.saldo_devedor):,.2f}\n"
        f"- Amortização mensal: R$ {float(contract.amortizacao_mensal):,.2f}\n"
        f"- Juros da próxima parcela: R$ {juros:,.2f}\n"
        f"- Seguros (MIP+DFI): R$ {seguros:,.2f}\n"
        f"- Parcela total estimada: R$ {parcela:,.2f}\n"
        f"- Próximo vencimento: {contract.data_proxima_parcela}\n"
        f"- Parcelas restantes: {contract.prazo_remanescente}\n"
    )

    # Incluir custos extras no contexto se existirem
    extras = contract.custos_extras or []
    if extras:
        extras_total = sum(e.get("valor", 0) if isinstance(e, dict) else 0 for e in extras)
        contract_context += f"\n## Custos extras mensais (cadastrados pelo usuário)\n"
        for e in extras:
            nome = e.get("nome", "?") if isinstance(e, dict) else "?"
            valor = e.get("valor", 0) if isinstance(e, dict) else 0
            contract_context += f"- {nome}: R$ {valor:,.2f}\n"
        contract_context += f"- **Total custos extras: R$ {extras_total:,.2f}/mês**\n"
        contract_context += (
            f"\nIMPORTANTE: considere esses custos extras em TODA análise e recomendação. "
            f"Eles impactam o comprometimento mensal real do usuário.\n"
        )

    contract_context += f"\nUse estes valores como parâmetros ao chamar as ferramentas."

    agent = create_chat_agent(mode=body.mode)

    # Mensagens: contexto do contrato + pergunta do usuário
    messages = [
        {"role": "user", "content": f"[CONTEXTO DO CONTRATO — não repita isso ao usuário]\n\n{contract_context}"},
        {"role": "assistant", "content": "Entendido. Tenho os dados do contrato. Como posso ajudar?"},
        {"role": "user", "content": body.message},
    ]

    async def stream():
        # Enviar contexto como primeiro evento
        yield _sse("context", {
            "banco": contract.banco,
            "saldo_devedor": float(contract.saldo_devedor),
            "parcela_total": parcela,
            "prazo_remanescente": contract.prazo_remanescente,
        })

        try:
            stream_result = Runner.run_streamed(agent, input=messages)
            # Track whether we're inside a tool call to suppress argument deltas
            in_tool_call = False

            async for event in stream_result.stream_events():
                if isinstance(event, RunItemStreamEvent):
                    item = event.item

                    if isinstance(item, ToolCallItem):
                        in_tool_call = True
                        yield _sse("tool_call", {
                            "tool": item.raw_item.name if hasattr(item.raw_item, 'name') else str(item.type),
                            "arguments": item.raw_item.arguments if hasattr(item.raw_item, 'arguments') else "",
                        })

                    elif isinstance(item, ToolCallOutputItem):
                        in_tool_call = False
                        yield _sse("tool_result", {
                            "output": item.output if isinstance(item.output, str) else str(item.output),
                        })

                    elif isinstance(item, MessageOutputItem):
                        in_tool_call = False
                        text = ""
                        if hasattr(item, "raw_item") and hasattr(item.raw_item, "content"):
                            for block in item.raw_item.content:
                                if hasattr(block, "text"):
                                    text += block.text
                        if text:
                            yield _sse("text", {"content": text})

                elif isinstance(event, RawResponsesStreamEvent):
                    # Only emit text deltas when NOT inside a tool call.
                    # Tool call arguments arrive as deltas too — suppress them all.
                    if in_tool_call:
                        continue
                    data = event.data
                    if hasattr(data, "type") and data.type == "output_text_delta":
                        delta = getattr(data, "delta", "")
                        if delta:
                            yield _sse("text_delta", {"delta": delta})

            yield _sse("done", {"status": "ok"})

        except Exception as e:
            yield _sse("error", {"detail": str(e)})

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
