from fastapi import Request
from ai_os.security.context import RequestContext
from ai_os.security.identity import Role

def resolve_request_context(request: Request) -> RequestContext:
    """
    Temporary auth mechanism.
    Reads identity from headers.
    """

    user_id = request.headers.get("X-User-Id", "anonymous")
    role_header = request.headers.get("X-User-Role", "user").lower()

    role = Role.ADMIN if role_header == "admin" else Role.USER

    return RequestContext(user_id=user_id, role=role)