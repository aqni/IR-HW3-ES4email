
import os
import re

from elasticsearch import Elasticsearch, helpers
from typing import AsyncIterable, Iterable
from email import message
from email.parser import Parser
import dateutil
import datetime
from tqdm import tqdm
from bigram_spam_classifier import spamclassifier

class MailIndex:
    mappings = {
        "properties": {
            "Message-ID": {"type": "keyword"},
            "date": {
                "type": "date",
                "format": "strict_date_optional_time",
            },
            "from": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "keyword",
                    },
                    "address": {
                        "type": "keyword",
                    },
                }
            },
            "to": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "keyword",
                    },
                    "address": {
                        "type": "keyword",
                    },
                }
            },
            "flie": {"type": "keyword", },
            "subject": {"type": "text", },
            "length": {"type": "integer", },
            "body": {
                "type": "text",
                "analyzer": "english"
            },
        }
    }

    def __init__(self,client:Elasticsearch,index_name:str,doc_type:str):
        self.client=client
        self.indexName=index_name
        self.docType=doc_type
        self.batch=[]
    
    def reCreateIndex(self):
        if self.client.indices.exists(index=self.indexName):
            print(self.client.indices.delete(index=self.indexName))
        mappings={self.docType:MailIndex.mappings}
        print(self.client.indices.create(index=self.indexName, mappings=MailIndex.mappings))
    
    def indexDocs(self,batch:Iterable,flush:bool=True):
        helpers.bulk(self.client,batch,index=self.indexName)
    
    filePattern = re.compile("\ -\ [\w\-\ ]*(\.[\w\-]+)+")
    @staticmethod
    def mailAddAction(email: message) -> dict:
        body = email.get_payload()
        return {
            "Message-ID": email["Message-ID"].strip('<|>'),
            "date": dateutil.parser.parse(email["Date"]).isoformat(),
            "from.name": email["X-From"],
            "from.address": email["From"],
            "to.name": [x[0:x.find('<')].strip() for x in (email["X-To"].split(', ') if email["X-To"] else [])],
            "to.address": [x.strip() for x in (email["To"].split(', ') if email["To"] else [])],
            "flie": [x.group()[3:] for x in MailIndex.filePattern.finditer(body)],
            "subject": email["Subject"],
            "length": len(body),
            "body": body,
        }

path = 'C:/Users/A/source/vscode/InformationRetrieval/hw3/maildir/'
indexName = 'mail_map'
docType="mail_doc"

if __name__ == '__main__':
    es = Elasticsearch()
    mi=MailIndex(es,indexName,docType)
    mi.reCreateIndex()
    filenames=[os.path.join(dir, f) for dir, _, fs in os.walk(path) for f in fs]
    batch=[]
    for fn in tqdm(filenames):
        with open(fn, "r",encoding='windows-1252') as f:
            e = Parser().parse(f)
            action = MailIndex.mailAddAction(e)
            batch.append(action)
        if(len(batch)>=500):
            mi.indexDocs(batch)
            batch=[]
    mi.indexDocs(batch)

