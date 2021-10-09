import time
from elasticsearch import Elasticsearch, helpers
import warnings
warnings.filterwarnings('ignore')

es_remote = Elasticsearch(['10.127.122.198'], 
                   port = 60500,
                   verify_certs = False,
                   use_ssl = True)

if not es_remote.ping():
    print("Cannot connect to Elastic")
    
es_local = Elasticsearch()

if not es_local.ping():
    print("Cannot connect to Elastic")
    
def bulk_baseline_data(index, mlist):
    for m in mlist:
    # use a `yield` generator so that the data
    # isn't loaded into memory
        yield {
            "_index": index,
            "_source": m,
        }
        
def main():
    es_doc_list = []
    start = time.time()
    while True:
        thread_pool_data = es_remote.cat.thread_pool(format = 'json')
        search_pool_info = thread_pool_data[13]
        write_pool_info = thread_pool_data[19]

        jvm_data = es_remote.nodes.stats(metric = ["jvm"])
        node = list(jvm_data["nodes"].keys())[0]
        jvm_mem_info = jvm_data["nodes"][node]["jvm"]["mem"]

        es_doc = {
            "timestamp": time.time(),
            "search_active": search_pool_info['active'],
            "search_queue": search_pool_info['queue'],
            "search_rejected": search_pool_info['rejected'],
            "write_active": write_pool_info['active'],
            "write_queue": write_pool_info['queue'],
            "write_rejected": write_pool_info['rejected'],
            "heap_used_percentage": jvm_mem_info['heap_used_percent']
        }

        es_doc_list.append(es_doc.copy())
#         time.sleep(1)
        if len(es_doc_list) >= 100:
            response = helpers.bulk(es_local, bulk_baseline_data('health_monitoring', es_doc_list))
            es_doc_list.clear()
            print("Pushed {} records to elastic db for a time duration of  {} seconds".format(response[0], time.time()-start))
            start = time.time()
        
if __name__ == "__main__":
    main()
        