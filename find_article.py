#!/usr/bin/env python
"""Quick script to find a recent Knigovishte article."""
import urllib.request
from html.parser import HTMLParser
import sys

class LinkFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_article = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.in_article = True
        if tag == 'a' and self.in_article:
            for attr, value in attrs:
                if attr == 'href' and value and '/vijte/' in value:
                    self.links.append(value)

try:
    # Fetch homepage
    url = "https://www.knigovishte.bg/vijte"
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "knigovishte-podcast/0.1", "Accept-Language": "bg,en;q=0.8"}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode('utf-8', errors='replace')

    # Find article links
    parser = LinkFinder()
    parser.feed(html)

    if parser.links:
        first_link = parser.links[0]
        # Ensure absolute URL
        if first_link.startswith('/'):
            first_link = "https://www.knigovishte.bg/vijte" + first_link
        print(first_link)
    else:
        print("No article links found", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
