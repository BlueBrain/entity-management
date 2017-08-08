#!/usr/bin/env python
'''simple app for interacting with entity source'''

import argparse
import logging
import urlparse

from pprint import pprint

from entity_management import client
from entity_management.entity import ENTITY_TYPES


def split_values(values):
    '''create dictionary w/ key/values based on key=value pairs'''
    return dict(arg.split('=') for arg in values)


def get_parser():
    '''return the argument parser'''
    types = [None] + sorted(ENTITY_TYPES.keys())

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', dest='verbose',
                        default=0, help='-v for INFO, -vv for DEBUG')

    subparsers = parser.add_subparsers(dest='action')

    get = subparsers.add_parser('get',
                                help='get by url')
    get.add_argument('url')

    query = subparsers.add_parser('query',
                                  help='Query graph')
    query.add_argument('--type', '-t', default=None, choices=types,
                       help='Type of entity')
    query.add_argument('predicates', nargs='*')

    register = subparsers.add_parser('register',
                                     help='Register')
    register.add_argument('--type', '-t', default=None, choices=types,
                          help='Type of entity')
    register.add_argument('properties', nargs='+')

    return parser


def main(args):
    '''main'''
    logging.basicConfig(level=(logging.WARNING,
                               logging.INFO,
                               logging.DEBUG)[min(args.verbose, 2)])

    if args.action == 'query':
        query = split_values(args.predicates)
        entities = client.get_entities(args.type, query)
        pprint(entities)
    elif args.action == 'register':
        properties = split_values(args.properties)
        id_ = client.register_entity(args.type, properties)
        print id_
    elif args.action == 'get':
        url = urlparse.urlparse(args.url)
        type_, id_ = url.path[1:].split('/')
        entity = client.get_entity(type_, id_)
        pprint(entity)


if __name__ == '__main__':
    PARSER = get_parser()
    main(PARSER.parse_args())
