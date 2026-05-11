import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { devLogin, isDev, supabase } from "@/lib/auth";

export const Route = createFileRoute("/login")({
  component: Login,
});

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleMagicLink(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/dashboard` },
    });

    setLoading(false);
    if (error) {
      setError(error.message);
    } else {
      setSent(true);
    }
  }

  function handleDevLogin() {
    devLogin();
    navigate({ to: "/dashboard" });
  }

  if (sent) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-6">
        <div className="max-w-sm w-full text-center">
          <p className="text-xs text-primary uppercase tracking-widest mb-6">
            Marco Zero
          </p>
          <h1 className="font-serif text-2xl font-semibold mb-4">
            Verifique seu e-mail
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed mb-8">
            Enviamos um link de acesso para{" "}
            <span className="text-foreground">{email}</span>.
            <br />
            Clique no link para entrar.
          </p>
          <button
            onClick={() => setSent(false)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Usar outro e-mail
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="max-w-sm w-full">
        {/* Header */}
        <div className="text-center mb-10">
          <p className="text-xs text-primary uppercase tracking-widest mb-6">
            Marco Zero
          </p>
          <h1 className="font-serif text-2xl font-semibold mb-2">
            Entrar
          </h1>
          <p className="text-muted-foreground text-sm">
            Sem senha. Receba um link no seu e-mail.
          </p>
        </div>

        {/* Form */}
        {!isDev ? (
          <form onSubmit={handleMagicLink} className="space-y-4">
            <div>
              <label className="text-xs text-muted-foreground uppercase tracking-wide block mb-2">
                E-mail
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                className="w-full bg-muted border border-border rounded-md px-4 py-3
                           text-sm text-foreground placeholder:text-muted-foreground
                           focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            {error && (
              <p className="text-xs text-loss">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground rounded-md py-3
                         text-sm font-medium hover:bg-primary/90 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Enviando…" : "Receber link de acesso"}
            </button>
          </form>
        ) : (
          /* Dev mode: botão direto sem auth real */
          <div className="space-y-4">
            <div className="border border-dashed border-border rounded-md p-4 text-center">
              <p className="text-xs text-muted-foreground mb-3">
                Modo dev — Supabase não configurado
              </p>
              <button
                onClick={handleDevLogin}
                className="w-full bg-primary text-primary-foreground rounded-md py-3
                           text-sm font-medium hover:bg-primary/90 transition-colors"
              >
                Entrar como dev
              </button>
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Configure{" "}
              <code className="text-foreground">VITE_SUPABASE_URL</code> e{" "}
              <code className="text-foreground">VITE_SUPABASE_ANON_KEY</code> no{" "}
              <code className="text-foreground">web/.env.local</code> para usar
              magic link real.
            </p>
          </div>
        )}

        <p className="text-center mt-6 text-xs text-muted-foreground">
          Primeira vez?{" "}
          <span className="text-foreground">
            Conta criada automaticamente ao entrar.
          </span>
        </p>
      </div>
    </div>
  );
}
