import logging
import os
from os import getcwd
import hashlib
from fastapi.responses import FileResponse, Response
from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from app.core import Config

router = APIRouter(prefix="/opa", tags=["opa"])
logger = Config.setup_logging()


@router.get("/rules")
async def get_opa_bundle_file(request: Request):
    file_path = getcwd() + "/app/opa/bundle.tar.gz"
    if not os.path.exists(file_path):
        logger.error(f'Error when retrieving OPA bundle file.',
                     exc_info=ValueError(status.HTTP_404_NOT_FOUND))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Read the file's content
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Calculate the ETag based on the file content
    etag = hashlib.md5(file_content).hexdigest()

    # Check if the client's If-None-Match header matches the current ETag
    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304)

    response_headers = {"ETag": etag}
    return FileResponse(path=file_path, headers=response_headers)
