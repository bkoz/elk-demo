#!/usr/bin/env python
# coding: utf-8

"""
Example Elastic client using requests.
"""

import argparse
import requests

def get_health(session: requests.sessions.Session, host: str, port: str, verify: bool):
    """
    get_health
    """
    url = f'{host}:{port}'
    r = session.get(url, verify=verify)
    print(r.content.decode())

    url = f'{url}/_cat/health'
    r = session.get(url, verify=verify)
    print(r.content.decode())

def create_index(session: requests.Session, host: str, port: str, verify: bool):
    """
    create_index - Create and read a simple index.
    """

    url = f'{host}:{port}/customer/_doc/0'
    payload = {"firstname": "Bob", "lastname": "Koz"}
    r = session.put(url, verify=verify, json=payload)
    print(r.content.decode())

    r = session.get(url, verify=verify)
    print(r.content.decode())

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
    
    parser.add_argument('-i', '--verify', action='store_true', default=False)
    args = parser.parse_args()
    
    print(f'host = {args.host}, port = {args.port}, user = {args.user}, password = {args.password}, verify = {args.verify}')

    session = requests.Session()
    session.auth = (args.user, args.password)
 
    get_health(session, args.host, args.port, args.verify)
    create_index(session, args.host, args.port, args.verify)
