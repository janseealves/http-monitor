from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass
class CheckResult:
    url: str
    ts: float
    status: int | None
    latency_ms: float | None
    ok: bool
    error: str | None = None


class Monitor:
    """Subject do padrao Observer: faz fan-out de cada resultado."""

    def __init__(self) -> None:
        self._observers = []

    def subscribe(self, observer) -> None:
        self._observers.append(observer)

    def notify(self, result: CheckResult) -> None:
        for observer in self._observers:
            observer.update(result)


class Supervisor:
    """Mantem uma thread por URL, cada uma em loop: check -> notify -> sleep."""

    def __init__(self, monitor: Monitor, interval: float, timeout: float) -> None:
        self.monitor = monitor
        self.interval = interval
        self.timeout = timeout
        self._workers: dict[str, tuple[threading.Thread, threading.Event]] = {}
        self._lock = threading.Lock()

    def add_target(self, url: str) -> bool:
        with self._lock:
            if url in self._workers:
                return False
            stop = threading.Event()
            thread = threading.Thread(
                target=self._run, args=(url, stop), daemon=True, name=f"worker:{url}"
            )
            self._workers[url] = (thread, stop)
        thread.start()
        return True

    def remove_target(self, url: str) -> bool:
        with self._lock:
            entry = self._workers.pop(url, None)
        if entry is None:
            return False
        _thread, stop = entry
        stop.set()
        return True

    def targets(self) -> list[str]:
        with self._lock:
            return list(self._workers)

    def _run(self, url: str, stop: threading.Event) -> None:
        # import local para evitar ciclo (checker importa CheckResult daqui)
        from checker import check

        while not stop.is_set():
            result = check(url, timeout=self.timeout)
            self.monitor.notify(result)
            stop.wait(self.interval)  # acorda na hora se a URL for removida
