import { useCallback, useSyncExternalStore } from "react";
import { isAuthenticated, clearAuth, getStoredUser } from "@/lib/auth";

// Reativo: qualquer componente que use useAuth re-renderiza quando o token muda
const listeners = new Set<() => void>();
function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

function getSnapshot(): boolean {
  return isAuthenticated();
}

/** Notifica todos os subscribers que o estado de auth mudou. */
export function notifyAuthChange(): void {
  listeners.forEach((cb) => cb());
}

export function useAuth() {
  const authenticated = useSyncExternalStore(subscribe, getSnapshot);
  const user = getStoredUser();

  const logout = useCallback(() => {
    clearAuth();
    notifyAuthChange();
  }, []);

  return { authenticated, user, logout };
}
