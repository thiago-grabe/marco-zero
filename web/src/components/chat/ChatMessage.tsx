/**
 * ChatMessage — renders a single message by iterating its parts[].
 *
 * Interleaves text (markdown) with tool indicators and result cards
 * in the order they occurred during the conversation.
 */

import { Component, type ReactNode } from "react";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { ToolCallIndicator } from "./ToolCallIndicator";
import { ToolResultCard } from "./ToolResultCard";
import type { ActionHandler, ChatMessage as ChatMessageType } from "./types";

// ── Error Boundary ───────────────────────────────────────────────────────────

interface ErrorBoundaryProps {
  fallback: ReactNode;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

class MessageErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

// ── Component ────────────────────────────────────────────────────────────────

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
  isLastMessage?: boolean;
  onAction: ActionHandler;
}

export function ChatMessageView({
  message,
  isStreaming = false,
  isLastMessage = false,
  onAction,
}: ChatMessageProps) {
  const isStreamingThis = isStreaming && isLastMessage;

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 max-w-[80%]">
          <p className="text-sm text-foreground">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message — render parts if available, fallback to content
  const hasParts = message.parts.length > 0;

  return (
    <MessageErrorBoundary
      fallback={
        <div className="border border-loss/30 rounded-lg p-4 bg-loss/5 text-sm text-loss">
          Erro ao renderizar resposta.
          <details className="mt-2">
            <summary className="text-xs cursor-pointer">Ver texto bruto</summary>
            <pre className="mt-1 text-xs whitespace-pre-wrap text-muted-foreground">
              {message.content}
            </pre>
          </details>
        </div>
      }
    >
      <div className="max-w-[95%] space-y-1">
        {hasParts ? (
          message.parts.map((part, i) => {
            switch (part.type) {
              case "text":
                return (
                  <MarkdownRenderer
                    key={`text-${i}`}
                    content={part.content}
                    isStreaming={isStreamingThis && i === message.parts.length - 1}
                  />
                );
              case "tool_call":
                return (
                  <ToolCallIndicator
                    key={`tc-${part.id}`}
                    tool={part.tool}
                    status={part.status}
                  />
                );
              case "tool_result":
                return (
                  <ToolResultCard
                    key={`tr-${i}`}
                    tool={part.tool}
                    data={part.data}
                    raw={part.raw}
                    onAction={onAction}
                  />
                );
              default:
                return null;
            }
          })
        ) : (
          // Fallback: no parts yet (streaming in progress, text accumulating)
          <MarkdownRenderer
            content={message.content}
            isStreaming={isStreamingThis}
          />
        )}
      </div>
    </MessageErrorBoundary>
  );
}
