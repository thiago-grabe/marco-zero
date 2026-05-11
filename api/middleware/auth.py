"""
JWT validation para tokens emitidos pelo Supabase Auth.

Supabase usa RS256. Para validar, precisamos da chave pública do projeto.
No desenvolvimento, podemos usar HS256 com o JWT secret do projeto.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """
    Extrai e valida o JWT do header Authorization: Bearer <token>.
    Retorna o user_id (claim 'sub') se válido.
    """
    _is_placeholder = settings.supabase_jwt_secret in ("", "your-supabase-jwt-secret-here")
    if settings.is_dev and _is_placeholder:
        # Dev sem JWT real: aceita qualquer token ou sem token.
        # Retorna o user_id do token se presente, senão usa o dev default.
        if credentials:
            try:
                # Tenta decodificar sem verificar assinatura (só lê o sub)
                payload = jwt.decode(
                    credentials.credentials, options={"verify_signature": False}
                )
                if user_id := payload.get("sub"):
                    return user_id
            except JWTError:
                pass
        return "00000000-0000-0000-0000-000000000001"

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: sem user_id",
            )
        return user_id
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {e}",
        ) from e
