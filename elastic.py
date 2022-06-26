import time
from elasticsearch import Elasticsearch, helpers
import pandas as pd
    
es_local = Elasticsearch()

if not es_local.ping():
    print("Cannot connect to local Elastic")
    
def bulk_baseline_data(index, mlist):
    for m in mlist:
    # use a `yield` generator so that the data
    # isn't loaded into memory
        yield {
            "_index": index,
            "_source": m,
        }
        
def elastic_health_monitoring(host, port):
    es_doc_list = []
    start = time.time()

    # esdb_url = "http://{}:{}".format(args.host, args.port)
    es_remote = Elasticsearch([{"host": host, "port": port}])
    if not es_remote.ping():
        print("Cannot connect to remote Elastic")
    while True:
        thread_pool_data = es_remote.cat.thread_pool(format = 'json')
        df = pd.DataFrame(thread_pool_data)

        df = df.loc[df.name.isin(['search', 'write'])]

        search_pool_info = df.loc[df.name == 'search'].to_records(index=False)[0]
        write_pool_info = df.loc[df.name == 'write'].to_records(index=False)[0]

        jvm_data = es_remote.nodes.stats(metric = ["jvm"])
        node = list(jvm_data["nodes"].keys())[0]
        jvm_mem_info = jvm_data["nodes"][node]["jvm"]["mem"]

        es_doc = {
            "timestamp": int(time.time()*1000),
            "search_active": search_pool_info['active'],
            "search_queue": search_pool_info['queue'],
            "search_rejected": search_pool_info['rejected'],
            "write_active": write_pool_info['active'],
            "write_queue": write_pool_info['queue'],
            "write_rejected": write_pool_info['rejected'],
            "heap_used_percentage": jvm_mem_info['heap_used_percent']
        }
        # print(es_doc)

        es_doc_list.append(es_doc.copy())

        if len(es_doc_list) >= 20:
            response = helpers.bulk(es_local, bulk_baseline_data('health_monitoring', es_doc_list))
            es_doc_list.clear()
            print("Pushed {} records to elastic db for a time duration of  {} seconds".format(response[0], time.time()-start))
            start = time.time()