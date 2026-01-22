import os
import socket
import sys

if "OPIK_PROJECT_NAME" not in os.environ:
    os.environ["OPIK_PROJECT_NAME"] = "PlanProof"


def _warn(message: str) -> None:
    print(f"OPIK WARNING: {message}", file=sys.stderr)


def _network_available() -> bool:
    try:
        socket.getaddrinfo("www.comet.com", 443)
        return True
    except OSError:
        return False


try:
    import opik as _opik  # type: ignore
    from opik import opik_context as _opik_context  # type: ignore
except Exception as exc:  # pragma: no cover - optional tracing dependency
    _warn(f"Opik import failed; tracing disabled. ({exc})")
    _opik = None
    _opik_context = None


class _NoOpOpik:
    @staticmethod
    def track(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator


class _NoOpOpikContext:
    @staticmethod
    def update_current_span(*_args, **_kwargs) -> None:
        return None

    @staticmethod
    def update_current_trace(*_args, **_kwargs) -> None:
        return None


_opik_enabled = bool(_opik and _opik_context)
if not os.environ.get("OPIK_API_KEY"):
    _warn("OPIK_API_KEY not set; tracing disabled.")
    _opik_enabled = False

if _opik_enabled and not _network_available():
    _warn("Network unavailable; tracing disabled.")
    _opik_enabled = False

opik = _opik if _opik_enabled else _NoOpOpik()
opik_context = _opik_context if _opik_enabled else _NoOpOpikContext()
