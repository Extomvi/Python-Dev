from collections import Counter
from typing import Dict

import spacy
"""
This module helps to process text using NLP to extract the entities in the texts i.e nouns (place, person, things e.t.c)

We download the model before we can utilize it

"""

from .debugging import app_logger as log


class DataProcessor():

    def __init__(self) -> None:
        log.info('spacy model loading')
        self.nlp = spacy.load("en_core_web_sm")
        log.info('space model loaded')
        self.skip = ['CARDINAL', 'MONEY', 'ORDINAL', 'DATE', 'TIME']

    def entities(self, doc) -> Counter:
        t = [e.text.lower() for e in doc.ents if e.label_ not in self.skip]
        return Counter(t)

    def process(self, text: str) -> Dict:
        return  {'entities': self.entities(self.nlp(text))}

    def process_message(self, post):
        return None