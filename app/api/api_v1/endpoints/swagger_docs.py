from typing import Any, List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from fastapi.responses import JSONResponse, ORJSONResponse

import json
from fastapi.encoders import jsonable_encoder

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

import sys

router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=router.openapi_url,
        title=router.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )
