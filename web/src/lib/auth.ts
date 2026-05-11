/**
 * Auth local — sem Supabase, sem serviços externos.
 * JWT armazenado no localStorage.
 */

const TOKEN_KEY = "mz-token";
const USER_KEY = "mz-user";

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

/** Retorna o token para o API client. */
export async function getToken(): Promise<string | null> {
  return getStoredToken();
}
