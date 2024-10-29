# pylint: disable=missing-docstring,no-member
import json

from pytest_httpx import IteratorStream

from entity_management_async.core import Entity
from entity_management_async.morphology import ReconstructedPatchedCell
from entity_management_async.settings import DASH, NSG
from entity_management_async.state import get_base_url
from entity_management_async.util import quote
from tests._async.test_nexus import FILE_ID, FILE_NAME_EXT, FILE_RESPONSE, FILE_URL

CELL_NAME = "mycell"
CELL_ID = NSG[CELL_NAME]

IMAGE_NAME = "myimage"
IMAGE_ID = NSG[IMAGE_NAME]

CELL_RESPONSE = {
    "@context": [
        "https://bluebrain.github.io/nexus/contexts/search.json",
        "https://bluebrain.github.io/nexus/contexts/metadata.json",
    ],
    "@id": CELL_ID,
    "@type": ["ReconstructedPatchedCell", "Entity"],
    "_constrainedBy": "nsg:dash/reconstructedpatchedcell",
    "_createdAt": "2019-04-26T15:30:21.011Z",
    "_createdBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
    "_deprecated": False,
    "_project": "https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj",
    "_rev": 1,
    "_self": "https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/_/%s" % quote(CELL_ID),
    "_updatedAt": "2019-04-26T15:30:21.011Z",
    "_updatedBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
    "brainLocation": {
        "brainRegion": {
            "@id": "http://uri.interlex.org/paxinos/uris/rat/labels/1017",
            "label": "ventral posterolateral thalamic nucleus",
        }
    },
    "distribution": {
        "@type": "DataDownload",
        "contentSize": {"unitCode": "bytes", "value": 397841},
        "contentUrl": FILE_URL,
        "digest": {
            "algorithm": "SHA-256",
            "value": "1123f4816beea40352612374a1ac5b8bf4fa515a2f98af9793c6f83d2c8080d6",
        },
        "encodingFormat": "application/octet-stream",
        "name": "morphology_file_name.asc",
    },
    "wasDerivedFrom": [
        {
            "@id": IMAGE_ID,  # link to core.Entity to test that type can be recovered.
            "@type": "Entity",
        }
    ],
    "mType": {
        "@id": "http://uri.interlex.org/base/ilx_0738236",
        "label": "VPL_TC",
        "prefLabel": "VPL_TC",
    },
    "name": "cell_name",
}

IMAGE_RESPOSE = {
    "@context": [
        "https://bluebrain.github.io/nexus/contexts/search.json",
        "https://bluebrain.github.io/nexus/contexts/metadata.json",
    ],
    "@id": IMAGE_ID,
    "@type": "Entity",
    "_constrainedBy": "nsg:dash/entity",
    "_createdAt": "2019-05-08T14:03:10.196Z",
    "_createdBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
    "_deprecated": False,
    "_project": "https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj",
    "_rev": 1,
    "_self": "https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/datashapes:entity/%s"
    % IMAGE_NAME,
    "_updatedAt": "2019-05-08T14:03:10.196Z",
    "_updatedBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
    "distribution": {
        "@type": "DataDownload",
        "contentSize": {"unitCode": "bytes", "value": 397841},
        "contentUrl": FILE_ID,
        "digest": {
            "algorithm": "SHA-256",
            "value": "1123f4816beea40352612374a1ac5b8bf4fa515a2f98af9793c6f83d2c8080d6",
        },
        "encodingFormat": "application/octet-stream",
        "name": FILE_NAME_EXT,
    },
    "name": IMAGE_NAME,
}


CELL_LIST_RESPONSE = {
    "@context": [
        "https://bluebrain.github.io/nexus/contexts/search.json",
        "https://bluebrain.github.io/nexus/contexts/metadata.json",
    ],
    "_results": [
        {
            "@id": CELL_ID,
            "@type": [
                "https://neuroshapes.org/ReconstructedPatchedCell",
                "http://www.w3.org/ns/prov#Entity",
            ],
            "_constrainedBy": "https://neuroshapes.org/dash/reconstructedpatchedcell",
            "_createdAt": "2019-04-26T15:29:33.141Z",
            "_createdBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
            "_deprecated": False,
            "_project": "https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj",
            "_rev": 1,
            "_self": "https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/"
            "%s/%s" % (quote(DASH.reconstructedpatchedcell), quote(CELL_ID)),
            "_updatedAt": "2019-04-26T15:29:33.141Z",
            "_updatedBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
        }
    ],
    "_total": 1,
}


async def test_reconstructed_patched_cell(tmp_path, httpx_mock):
    stream = json.dumps(FILE_RESPONSE).encode("utf-8")
    httpx_mock.add_response(
        stream=IteratorStream([stream[: len(stream) // 2], stream[len(stream) // 2 :]]),
        method="GET",
        url=f"{FILE_URL}?tag=&rev=",
        headers={"Content-Disposition": 'attachment; filename="=?UTF-8?B?bXlmaWxlLmpwZw==?="'},
    )

    httpx_mock.add_response(  # mock patched cell listing response
        method="GET",
        url=f"{ReconstructedPatchedCell.get_constrained_url()}?from=0&size=50&deprecated=false",
        json=CELL_LIST_RESPONSE,
    )

    httpx_mock.add_response(  # mock patched cell detailed response
        method="GET",
        url=f"{get_base_url(cross_bucket=True)}/{quote(CELL_ID)}",
        json=CELL_RESPONSE,
    )

    cells = ReconstructedPatchedCell.list_by_schema()
    cell = await cells.__anext__()
    cell = await cell

    assert cell.name == "cell_name"
    assert isinstance(cell.wasDerivedFrom[0], Entity)

    file_path = await cell.distribution[0].download(path=str(tmp_path))

    expected_path = tmp_path / FILE_NAME_EXT
    assert file_path == str(expected_path)
    assert expected_path.is_file() is True
    assert expected_path.read_bytes() == stream
