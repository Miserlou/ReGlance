"""
seed.py

Seed some data to the service via API. Ignore this.
"""

import requests


URL_BASE = "http://localhost:5000"


data = {
    "url": "https://blog.zappa.io/posts/introducing-nodb-pythonic-data-store-s3",
    "title": "Introducing NoDB"
}
r = requests.post(URL_BASE + "/record/", json=data)
