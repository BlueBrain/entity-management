"""
Access to VoxelBrain.

https://nip.humanbrainproject.eu/documentation/user-manual.html#voxel-brain
"""

import os
import requests


API_ROOT = "http://nip.humanbrainproject.eu/api/analytics/atlas"


def download_file(url, filepath, overwrite):
    """ Download file from `url` if it is missing. """
    if os.path.exists(filepath) and not overwrite:
        return filepath

    tmp_filepath = filepath + ".download"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(tmp_filepath, "wb") as f:
            f.write(resp.content)
        os.rename(tmp_filepath, filepath)
    finally:
        try:
            os.unlink(tmp_filepath)
        except OSError:
            pass

    return filepath


def fetch_data(atlas_id, layer, output_dir, overwrite=False):
    """ Fetch NRRD with `layer` data for given `atlas_id`. """
    params = {
        'atlas_id': atlas_id,
        'layer': layer
    }
    url = API_ROOT + "/download?uri={atlas_id}/{layer}/{layer}.nrrd".format(**params)
    filepath = os.path.join(output_dir, "{atlas_id}-{layer}.nrrd".format(**params))
    return download_file(url, filepath, overwrite=overwrite)


def fetch_hierarchy(atlas_id, output_dir, overwrite=False):
    """ Fetch JSON with brain region hierarchy for given `atlas_id`. """
    params = {
        'atlas_id': atlas_id,
    }
    url = API_ROOT + "/releases/{atlas_id}/filters/brain_region/65535".format(**params)
    filepath = os.path.join(output_dir, "{atlas_id}.json".format(**params))
    return download_file(url, filepath, overwrite=overwrite)
