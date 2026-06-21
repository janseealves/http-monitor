import time

import httpx

from monitor import CheckResult


def check(url: str, timeout: float = 5.0) -> CheckResult:
    start = time.perf_counter()
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True)
        elapsed = (time.perf_counter() - start) * 1000
        return CheckResult(
            url=url,
            ts=time.time(),
            status=resp.status_code,
            latency_ms=round(elapsed, 1),
            ok=resp.status_code < 400,
        )
    except httpx.RequestError as exc:
        # timeout, DNS, conexao recusada... vira resultado, nao exceção
        elapsed = (time.perf_counter() - start) * 1000
        return CheckResult(
            url=url,
            ts=time.time(),
            status=None,
            latency_ms=round(elapsed, 1),
            ok=False,
            error=type(exc).__name__,
        )
