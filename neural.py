"""
Neural Web Cartographer
-----------------------
A cyberpunk-style live web intelligence visualizer.

What it does:
- Crawls a website
- Extracts internal links
- Builds a relationship graph
- Detects "important" pages using PageRank
- Creates an interactive HTML visualization
- Generates a mini AI summary of the site's structure

Why it's cool:
- Feels like a hacker recon tool
- Produces a visual network map
- Useful for SEO, security research, and curiosity

Install:
    pip install requests beautifulsoup4 networkx pyvis colorama

Run:
    python web_cartographer.py https://example.com
"""

import sys
import time
import queue
import requests
import networkx as nx

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pyvis.network import Network
from colorama import Fore, Style, init

init(autoreset=True)

MAX_PAGES = 40
TIMEOUT = 5


class WebCartographer:
    def __init__(self, start_url):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.visited = set()
        self.graph = nx.DiGraph()

    def is_internal(self, url):
        return urlparse(url).netloc == self.domain

    def clean_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

    def extract_links(self, url):
        links = set()

        try:
            response = requests.get(
                url,
                timeout=TIMEOUT,
                headers={
                    "User-Agent": "NeuralWebCartographer/1.0"
                }
            )

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup.find_all("a", href=True):
                href = urljoin(url, tag["href"])
                href = self.clean_url(href)

                if self.is_internal(href):
                    links.add(href)

        except Exception as e:
            print(Fore.RED + f"[!] Failed: {url} ({e})")

        return links

    def crawl(self):
        q = queue.Queue()
        q.put(self.start_url)

        print(Fore.CYAN + "\n[+] Initializing neural crawl...\n")

        while not q.empty() and len(self.visited) < MAX_PAGES:
            current = q.get()

            if current in self.visited:
                continue

            print(Fore.GREEN + f"[SCAN] {current}")

            self.visited.add(current)
            self.graph.add_node(current)

            links = self.extract_links(current)

            for link in links:
                self.graph.add_edge(current, link)

                if link not in self.visited:
                    q.put(link)

            time.sleep(0.2)

    def analyze(self):
        print(Fore.YELLOW + "\n[+] Running graph intelligence...\n")

        pagerank = nx.pagerank(self.graph)

        ranked = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )

        print(Fore.MAGENTA + "Most influential pages:\n")

        for url, score in ranked[:10]:
            print(
                Fore.WHITE +
                f"{score:.4f}  ->  {url}"
            )

        return pagerank

    def visualize(self, pagerank):
        print(Fore.CYAN + "\n[+] Building interactive visualization...\n")

        net = Network(
            height="900px",
            width="100%",
            bgcolor="#0d1117",
            font_color="white",
            directed=True
        )

        for node in self.graph.nodes():
            score = pagerank.get(node, 0)

            size = 15 + score * 300

            color = (
                "#ff4d4d" if score > 0.05
                else "#4da6ff"
            )

            net.add_node(
                node,
                label=node.split("/")[-1] or "/",
                title=node,
                size=size,
                color=color
            )

        for src, dst in self.graph.edges():
            net.add_edge(src, dst)

        net.force_atlas_2based()

        output = "web_map.html"
        net.save_graph(output)

        print(Fore.GREEN + f"[✓] Visualization saved to: {output}")

    def ai_summary(self):
        print(Fore.YELLOW + "\n[+] AI structural summary\n")

        total_nodes = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()

        density = nx.density(self.graph)

        print(Fore.WHITE + f"Pages discovered: {total_nodes}")
        print(Fore.WHITE + f"Connections mapped: {total_edges}")
        print(Fore.WHITE + f"Graph density: {density:.4f}")

        if density > 0.1:
            print(Fore.GREEN + "Site appears highly interconnected.")
        else:
            print(Fore.BLUE + "Site structure is sparse and hierarchical.")

        dead_ends = [
            n for n in self.graph.nodes()
            if self.graph.out_degree(n) == 0
        ]

        if dead_ends:
            print(
                Fore.RED +
                f"Detected {len(dead_ends)} dead-end pages."
            )

    def run(self):
        self.crawl()
        pagerank = self.analyze()
        self.visualize(pagerank)
        self.ai_summary()

        print(
            Fore.CYAN +
            Style.BRIGHT +
            "\n[✓] Neural web cartography complete.\n"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python web_cartographer.py https://example.com")
        return

    url = sys.argv[1]

    if not url.startswith("http"):
        url = "https://" + url

    bot = WebCartographer(url)
    bot.run()


if __name__ == "__main__":
    main()
