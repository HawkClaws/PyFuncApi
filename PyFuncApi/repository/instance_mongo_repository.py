from .mongo_repository import MongoRepositoryManager

batch_task_repository = None
async_data_mongo_repository = None
api_data_repository = None

def get_batch_task_repository():
    global batch_task_repository
    if batch_task_repository is None:
        batch_task_repository = MongoRepositoryManager("pyfuncapi", "batch_task")
    return batch_task_repository

def get_async_data_repository():
    global async_data_mongo_repository
    if async_data_mongo_repository is None:
        async_data_mongo_repository = MongoRepositoryManager("pyfuncapi", "async_result")
    return async_data_mongo_repository

def get_api_data_repository():
    global api_data_repository
    if api_data_repository is None:
        api_data_repository = MongoRepositoryManager("pyfuncapi", "api_data")
    return api_data_repository