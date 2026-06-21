from __future__ import annotations

import threading
from collections import deque
from dataclasses import asdict

from monitor import CheckResult


class Observer:
    def update(self, result: CheckResult) -> None:
        raise NotImplementedError


class StateStore(Observer):
    """Guarda os ultimos N resultados por URL."""

    def __init__(self, history_size: int) -> None:
        self.history_size = history_size
        self._history: dict[str, deque[CheckResult]] = {}
        # workers escrevem em varias threads, o front le no event loop
        self._lock = threading.Lock()

    def update(self, result: CheckResult) -> None:
        with self._lock:
            dq = self._history.get(result.url)
            if dq is None:
                dq = deque(maxlen=self.history_size)
                self._history[result.url] = dq
            dq.append(result)

    def latest(self) -> list[dict]:
        with self._lock:
            return [asdict(dq[-1]) for dq in self._history.values() if dq]

    def history(self, url: str) -> list[dict]:
        with self._lock:
            dq = self._history.get(url)
            return [asdict(r) for r in dq] if dq else []

    def forget(self, url: str) -> None:
        with self._lock:
            self._history.pop(url, None)


class AlertLogger(Observer):
    """Loga apenas a transicao ok -> falha (e a recuperacao)."""

    def __init__(self) -> None:
        self._last_ok: dict[str, bool] = {}

    def update(self, result: CheckResult) -> None:
        previous = self._last_ok.get(result.url)
        if previous is True and not result.ok:
            print(f"[ALERTA] {result.url} caiu (status={result.status} erro={result.error})", flush=True)
        elif previous is False and result.ok:
            print(f"[OK] {result.url} se recuperou", flush=True)
        self._last_ok[result.url] = result.ok
