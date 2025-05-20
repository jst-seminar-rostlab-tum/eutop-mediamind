import json
import os
import sys

from eventregistry import *


def getarticles():
    er = EventRegistry(apiKey="f3ec0636-e14b-4fe6-980b-fc0720ab8131")
    query = {
        "$query": {
            "$and": [
                {
                    "$or": [
                        {"sourceUri": "faz.net"},
                        {"sourceUri": "bild.de"},
                        {"sourceUri": "spiegel.de"},
                    ]
                },
                {"dateStart": "2025-05-17", "dateEnd": "2025-05-18"},
            ]
        }
    }
    q = QueryArticlesIter.initWithComplexQuery(query)
    # change maxItems to get the number of results that you want
    for article in q.execQuery(er, maxItems=100):
        print(article)
