from pymongo import MongoClient, DESCENDING, ASCENDING
from django.conf import settings
import uuid
import mongomock

class MongoRepositoryManager:

    def __init__(self, dbName, collectionName):
        self.dbName = dbName
        self.collectionName = collectionName
        self.repository = self._get_repository()

    def select(self, filter, sort=None):
        return self.repository.select(filter, sort)

    def select_list(self, filter=None, sort=None):
        return self.repository.select_list(filter, sort)

    def select_and_delete(self, filter={}, sort=None):
        return self.repository.select_and_delete(filter, sort)

    def insert(self, document):
        return self.repository.insert(document)

    def update(self, id, update):
        return self.repository.update(id, update)

    def delete(self, id):
        return self.repository.delete(id)

    def count(self, filter):
        return self.repository.count(filter)

    def _get_repository(self):
        if settings.MONGO_REPOSITORY_URL is None:
            print("MONGO_REPOSITORY_URL が指定されていないため、MockMongoRepository を使用します。データは永続化されません。")
            return MockMongoRepository(self.collectionName)
        else:
            return MongoRepository(self.dbName, self.collectionName)


class MongoRepository:

    def __init__(self, dbName, collectionName):
        self.client = MongoClient(
            settings.MONGO_REPOSITORY_URL, 27017)
        self.db = self.client[dbName]
        self.collection = self.db.get_collection(collectionName)

    def select(self, filter, sort=None):
        return self.collection.find_one(filter=filter, sort=sort)

    def select_list(self, filter=None, sort=None):
        return self.collection.find(filter=filter, sort=sort)

    def select_and_delete(self, filter={}, sort=None):
        return self.collection.find_one_and_delete(filter=filter, sort=sort)

    def insert(self, document):
        document['id'] = str(uuid.uuid4())
        self.collection.insert_one(document)
        return document['id']

    def update(self, id, update):
        filter = {'id': id}
        return self.collection.update_one(filter=filter, update={'$set': update}, upsert=True)

    def delete(self, id):
        filter = {'id': id}
        return self.collection.delete_one(filter)

    def count(self, filter):
        return self.collection.count_documents(filter)

class MockMongoRepository:

    def __init__(self, collectionName):
        self.db = mongomock.MongoClient().db
        self.collection = self.db.get_collection(collectionName)


    def select(self, filter, sort=None):
        return self.collection.find_one(filter=filter, sort=sort)

    def select_list(self, filter=None, sort=None):
        return self.collection.find(filter=filter, sort=sort)

    def select_and_delete(self, filter={}, sort=None):
        return self.collection.find_one_and_delete(filter=filter, sort=sort)

    def insert(self, document):
        document['id'] = str(uuid.uuid4())
        self.collection.insert_one(document)
        return document['id']

    def update(self, id, update):
        filter = {'id': id}
        return self.collection.update_one(filter=filter, update={'$set': update}, upsert=True)

    def delete(self, id):
        filter = {'id': id}
        return self.collection.delete_one(filter)

    def count(self, filter):
        return self.collection.count_documents(filter)