from functools import wraps

from sanic.response import json

from app.auth import decode_token


def require_auth(role: str | None = None):
    def decorator(f):
        @wraps(f)
        async def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return json({"error": "Unauthorized"}, status=401)

            token = auth_header[7:]
            try:
                payload = decode_token(token)
            except Exception:
                return json({"error": "Invalid or expired token"}, status=401)

            if role and payload.get("role") != role:
                return json({"error": "Forbidden"}, status=403)

            request.ctx.user_id = payload["sub"]
            request.ctx.role = payload["role"]
            return await f(request, *args, **kwargs)

        return wrapper
    return decorator