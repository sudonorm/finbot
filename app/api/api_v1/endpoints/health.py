from typing import Any, List, Union, Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from fastapi.responses import JSONResponse, ORJSONResponse

from fastapi.encoders import jsonable_encoder

import time
import re
import ast
import json

from chat.src.utils.async_utils import async_retry

from random import choice
from langchain_core.messages import HumanMessage
from chat.src.agents import graph_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

import sys
import os
from pydantic import BaseModel
import uuid

home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
home_dir_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

if home_dir not in sys.path:
    sys.path.append(home_dir)
if home_dir_parent not in sys.path:
    sys.path.append(home_dir_parent)

from core.config import settings
from core import security


router = APIRouter()


@router.get(
    "", include_in_schema=False
)  ### exception added to guide agianst the 307 redirect error on cloud servers
@router.get(
    "/",
)
async def health_check(
    # token: Annotated[str, Depends(security.JWTBearer())], ###TODO: uncomment this in production to ensure this endpoint cannot be used without Auth. Please set the SECRET_KEY in the .env file and use it to create a token
):
    return {"status": "ok"}
