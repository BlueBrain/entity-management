'''compat for python2/3'''
import sys

#F0401: 'Unable to import module'
# pylint: disable=no-name-in-module,unused-import,F0401
if sys.version_info < (3, 0):
    StringType = (str, unicode)   # pragma: no cover
else:
    StringType = str  # pragma: no cover

try:
    from urllib.parse import urlparse, urlsplit, urlunsplit  # pragma: no cover
except ImportError:  # pragma: no cover
    from urlparse import urlparse, urlsplit, urlunsplit  # pragma: no cover
