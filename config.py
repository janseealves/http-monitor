# Configurações do monitor. Edite aqui as URLs e os parâmetros de checagem.

TARGETS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/503",
    "https://example.com",
]

INTERVAL = 5.0        # segundos entre checagens de uma mesma URL
HISTORY_SIZE = 30     # quantos resultados manter por URL
TIMEOUT = 5.0         # timeout de cada requisição HTTP
