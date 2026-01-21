import os

if "OPIK_PROJECT_NAME" not in os.environ:
    os.environ["OPIK_PROJECT_NAME"] = "PlanProof"

try:
    import opik as _opik  # type: ignore
except Exception:  # pragma: no cover - optional tracing dependency
    _opik = None


class _NoOpOpik:
    @staticmethod
    def track(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator


opik = _opik if _opik is not None else _NoOpOpik()
