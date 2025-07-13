"""
MongoDB util functions file.
"""

from collections.abc import Mapping, Sequence
from datetime import datetime

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure

from server.utils.aws.ssm import get_secret


def deep_serialize_mongo(doc, seen=None):
    if seen is None:
        seen = set()

    # Avoid infinite recursion for shared/circular references
    doc_id = id(doc)
    if doc_id in seen:
        return None  # or raise an error / return a placeholder
    seen.add(doc_id)

    # Convert ObjectId to string
    if isinstance(doc, ObjectId):
        return str(doc)

    # Leave datetime as-is (FastAPI handles it)
    if isinstance(doc, datetime):
        return doc

    # Recursively handle lists/tuples
    if isinstance(doc, Sequence) and not isinstance(doc, str):
        return [deep_serialize_mongo(item, seen) for item in doc]

    # Recursively handle dictionaries
    if isinstance(doc, Mapping):
        return {key: deep_serialize_mongo(value, seen) for key, value in doc.items()}

    # Return primitives as-is
    return doc


def create_mongodb_instance() -> AsyncMongoClient | None:
    try:
        mongo_db_user = get_secret("/alwayssaved/MONGO_DB_USER")

        mongo_db_password = get_secret("/alwayssaved/MONGO_DB_PASSWORD")

        mongo_db_base_uri = get_secret("/alwayssaved/MONGO_DB_BASE_URI")

        mongo_db_name = get_secret("/alwayssaved/MONGO_DB_NAME")

        mongo_db_cluster_name = get_secret("/alwayssaved/MONGO_DB_CLUSTER_NAME")

        if (
            mongo_db_user is None
            or mongo_db_password is None
            or mongo_db_base_uri is None
            or mongo_db_cluster_name is None
            or mongo_db_name is None
        ):
            raise ValueError("MONGO_DB environment variables are not set.")

        connection_string = f"mongodb+srv://{mongo_db_user}:{mongo_db_password}@{mongo_db_base_uri}/{mongo_db_name}?retryWrites=true&w=majority&appName={mongo_db_cluster_name}"

        # Create a new client and connect to the server
        client = AsyncMongoClient(connection_string)

        return client

    except ConnectionFailure as e:
        print(f"❌ ConnectionError in create_mongodb_instance: {str(e)}")

    return None


# pylint: disable=W0105
"""
Notes:

Refactored MongoDB using pymongo to avoid Motor deprecation issues.

Links:
 - https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/
 - https://pymongo.readthedocs.io/en/4.13.0/tutorial.html
"""
