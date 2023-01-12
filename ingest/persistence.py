"""
This module provides methods for persisting processed data to long-term storage
"""
from google.cloud import firestore

from .debugging import app_logger as log

def persist_no_op(*args, **kwargs):
    pass

def get_database_client() -> firestore.Client:
    return firestore.Client()

def persist(client, pubname, collname, doc_id, document_dict):
    pass

def increment_pubication(client, pubname, count):
    pass

