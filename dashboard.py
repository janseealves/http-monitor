from __future__ import annotations

import time

import streamlit as st

import config
from monitor import Monitor, Supervisor
from observers import AlertLogger, StateStore

st.set_page_config(page_title="Monitor de Webservices HTTP", page_icon="📡", layout="wide")

REFRESH_SECONDS = 2


@st.cache_resource
def start_monitor() -> tuple[Supervisor, StateStore]:
    # cache_resource garante que os workers subam uma vez so,
    # mesmo o script sendo reexecutado a cada interacao
    monitor = Monitor()
    store = StateStore(history_size=config.HISTORY_SIZE)
    monitor.subscribe(store)
    monitor.subscribe(AlertLogger())

    supervisor = Supervisor(monitor, interval=config.INTERVAL, timeout=config.TIMEOUT)
    for url in config.TARGETS:
        supervisor.add_target(url)
    return supervisor, store


supervisor, store = start_monitor()

st.title("Monitor de Webservices HTTP")
st.caption("Checagens periodicas via threads, padrao Observer, dashboard com auto-refresh")

with st.form("add_target", clear_on_submit=True):
    col_url, col_btn = st.columns([5, 1])
    new_url = col_url.text_input("URL", placeholder="https://exemplo.com/health", label_visibility="collapsed")
    submitted = col_btn.form_submit_button("Monitorar", use_container_width=True)
    if submitted and new_url.strip():
        if supervisor.add_target(new_url.strip()):
            st.toast(f"Monitorando {new_url.strip()}")
        else:
            st.toast("Essa URL ja esta sendo monitorada")


def render_summary(results: list[dict]) -> None:
    up = sum(1 for r in results if r["ok"])
    down = len(results) - up
    lats = [r["latency_ms"] for r in results if r["ok"] and r["latency_ms"] is not None]
    avg = round(sum(lats) / len(lats), 1) if lats else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monitorando", len(results))
    c2.metric("No ar", up)
    c3.metric("Fora do ar", down)
    c4.metric("Latencia media", f"{avg} ms" if avg is not None else "—")


def render_card(result: dict) -> None:
    ok = result["ok"]
    status = str(result["status"]) if result["status"] is not None else "falha"
    latency = str(int(round(result["latency_ms"]))) if result["latency_ms"] is not None else "—"
    quando = time.strftime("%H:%M:%S", time.localtime(result["ts"]))

    with st.container(border=True):
        st.markdown(f'{"🟢" if ok else "🔴"} **{result["url"]}**')
        c1, c2 = st.columns(2)
        c1.metric("Status", status)
        c2.metric("Latencia (ms)", latency)

        # historico recente de latencia
        hist = [h["latency_ms"] for h in store.history(result["url"]) if h["latency_ms"] is not None]
        if len(hist) > 1:
            st.line_chart(hist, height=90)

        estado = "disponivel" if ok else f"indisponivel ({result['error']})" if result["error"] else "indisponivel"
        st.caption(f"{estado} · ultima checagem {quando}")
        if st.button("remover", key=f"rm::{result['url']}", use_container_width=True):
            supervisor.remove_target(result["url"])
            store.forget(result["url"])
            st.rerun()


@st.fragment(run_every=REFRESH_SECONDS)
def dashboard() -> None:
    # ok=False vem primeiro, entao as falhas aparecem no topo
    results = sorted(store.latest(), key=lambda r: (r["ok"], r["url"]))
    if not results:
        st.info("Aguardando a primeira checagem...")
        return

    render_summary(results)
    st.divider()

    cols = st.columns(2)
    for i, result in enumerate(results):
        with cols[i % 2]:
            render_card(result)


dashboard()
