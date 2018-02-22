#!/usr/bin/env python
'''simple app for interacting with entity source'''
# TODO consider rewriting this to use new nexus api
# or remove it completely
import argparse
import logging

from pprint import pprint

from entity_management import client
from entity_management.compat import urlparse, StringType
from entity_management.entity import ENTITY_TYPES


MAX_TEXT_WIDTH = 150


def _truncate(obj):
    '''strings that are too long are truncated to be easier to read on a terminal'''
    if isinstance(obj, dict):
        return {k: _truncate(v) for k, v in obj.items()}
    elif isinstance(obj, StringType):
        ret = str(obj)
        if MAX_TEXT_WIDTH < len(ret):
            ret = ret[:MAX_TEXT_WIDTH] + '...'
        return ret
    else:
        return obj


def split_values(values):
    '''create dictionary w/ key/values based on key=value pairs'''
    return dict(arg.split('=') for arg in values)


def get_parser():
    '''return the argument parser'''
    types = [None] + sorted(ENTITY_TYPES.keys())

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', dest='verbose', default=0,
                        help='-v for INFO, -vv for DEBUG')

    subparsers = parser.add_subparsers(dest='action')

    get = subparsers.add_parser('get',
                                help='get by url')
    get.add_argument('url')

    query = subparsers.add_parser('query',
                                  help='Query graph')
    query.add_argument('--type', '-t', default='entities', choices=types,
                       help='Type of entity')
    query.add_argument('predicates', nargs='*')

    register = subparsers.add_parser('register',
                                     help='Register')
    register.add_argument('--type', '-t', default='entities', choices=types,
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
        entities = [_truncate(entity) for entity in client.get_entities(args.type, query)]
        pprint(entities)
    elif args.action == 'register':
        properties = split_values(args.properties)
        id_ = client.register_entity(args.type, properties)
        print(id_)
    elif args.action == 'get':
        url = urlparse(args.url)
        if url.netloc in ENTITY_TYPES:
            type_, id_ = url.netloc, url.path[1:]
        else:
            type_, id_ = url.path[1:].split('/')
        entity = _truncate(client.get_entity(type_, id_))
        pprint(entity)


if __name__ == '__main__':
    PARSER = get_parser()
    main(PARSER.parse_args())
