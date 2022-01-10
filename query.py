from build_indexes import indexName, docType
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


class MailSearch(Elasticsearch):
    def __init__(self,index:str):
        super().__init__()
        self.indexName=index

    def searchMail(self,query:dict):
        return self.search(index=indexName, query=query)
    


if __name__ == '__main__':
    search=MailSearch(indexName)
    query = {
        "bool": {
            "must":[],
            "must_not":[],
            "should": []
        }
    }
    a=search.searchMail(query)
    
