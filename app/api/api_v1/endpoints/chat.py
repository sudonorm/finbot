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

stm = "/app/api"
dbstm = "/chat/src/chat_dbs/"
db_directory = f"{home_dir_parent.replace(stm, dbstm)}"

router = APIRouter()


@async_retry(max_retries=5, delay=2)
async def invoke_agent_with_retry(
    question_str: str, unique_id: str = "61aaa70565-bdb1-444d-8680-60d0984b2513"
):
    """Retry the agent if a tool fails to run.

    This can help when there are intermittent connection issues
    to external LLM APIs.
    """

    config = {"configurable": {"thread_id": unique_id}}
    sqlite3_conn = sqlite3.connect(
        f"{db_directory}{unique_id}.sqlite", check_same_thread=False
    )
    checkpointer = SqliteSaver(sqlite3_conn)

    graph = graph_react_agent.workflow.compile(checkpointer=checkpointer)

    return graph.invoke(
        {"messages": [HumanMessage(content=question_str)]},
        config=config,
    )


class ChatInput(BaseModel):
    question: str = None
    response_bdy: dict | None = None
    language: str = None


@router.post(
    "", include_in_schema=False
)  ### exception added to guide agianst the 307 redirect error on cloud servers
@router.post(
    "/",
)
async def chat_bot(
    # token: Annotated[str, Depends(security.JWTBearer())], ###TODO: uncomment this in production to ensure this endpoint cannot be used without Auth. Please set the SECRET_KEY in the .env file and use it to create a token
    chat_input: ChatInput,
) -> Response:
    """
    Chat with Fin bot
    """

    question_str = chat_input.question

    if len(chat_input.response_bdy) > 0 and "session_uuid" in list(
        chat_input.response_bdy.keys()
    ):
        session_uuid = chat_input.response_bdy.get("session_uuid")
        # print("uuid found", session_uuid)
    else:
        session_uuid = str(uuid.uuid4())
        chat_input.response_bdy.update({"session_uuid": session_uuid})

    graph = None

    try:

        agent_response = await invoke_agent_with_retry(
            question_str=question_str, unique_id=session_uuid
        )

    except:

        chat_input.response_bdy.update(
            {
                "response": f'{"I am unfortunately unable to answer your question - "}{question_str}{" - please rephrase your question and try again."}'
            }
        )
        chat_input.response_bdy.update(
            {
                "no_tool_available": [
                    {
                        f"{'no_tool'}_question": question_str,
                        f"{'no_tool'}_answer": f'{"I am unfortunately unable to answer your question - "}{question_str}{" - please rephrase your question and try again."}',
                    }
                ]
            }
        )

        output_response = {
            "content": chat_input.response_bdy,
            "page": {
                "size": 1,
                "totalElements": 1,
                "totalPages": 1,
            },
        }

        return ORJSONResponse(content=output_response)

    response_str = agent_response.get("answer")

    if response_str not in [None, ""] and len(agent_response.get("messages")) > 0:

        chat_input.response_bdy.update({"response": response_str})

    else:

        chat_input.response_bdy.update(
            {
                "response": f'{"I am unfortunately unable to answer your question - "}{question_str}{" - please rephrase your question and try again."}'
            }
        )
        chat_input.response_bdy.update(
            {
                "no_tool_available": [
                    {
                        f"{'no_tool'}_question": question_str,
                        f"{'no_tool'}_answer": f'{"I am unfortunately unable to answer your question - "}{question_str}{" - please rephrase your question and try again."}',
                    }
                ]
            }
        )

    output_response = {
        "content": chat_input.response_bdy,
        "page": {
            "size": 1,
            "totalElements": 1,
            "totalPages": 1,
        },
    }

    return ORJSONResponse(content=output_response)
