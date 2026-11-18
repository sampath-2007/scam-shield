import os
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from rules import analyze_message
from schemas import CheckRequest, CheckResponse

_LOCAL_FRONTEND_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
_ORIGINS_ENV_VAR = "SCAM_SHIELD_ALLOWED_ORIGINS"


def _configured_frontend_origins() -> list[str]:
    """Return exact configured origins, rejecting wildcards and URL paths."""
    origins = list(_LOCAL_FRONTEND_ORIGINS)
    configured_origins = os.getenv(_ORIGINS_ENV_VAR, "")

    for configured_origin in configured_origins.split(","):
        configured_origin = configured_origin.strip()
        if not configured_origin:
            continue

        try:
            parsed = urlsplit(configured_origin)
            parsed.port
        except ValueError as error:
            raise RuntimeError(
                f"{_ORIGINS_ENV_VAR} contains an invalid origin."
            ) from error

        is_loopback = parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
        if (
            "*" in configured_origin
            or (
                parsed.scheme.lower() != "https"
                and not (parsed.scheme.lower() == "http" and is_loopback)
            )
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise RuntimeError(
                f"{_ORIGINS_ENV_VAR} must contain exact HTTP(S) origins without paths."
            )

        origin = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
        if origin not in origins:
            origins.append(origin)

    return origins


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Scam Shield for Elders",
    description="Rule-based checks for potentially scam messages.",
    version="0.1.0",
)
app.state.limiter = limiter


async def _validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return useful validation errors without echoing submitted message contents."""
    safe_errors: list[dict[str, str]] = []
    for error in exc.errors():
        location = error.get("loc", ())
        field = str(location[-1]) if location else "request"
        error_type = error.get("type")

        if error_type == "json_invalid":
            field = "request"
            message = "Request body must be valid JSON."
        elif field == "text":
            message = (
                "Message text must be no more than 10,000 characters."
                if error_type == "string_too_long"
                else "Message text is required and must not be empty."
            )
        elif field == "language":
            message = "Language must be one of: en, hi, kn."
        else:
            field = "request"
            message = "Request contains an unexpected or invalid field."

        safe_errors.append({"field": field, "message": message})

    return JSONResponse(status_code=422, content={"detail": safe_errors})


async def _rate_limit_error_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait before trying again."},
    )


app.add_exception_handler(RequestValidationError, _validation_error_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_configured_frontend_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "app": "Scam Shield for Elders"}


@app.post("/api/check", response_model=CheckResponse)
@limiter.limit("10/minute")
def check_message(request: Request, payload: CheckRequest) -> CheckResponse:
    result = analyze_message(payload.text, payload.language)
    return CheckResponse(**result)
