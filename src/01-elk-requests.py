#!/usr/bin/env python
# coding: utf-8

"""
Example Elastic client using requests.
"""

import requests
import json
import argparse

def get_health(session: requests.Session, url: str, port: str, verify: bool):
    """
    get_health
    """
    r = session.get(f'{url}:{port}/_cat/health', verify=verify)
    print(r.content.decode())
    r = session.get(f'{url}:{port}', verify=verify)
    print(r.content.decode())


# POST some example data.
# url = f'http://{service}:9200/customer/_doc/4'
# payload = {"firstname": "Bob", "lastname": "Koz"}
# r = session.put(url, verify=verify_certs, json=payload)
# print(r.content.decode())


# ##### GET the example back.
# url = f'http://{service}:9200/customer/_doc/4'
# r = session.get(url, verify=verify_certs)
# print(r.content.decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', metavar='host', nargs='?',
        default='https://localhost',
        help='Hostname of the ElasticSearch cluster'
        )
    parser.add_argument(
        '--port', metavar='port', nargs='?',
        default='9200',
        help='Port of the ElasticSearch cluster'
        )
    parser.add_argument(
        '--user', metavar='user', nargs='?',
        default='elastic',
        help='User for the ElasticSearch cluster'
        )
    parser.add_argument(
        '--password', metavar='password', nargs='?',
        default='elastic',
        help='Password for the ElasticSearch cluster'
        )
    #parser.add_argument(
    #    '--verify_certs', metavar='verify_certs', nargs='?',
    #    type=bool,
    #    default=True,
    #    action='store_true',
    #    help='Verify checking of SSL certs.'
    #    )
    parser.add_argument('-i', '--verify', action='store_true', default=False)

    args = parser.parse_args()
    # if args.verify_certs == "False": args.verify_certs = False
    print(f'host = {args.host}, port = {args.port}, user = {args.user}, password = {args.password}, verify = {args.verify}')


    # service = 'elasticsearch-sample-es-http.elastic'
    # user = 'elastic'
    # password = 'password'
    # verify_certs = False
    session = requests.Session()
    session.auth = (args.user, args.password)
    
    get_health(session, args.host, args.port, args.verify)
