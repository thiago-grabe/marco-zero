/**
 * MarkdownRenderer — renders LLM markdown with dark premium styling.
 *
 * During active streaming, falls back to whitespace-pre-wrap.
 * After streaming ends, renders full markdown with react-markdown.
 *
 * Custom overrides:
 *   - Tables: border-border, font-serif tabular-nums for BRL cells
 *   - Strong: font-semibold (the bold fix)
 *   - Code: bg-muted with copy button
 *   - Headings: font-serif
 */

import React, { useState } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

const BRL_PATTERN = /^R\$\s/;

const components: Components = {
  h2: ({ children }) => (
    <h2 className="font-serif text-lg font-semibold text-foreground mt-4 mb-2">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="font-serif text-base font-semibold text-foreground mt-3 mb-1.5">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm text-foreground leading-relaxed mb-3">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="text-foreground font-semibold">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="text-muted-foreground">{children}</em>
  ),
  ul: ({ children }) => (
    <ul className="text-sm text-foreground list-disc pl-5 mb-3 space-y-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="text-sm text-foreground list-decimal pl-5 mb-3 space-y-1">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="text-sm text-foreground leading-relaxed">{children}</li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-primary pl-4 text-muted-foreground italic my-3">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} className="text-primary hover:text-primary/80 underline underline-offset-2">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="border border-border rounded-lg overflow-hidden my-3">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-muted">{children}</thead>,
  th: ({ children }) => (
    <th className="text-xs text-muted-foreground uppercase tracking-wider px-3 py-2 text-left font-medium">
      {children}
    </th>
  ),
  td: ({ children }) => {
    const text = typeof children === "string" ? children : String(children ?? "");
    const isBRL = BRL_PATTERN.test(text.trim());
    return (
      <td
        className={`px-3 py-2 border-t border-border ${
          isBRL ? "font-serif tabular-nums text-right text-foreground" : "text-foreground"
        }`}
      >
        {children}
      </td>
    );
  },
  code: ({ className, children }) => {
    const isBlock = className?.includes("language-");
    if (isBlock) {
      return <code className={`${className} text-xs`}>{children}</code>;
    }
    return (
      <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-foreground">
        {children}
      </code>
    );
  },
  pre: ({ children }) => <CodeBlock>{children}</CodeBlock>,
};

function CodeBlock({ children }: { children: React.ReactNode }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = extractText(children);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-3">
      <pre className="bg-muted rounded-lg p-4 overflow-x-auto text-xs">{children}</pre>
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 text-xs text-muted-foreground hover:text-foreground
                   bg-background/80 px-2 py-1 rounded border border-border opacity-0
                   group-hover:opacity-100 transition-opacity"
      >
        {copied ? "Copiado" : "Copiar"}
      </button>
    </div>
  );
}

function extractText(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (React.isValidElement(node) && node.props.children) {
    return extractText(node.props.children);
  }
  return "";
}

interface MarkdownRendererProps {
  content: string;
  isStreaming?: boolean;
}

export const MarkdownRenderer = React.memo(function MarkdownRenderer({
  content,
  isStreaming = false,
}: MarkdownRendererProps) {
  if (!content.trim()) return null;

  // During streaming: plain text to avoid broken partial markdown
  if (isStreaming) {
    return (
      <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
        {content}
      </div>
    );
  }

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
});
