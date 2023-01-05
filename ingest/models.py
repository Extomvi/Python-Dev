"""
Module that provides models used as messages to be passed via the messageq
"""

from collections import Counter
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel

class Post(BaseModel):
    '''Post method is used to store content from the front-end'''
    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

class ProcessedPost(BaseModel):
    '''ProcessedPost is used to store results of the DataProcessor'''

    @property
    def pub_key(self) -> str:
        return None

    def transform_for_database(self, top_n=2000) -> List[Tuple[str, str, str, Dict]]:
        return None

    def __add__(self, other) -> ProcessedPost:
        return self