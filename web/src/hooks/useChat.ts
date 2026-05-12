/**
 * useChat — SSE streaming hook for Tenor chat.
 *
 * Handles all 6 SSE event types from the backend:
 *   context, tool_call, tool_result, text, text_delta, done, error
 *
 * Uses useRef for assistantText to avoid closure race condition.
 * FIFO queue matches tool_result to the first pending tool_call.
 */

import { useCallback, useRef, useState } from "react";
import { getToken } from "@/lib/auth";
import type {
  ChatContext,
  ChatMessage,
  MessagePart,
  ToolCallPart,
  ToolName,
} from "@/components/chat/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [context, setContext] = useState<ChatContext | null>(null);
  const assistantTextRef = useRef("");
  const partsRef = useRef<MessagePart[]>([]);
  const pendingToolsRef = useRef<string[]>([]); // FIFO queue of tool names
  const abortRef = useRef<AbortController | null>(null);

  const updateAssistantMessage = useCallback(() => {
    setMessages((prev) => {
      const next = [...prev];
      const lastIdx = next.length - 1;
      if (lastIdx >= 0 && next[lastIdx].role === "assistant") {
        next[lastIdx] = {
          ...next[lastIdx],
          content: assistantTextRef.current,
          parts: [...partsRef.current],
        };
      } else {
        next.push({
          role: "assistant",
          content: assistantTextRef.current,
          parts: [...partsRef.current],
        });
      }
      return next;
    });
  }, []);

  const sendMessage = useCallback(
    async (contractId: string, message: string) => {
      // Reset state for new message
      assistantTextRef.current = "";
      partsRef.current = [];
      pendingToolsRef.current = [];

      setMessages((prev) => [...prev, { role: "user", content: message, parts: [] }]);
      setIsStreaming(true);

      const token = await getToken();
      abortRef.current?.abort();
      abortRef.current = new AbortController();

      try {
        const response = await fetch(`${BASE_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ contract_id: contractId, message }),
          signal: abortRef.current.signal,
        });

        if (!response.ok || !response.body) {
          const err = await response.json().catch(() => ({ detail: "Erro na API" }));
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Erro: ${err.detail}`, parts: [] },
          ]);
          setIsStreaming(false);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          let eventType = "";
          for (const line of lines) {
            if (line.startsWith("event: ")) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith("data: ") && eventType) {
              try {
                const data = JSON.parse(line.slice(6));
                handleEvent(eventType, data);
              } catch {
                // ignore malformed JSON
              }
              eventType = "";
            }
          }
        }

        // Ensure final state is clean
        if (assistantTextRef.current && partsRef.current.length === 0) {
          partsRef.current.push({ type: "text", content: assistantTextRef.current });
        }
        updateAssistantMessage();
      } catch (e) {
        if ((e as Error).name !== "AbortError") {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Erro: ${(e as Error).message}`, parts: [] },
          ]);
        }
      } finally {
        setIsStreaming(false);
      }

      function handleEvent(type: string, data: Record<string, unknown>) {
        switch (type) {
          case "context":
            setContext(data as unknown as ChatContext);
            break;

          case "tool_call": {
            const toolName = (data.tool as string) ?? "unknown";
            const callId = `tc_${Date.now()}_${toolName}`;

            // Flush any accumulated text as a text part before the tool call
            if (assistantTextRef.current.trim()) {
              partsRef.current.push({ type: "text", content: assistantTextRef.current });
              assistantTextRef.current = "";
            }

            partsRef.current.push({
              type: "tool_call",
              id: callId,
              tool: toolName as ToolName,
              args: (data.arguments as string) ?? "",
              status: "pending",
            });
            pendingToolsRef.current.push(callId);
            updateAssistantMessage();
            break;
          }

          case "tool_result": {
            const output = (data.output as string) ?? "{}";
            let parsed: unknown = {};
            try {
              parsed = JSON.parse(output);
            } catch {
              parsed = { raw_text: output };
            }

            // Match to first pending tool call (FIFO)
            const matchedId = pendingToolsRef.current.shift();
            if (matchedId) {
              // Update the tool_call part status to done
              const callPart = partsRef.current.find(
                (p) => p.type === "tool_call" && (p as ToolCallPart).id === matchedId
              ) as ToolCallPart | undefined;

              const toolName = callPart?.tool ?? ("unknown" as ToolName);

              if (callPart) {
                callPart.status = "done";
              }

              partsRef.current.push({
                type: "tool_result",
                tool: toolName,
                data: parsed,
                raw: output,
              });
            }
            updateAssistantMessage();
            break;
          }

          case "text": {
            // Complete text from a MessageOutputItem — replaces accumulated deltas
            const content = (data.content as string) ?? "";
            assistantTextRef.current = content;
            // Add as text part if there isn't one already for this segment
            partsRef.current.push({ type: "text", content });
            updateAssistantMessage();
            break;
          }

          case "text_delta": {
            const delta = (data.delta as string) ?? "";
            assistantTextRef.current += delta;
            updateAssistantMessage();
            break;
          }

          case "done":
            // Flush remaining text
            if (assistantTextRef.current.trim()) {
              const lastPart = partsRef.current[partsRef.current.length - 1];
              if (lastPart?.type === "text") {
                lastPart.content = assistantTextRef.current;
              } else {
                partsRef.current.push({ type: "text", content: assistantTextRef.current });
              }
            }
            updateAssistantMessage();
            setIsStreaming(false);
            break;

          case "error":
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: `Erro: ${(data.detail as string) ?? "desconhecido"}`,
                parts: [],
              },
            ]);
            setIsStreaming(false);
            break;
        }
      }
    },
    [updateAssistantMessage]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setContext(null);
    assistantTextRef.current = "";
    partsRef.current = [];
    pendingToolsRef.current = [];
  }, []);

  return { messages, isStreaming, context, sendMessage, clearMessages };
}
