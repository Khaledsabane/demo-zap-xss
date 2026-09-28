import sys
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            partial(app.DemoHandler, directory=str(app.SITE)),
        )
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get_search_page(self, query):
        encoded_query = urlencode({"q": query})
        url = f"http://127.0.0.1:{self.server.server_port}/search?{encoded_query}"
        with urlopen(url) as response:
            return response.status, response.read().decode("utf-8")

    def test_home_page_is_available(self):
        with urlopen(f"http://127.0.0.1:{self.server.server_port}/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"CyberShop", response.read())

    def test_search_page_is_available(self):
        status, body = self.get_search_page("ordinateur")
        self.assertEqual(status, 200)
        self.assertIn("Recherche", body)
        self.assertIn("ordinateur", body)


if __name__ == "__main__":
    unittest.main()
