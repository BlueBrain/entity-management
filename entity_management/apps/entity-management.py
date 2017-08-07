#!/usr/bin/env python
'''simple app for interacting with entity source'''

import argparse
import logging

from entity_management import fakenexus


def split_query(queries):
    '''create dictionary w/ key/values based on key=value pairs'''
    return dict(arg.split('=') for arg in queries)


def get_parser():
    '''return the argument parser'''
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', dest='verbose',
                        default=0, help='-v for INFO, -vv for DEBUG')

    parser.add_argument('query', nargs='*')

    return parser


def main(args):
    '''main'''
    logging.basicConfig(level=(logging.WARNING,
                               logging.INFO,
                               logging.DEBUG)[min(args.verbose, 2)])

    query = split_query(args.query)
    entities = fakenexus.list_entites(query)

    from pprint import pprint
    pprint(entities)


if __name__ == '__main__':
    PARSER = get_parser()
    main(PARSER.parse_args())
