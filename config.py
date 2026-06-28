TARGETS = [
    "https://api.github.com",
    "https://www.wikipedia.org",
    "https://www.githubstatus.com/api/v2/status.json",
    "http://localhost:9",
]

INTERVAL = 5.0        # segundos entre checagens de uma mesma URL
HISTORY_SIZE = 30     # resultados mantidos por URL
TIMEOUT = 5.0         # timeout de cada requisição
