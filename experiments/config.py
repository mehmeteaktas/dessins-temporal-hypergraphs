"""Paths and communities. Override the data location with the environment variable DESSINS_DATA."""

import os

DATA_DIR = os.environ.get("DESSINS_DATA", "data")
RESULTS_DIR = os.environ.get("DESSINS_RESULTS", "results")

# community name -> Stack Exchange site; data are expected in DATA_DIR/<name>/Posts.xml and Comments.xml
SITES = {
    "DataScience": "datascience.stackexchange.com",
    "AI": "ai.stackexchange.com",
    "Biology": "biology.stackexchange.com",
    "Astronomy": "astronomy.stackexchange.com",
    "Academia": "academia.stackexchange.com",
}


def folder(name):
    return os.path.join(DATA_DIR, name)
