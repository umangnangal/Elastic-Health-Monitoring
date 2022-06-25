from elasticsearch import Elasticsearch
import json
import warnings
warnings.filterwarnings('ignore')

es_local = Elasticsearch()

if not es_local.ping():
    print("Cannot connect to Elastic")

with open('health.json') as f:
    body = json.load(f)

if es_local.indices.exists('health_monitoring'):
    print("Index 'health_monitoring' already present. Deleting it !")
    es_local.indices.delete('health_monitoring')
    
print("Creating new index : 'health_monitoring'")
es_local.indices.create(index='health_monitoring', body=body)
print("New index 'health_monitoring' created successfully.")