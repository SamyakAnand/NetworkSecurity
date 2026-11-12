"""Security-related environment configuration helpers."""

from urllib.parse import urlsplit


def parse_cors_origins(raw_origins: str | None) -> list[str]:
    """Parse a comma-separated allowlist of explicit HTTP(S) origins.

    An empty value means same-origin requests only. Wildcards, credentials,
    paths, query strings, fragments, and non-HTTP schemes are rejected.
    """
    allowed_origins: list[str] = []

    for raw_origin in (raw_origins or "").split(","):
        origin = raw_origin.strip()
        if not origin:
            continue
        if origin == "*":
            raise ValueError("CORS_ORIGINS must list explicit origins; '*' is not allowed.")

        parsed = urlsplit(origin)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.netloc
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError(
                f"Invalid CORS origin {origin!r}; use an explicit HTTP(S) origin."
            )

        try:
            parsed.port
        except ValueError as exc:
            raise ValueError(f"Invalid port in CORS origin {origin!r}.") from exc

        normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
        if normalized not in allowed_origins:
            allowed_origins.append(normalized)

    return allowed_origins
