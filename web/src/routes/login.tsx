import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { setAuth } from "@/lib/auth";
import { notifyAuthChange } from "@/hooks/useAuth";

export const Route = createFileRoute("/login")({
  component: Login,
});

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nome, setNome] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const endpoint = isRegister ? "/auth/register" : "/auth/login";
    const body = isRegister
      ? { email, password, nome: nome || undefined }
      : { email, password };

    try {
      const res = await fetch(`${BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Erro" }));
        setError(err.detail);
        setLoading(false);
        return;
      }

      const data = await res.json();
      setAuth(data.token, { user_id: data.user_id, email: data.email });
      notifyAuthChange();
      navigate({ to: "/dashboard" });
    } catch {
      setError("Falha na conexão com o servidor");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="max-w-sm w-full">
        <div className="text-center mb-10">
          <p className="text-xs text-primary uppercase tracking-widest mb-6">Marco Zero</p>
          <h1 className="font-serif text-2xl font-semibold mb-2">
            {isRegister ? "Criar conta" : "Entrar"}
          </h1>
          <p className="text-muted-foreground text-sm">
            {isRegister
              ? "Crie sua conta para começar a usar."
              : "Entre com seu e-mail e senha."}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="text-xs text-muted-foreground uppercase tracking-wide block mb-2">
                Nome (opcional)
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Seu nome"
                className="w-full bg-muted border border-border rounded-md px-4 py-3
                           text-sm text-foreground placeholder:text-muted-foreground
                           focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          )}

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

          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wide block mb-2">
              Senha
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 6 caracteres"
              className="w-full bg-muted border border-border rounded-md px-4 py-3
                         text-sm text-foreground placeholder:text-muted-foreground
                         focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          {error && <p className="text-xs text-loss">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-primary-foreground rounded-md py-3
                       text-sm font-medium hover:bg-primary/90 transition-colors
                       disabled:opacity-50"
          >
            {loading ? "Aguarde…" : isRegister ? "Criar conta" : "Entrar"}
          </button>
        </form>

        <p className="text-center mt-6 text-xs text-muted-foreground">
          {isRegister ? "Já tem conta?" : "Primeira vez?"}{" "}
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-foreground underline underline-offset-2"
          >
            {isRegister ? "Entrar" : "Criar conta"}
          </button>
        </p>
      </div>
    </div>
  );
}
