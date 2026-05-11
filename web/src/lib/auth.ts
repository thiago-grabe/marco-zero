import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL ?? "";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";

export const isDev = !supabaseUrl || !supabaseAnonKey;

// Em dev sem Supabase configurado, criamos um client dummy que não faz chamadas reais
export const supabase = createClient(
  supabaseUrl || "https://placeholder.supabase.co",
  supabaseAnonKey || "placeholder-anon-key"
);

// Chave usada para armazenar o token dev no localStorage
const DEV_TOKEN_KEY = "mz-dev-token";
// Token fake aceito pelo backend em modo dev
const DEV_TOKEN = "dev.bypass.token";

/** Retorna o access token atual (Supabase real ou dev bypass). */
export async function getToken(): Promise<string | null> {
  if (isDev) {
    return localStorage.getItem(DEV_TOKEN_KEY);
  }
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}

/** Login dev: injeta um token fake que o backend aceita em modo dev. */
export function devLogin(): void {
  localStorage.setItem(DEV_TOKEN_KEY, DEV_TOKEN);
}

/** Logout — limpa sessão Supabase ou token dev. */
export async function logout(): Promise<void> {
  if (isDev) {
    localStorage.removeItem(DEV_TOKEN_KEY);
    return;
  }
  await supabase.auth.signOut();
}

/** Verifica se o usuário está logado. */
export async function isAuthenticated(): Promise<boolean> {
  if (isDev) {
    return !!localStorage.getItem(DEV_TOKEN_KEY);
  }
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return !!session;
}
