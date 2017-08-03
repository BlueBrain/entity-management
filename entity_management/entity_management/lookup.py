"""enties for URL interpretation. """

import urlparse


def get_file_path(url):
    """ Get locally available file path from URL. """
    scheme, netloc, path = urlparse.urlsplit(url)[:3]
    if scheme in ('file', ''):
        assert(not netloc)
        result = path
    elif scheme == 'fakenexus':
        from entity_management import fakenexus
        result = fakenexus.get_file_path(url)
    else:
        raise Exception("Unexpected URL scheme: '%s'" % scheme)
    return result
