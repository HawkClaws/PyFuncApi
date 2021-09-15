import requests


class Repository:
    repository_url = ""

    def __init__(self, repository_url):
        self.repository_url = repository_url

    def select(self, repository_key, queryString=""):
        return requests.get(self.repository_url + repository_key + ".json" + queryString)

    def insert(self, repository_key, data):
        return requests.post(self.repository_url + repository_key + ".json", data=data.encode('utf-8'))

    def update(self, repository_key, data):
        return requests.patch(self.repository_url + repository_key + ".json", data=data.encode('utf-8'))

    def delete(self, repository_key):
        return requests.delete(self.repository_url + repository_key + ".json")
