"""
Access to VoxelBrain.

https://nip.humanbrainproject.eu/documentation/user-manual.html#voxel-brain
"""

import os
import requests


API_ROOT = "http://nip.humanbrainproject.eu/api/analytics/atlas"


def fetch_nrrd(atlas_id, layer, filepath):
    """ Fetch NRRD with layer data for given atlas. """
    url = API_ROOT + "/download?uri={0}/{1}/{1}.nrrd".format(atlas_id, layer)
    resp = requests.get(url)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(resp.content)


def get_file_path(atlas_id, layer, output_dir, overwrite=False):
    """ Fetch NRRD with layer data if necessary, return local file path. """
    filename = "{0}-{1}.nrrd".format(atlas_id, layer)
    filepath = os.path.join(output_dir, filename)
    if overwrite or not os.path.exists(filepath):
        tmp_filepath = filepath + ".download"
        try:
            fetch_nrrd(atlas_id, layer, tmp_filepath)
            os.rename(tmp_filepath, filepath)
        finally:
            try:
                os.unlink(tmp_filepath)
            except OSError:
                pass
    return filepath
