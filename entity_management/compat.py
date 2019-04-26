'''Compat for python2/3'''
# pylint: disable=import-error,unused-import

from six.moves import filter as filter_


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
