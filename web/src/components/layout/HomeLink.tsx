import { Link } from "@tanstack/react-router";

/**
 * Logo clicável que leva para a home (/).
 * Presente em TODAS as páginas do app.
 */
export function HomeLink({ className = "h-5" }: { className?: string }) {
  return (
    <Link to="/" title="Voltar para o início">
      <img src="/brand/logo-dark.svg" alt="Tenor" className={className} />
    </Link>
  );
}
