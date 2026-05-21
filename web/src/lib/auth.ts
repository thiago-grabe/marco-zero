/**
 * Auth silencioso — sem tela de login.
 *
 * Na primeira visita, cria uma conta anônima automaticamente.
 * Se o token expirar ou ficar inválido, recria automaticamente.
 * O usuário nunca vê erro de autenticação.
 */

const TOKEN_KEY = "mz-token";
const USER_KEY = "mz-user";
const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

export interface AuthUser {
  user_id: string;
  email: string;
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setAuth(token: string, user: AuthUser): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem(TOKEN_KEY);
}

export async function getToken(): Promise<string | null> {
  return getStoredToken();
}

/**
 * Cria uma conta anônima e armazena o token.
 */
async function createAnonymousAccount(): Promise<boolean> {
  const anonId = crypto.randomUUID().slice(0, 8);
  const email = `anon-${anonId}@tenor.local`;
  const password = crypto.randomUUID();

  try {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (res.ok) {
      const data = await res.json();
      setAuth(data.token, { user_id: data.user_id, email: data.email });
      return true;
    }
  } catch {
    // Backend indisponível
  }
  return false;
}

/**
 * Garante que o usuário tem um token válido.
 * Se não tem, cria conta anônima. Chamado pelo root layout.
 */
export async function ensureAuth(): Promise<void> {
  if (isAuthenticated()) return;
  await createAnonymousAccount();
}

/**
 * Renova o token quando recebe 401.
 * Limpa o token antigo, cria nova conta, retorna true se conseguiu.
 * Chamado automaticamente pelo API client quando recebe 401.
 */
export async function renewAuth(): Promise<boolean> {
  clearAuth();
  return createAnonymousAccount();
}
