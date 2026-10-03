from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import os


SITE = Path(__file__).resolve().parent / "site"


class DemoHandler(SimpleHTTPRequestHandler):
    """Sert les fichiers statiques et la page de recherche de démonstration."""

    def _send_html(self, content, status=200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _search_page(self, query):
        #heeeey
        displayed_query = query

        return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recherche | CyberShop</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header>
    <a class="brand" href="/">CyberShop</a>
    <nav><a href="/">Accueil</a><a href="/about.html">Le projet</a></nav>
  </header>
  <main>
    <section class="hero compact">
      <span class="pill">Résultat de recherche</span>
      <h1>Recherche</h1>
      <p>Vous avez recherché : <strong>{displayed_query}</strong></p>
      <a class="button" href="/">Nouvelle recherche</a>
    </section>
  </main>
  <footer>CyberShop | Démonstration XSS</footer>
</body>
</html>"""

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._send_html(self._search_page(query))
            return

        super().do_GET()


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(
        (host, port),
        partial(DemoHandler, directory=str(SITE)),
    )
    print(f"Demo sur http://{host}:{port}", flush=True)
    server.serve_forever()
