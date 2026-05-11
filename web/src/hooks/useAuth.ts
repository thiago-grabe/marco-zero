import { useEffect, useState } from "react";
import { isDev, isAuthenticated, supabase } from "@/lib/auth";

export interface AuthState {
  authenticated: boolean;
  loading: boolean;
}

export function useAuth(): AuthState {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    isAuthenticated().then((auth) => {
      setAuthenticated(auth);
      setLoading(false);
    });

    if (!isDev) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange((_, session) => {
        setAuthenticated(!!session);
      });
      return () => subscription.unsubscribe();
    }
  }, []);

  return { authenticated, loading };
}
