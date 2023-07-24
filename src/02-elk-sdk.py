#!/usr/bin/env python
# coding: utf-8

"""
Example Elastic client using the SDK.
"""

import subprocess
from datetime import datetime
from elasticsearch import Elasticsearch

#
# Get the Openshift route for Elastic.
#
COMMAND = "oc get routes elastic -o=jsonpath='{.spec.host}'"
HOST = subprocess.check_output(COMMAND, shell=True).decode()
PORT = '443'
VERIFY_CERTS = True
url = f'https://{HOST}:{PORT}'
ELASTIC_USER = 'elastic'

#
# Get the ELASTIC_PASSWORD for Elastic from Openshift.
#
COMMAND="oc get secrets elasticsearch-sample-es-elastic-user \
    -o=jsonpath='{.data.elastic}' | base64 --decode"
ELASTIC_PASSWORD = subprocess.check_output(COMMAND, shell=True).decode()

print(f'url = {url}')
es = Elasticsearch(url, verify_certs=VERIFY_CERTS, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))

# ##### GET the Elastic health
print(es.health_report())

# GET the Elastic status.
es.info()

# POST some example data.

#
# To index a document, three pieces of information are required: index, id, and a body
#
doc = {
    'author': 'author_name',
    'text': 'Interesting content...',
    'timestamp': datetime.now(),
}
resp = es.index(index="test-index", id=1, document=doc)
print(resp['result'])

# GET the example back.

#
# To get a document, the index and id are required:
#
resp = es.get(index="test-index", id=1)
print(resp['_source'])

# Search

resp = es.search(index="test-index", query={"match_all": {}})
print("Got %d Hits:" % resp['hits']['total']['value'])
for hit in resp['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])