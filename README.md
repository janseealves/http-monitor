# Monitor de Webservices HTTP

Aplicação desenvolvida para a disciplina de Rede de Computadores (2026.1).

A aplicação monitora uma lista de URLs, fazendo checagens periódicas em cada
uma. Para cada checagem ela registra o status HTTP e o tempo de resposta
(latência), guarda os últimos resultados em memória e mostra tudo num dashboard
que se atualiza sozinho. Dá pra adicionar e remover URLs pelo próprio dashboard,
sem reiniciar a aplicação.

## Tópicos de rede abordados

- HTTP: requisição GET em cada URL e leitura do status code.
- Medição de desempenho: latência por requisição (medida com `time.perf_counter`).
- Threads: uma thread por URL, cada uma fazendo as checagens em loop.
- Padrão Observer: um Monitor (Subject) repassa cada resultado para os observers.
- Dashboard em tempo real e formulário para o conteúdo dinâmico do webservice.

## Como funciona

Cada thread (worker) chama `check(url)`, que devolve um `CheckResult` com status,
latência e se está no ar. O worker passa esse resultado para o `Monitor`, que
avisa todos os observers inscritos:

- `StateStore`: guarda o histórico recente de cada URL em memória.
- `AlertLogger`: imprime um aviso quando uma URL sai do ar (transição ok -> falha).

O dashboard em Streamlit lê o `StateStore` e redesenha os cards a cada poucos
segundos. Se um servidor cai ou demora demais, o erro vira um resultado normal
(marcado como indisponível) em vez de derrubar a thread.

Arquivos:

- `config.py` — URLs monitoradas, intervalo, tamanho do histórico e timeout.
- `checker.py` — a função que faz o GET e mede a latência.
- `monitor.py` — `CheckResult`, o `Monitor` (Subject) e o `Supervisor` das threads.
- `observers.py` — o Observer base e os observers concretos.
- `dashboard.py` — o dashboard em Streamlit.

## Pré-requisitos

- Python 3.11 ou superior
- As bibliotecas listadas em `requirements.txt` (`streamlit` e `httpx`)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar

```bash
streamlit run dashboard.py
```

Depois é só abrir o endereço que o Streamlit mostra no terminal
(normalmente http://localhost:8501).

As URLs iniciais ficam em `config.py`. Para acompanhar outras, use o formulário
do dashboard.

## Autoria e contribuições

Projeto acadêmico desenvolvido por Jansen para a disciplina de Rede de
Computadores (2026.1).
