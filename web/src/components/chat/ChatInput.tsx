import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

interface ChatInputProps {
  onSend: (text: string) => void;
  isStreaming: boolean;
  prefill?: string;
}

export function ChatInput({ onSend, isStreaming, prefill }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Apply prefill from action buttons
  useEffect(() => {
    if (prefill) {
      setValue(prefill);
      textareaRef.current?.focus();
    }
  }, [prefill]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 150)}px`;
    }
  }, [value]);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="shrink-0 border-t border-border px-6 py-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte sobre seu financiamento…"
            disabled={isStreaming}
            rows={1}
            className="flex-1 bg-muted border border-border rounded-md px-4 py-3 resize-none
                       text-sm text-foreground placeholder:text-muted-foreground
                       focus:outline-none focus:ring-1 focus:ring-primary
                       disabled:opacity-50 max-h-[150px]"
          />
          <button
            onClick={handleSubmit}
            disabled={isStreaming || !value.trim()}
            className="bg-primary text-primary-foreground p-3 rounded-md
                       hover:bg-primary/90 transition-colors disabled:opacity-40
                       shrink-0"
            aria-label="Enviar mensagem"
          >
            <ArrowUp size={16} />
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Números calculados pelo motor SAC — a IA não calcula por conta própria.
        </p>
      </div>
    </div>
  );
}
