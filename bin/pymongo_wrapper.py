import pymongo
from pymongo import MongoClient

class TinyMongoCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._cursor)

    def sort(self, key_or_list, direction=None):
        if direction is None:
            direction = pymongo.ASCENDING
        elif direction == -1:
            direction = pymongo.DESCENDING
        self._cursor = self._cursor.sort(key_or_list, direction)
        return self

    def limit(self, limit):
        self._cursor = self._cursor.limit(limit)
        return self

    def count(self):
        return self._cursor.count()

class TinyMongoCollection:
    def __init__(self, collection):
        self._collection = collection

    def find(self, filter=None):
        cursor = self._collection.find(filter)
        return TinyMongoCursor(cursor)

    def find_one(self, filter=None):
        return self._collection.find_one(filter)

    def insert_one(self, document):
        return self._collection.insert_one(document)

    def insert_many(self, documents):
        return self._collection.insert_many(documents)

    def delete_one(self, filter):
        return self._collection.delete_one(filter)

    def delete_many(self, filter):
        return self._collection.delete_many(filter)

    def update_one(self, filter, update):
        return self._collection.update_one(filter, update)

    def update_many(self, filter, update):
        return self._collection.update_many(filter, update)

    def count_documents(self, filter=None):
        return self._collection.count_documents(filter)

class TinyMongoClient:
    def __init__(self, uri):
        self._client = MongoClient(uri)

    def __getattr__(self, name):
        return TinyMongoCollection(self._client[name])

    def close(self):
        self._client.close()

