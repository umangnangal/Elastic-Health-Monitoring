import argparse
from elastic import elastic_health_monitoring
from postgres import postgres_health_monitring
        
def main(args):
    if args.driver == 'elasticsearch':
        elastic_health_monitoring(args.host, args.port)
    elif args.driver == 'postgres':
        postgres_health_monitring()
    else: # keep on adding more checks here as the project grows
        pass
        

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Elasticsearch Health Monitoring
elastic_parser = subparsers.add_parser('elasticsearch')
elastic_parser.add_argument("--host", default="127.0.0.1")
elastic_parser.add_argument("--port", default="9200")
elastic_parser.add_argument("--verify_certs", default=False)
elastic_parser.add_argument("--use_ssl", default=False)
elastic_parser.set_defaults(driver='elasticsearch')

# PostgreSQL Health Monitoring
postgres_parser = subparsers.add_parser('postgres')
postgres_parser.add_argument("--host", default="127.0.0.1")
postgres_parser.add_argument("--port", default="5432")
postgres_parser.set_defaults(driver='postgres')

if __name__ == "__main__":
    args = parser.parse_args()
    print(args)

    main(args)
        