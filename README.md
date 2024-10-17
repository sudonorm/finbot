# Say hello to FinBot...

A financial assistant which leverages LLMs to provide financial information to the best of its ability. FinBot is built using LangChain and LangGraph, and OpenAI's ChatGPT.

# Usage

The app consists of two parts: the backend FastAPI service which serves the bot and a simple frontend Streamlit app.

To get started, we need to:

- Make a copy of the `.env.local` file which is in the root folder of this project
- <strong>Rename</strong> the `.env.local` to `.env`
- Fill out the necessary credentials (FinBot uses [FMP](https://site.financialmodelingprep.com/developer/docs) and [OpenAI](https://platform.openai.com/docs/concepts), so be sure to have API KEYs for those two services before proceeding)

## Local Development or running the app locally

After we have added the appropriate credentials to the `.env` file. We need to:

- Set up a virtual environment and install all the packages in the `requirements.txt` file. To be able to use `black` for formatting in a local dev env, install `requirements-dev.txt`

- Open a terminal/command line and with our virtual environment activated we need to run the backend service which serves FinBot using:

```shell
bash start.sh
```

The bot's backend endpoint should be visible at:

```
http://127.0.0.1:8282/docs
```

- We can also use the SwaggerUI to chat with the bot, but for a more smooth experience, we can run the Frontend Streamlit app in a new terminal/command line using:

```shell
streamlit run chat/src/frontend/main.py
```

The bot's frontend service should be visible at:

```
http://localhost:8501
```

Note: It might take a few seconds for the bot to respond if the question has a lot of context for it to parse.

## Testing FinBot in a production-like environment

Here, we will be using Docker, a Dockerfile, and a docker-compose.yml file.

Steps:

- Make sure the appropriate credentials are in the `.env` file.
- In the `.env` file, we need to make sure the correct `CHATBOT_URL` is used. To run the app in Docker, uncomment the second `CHATBOT_URL` and comment out the first one.
- To start the frontend and backend services, run the following from a terminal in the root folder and wait for the health check to pass (<strong>care should be taken when running Docker in a linux environment so no ports are exposed</strong>):

```shell
docker compose up -d
```

The Backend should be available at:

```text
http://finbot.localhost/docs
```

The Frontend should be available at:

```text
http://finbotfrontend.localhost/
```

Note: It might take a few seconds for the bot to respond if the question has a lot of context for it to parse.

# Limitations/improvements:

- Security

  - Endpoints should always be secured to avoid misuse.
  - Currently, authentication to use FinBot is not activated. To activate this, set the SECRET_KEY in the .env file, create a token using this secret key and uncomment the appropriate rows in `app/api/api_v1/endpoints/chat.py` and `app/api/api_v1/endpoints/health.py`

  - If Auth is enabled, the `Curl` command in the docker-compose.yml file will also need a header with a `Bearer` authorization containing the token.
  - Rate limiting should be enabled for endpoints to prevent DDOS attacks.

- Agent

  - OpenAI recently released [Swarm](https://github.com/openai/swarm) which, though still experimental, looks very promising for multi-agent orchestration. It should be trivial to swap out the current LangGraph agent used by FinBot for this logic. It might also perform better, but this is to be seen.

  - FinBot uses `gpt-4o-mini`. However, when `o1` is released for API usage, it should out-perform `gpt-4o-mini` in the various tasks FinBot does.

- News:

  - Searching for information on the internet takes a few seconds as we need to 1) find the relevant articles 2) extract the text from them, if available 3) chunk up the text and use these to answer the users question. FinBot uses duckduckgo to search for information on the internet.

  - We can optimize this section by 1) switching to a paid API service which curates searchable recent news articles and/or 2) running the operation to extract text from URLs in parallel rather than linearly.

- Company Metrics:

  - There are a lot more metrics that can be pulled from the FMP API and converted into tools. For now, FinBot sticks to the basics: company profile, executives, earnings calls. It can check the internet for anything else it needs.

- Bot Attention:

  - Because we checkpoint the conversation, FinBot remembers information it has seen in the past and passes this in as further context to reduce the need to requery the information, using a tool, when it has the answer in memory. This may not always be the desired behavior. In the case of FinBot, the messages passed in as extra context has been limited to the last 8. Further improvement on this would be to implement some form of State updating logic.

- Extra Tools:

  - FinBot is built using a tool-approach. Function-based tools can be added to this script (`chat/src/tools/bot_tools.py`) to extend the capability of FinBot.

- Persona:

  - FinBot currently does not have a persona. It would be nice for it to have some kind of persona or way of interacting with people. Even, maybe to introduce itself at the start of a conversation so the user is aware they are chatting with a bot, and are aware of its capabilities.

- Other LLMs:

  - For some of the tasks FinBot needs to do, other models should be tested to see if they are cheaper and faster.

- Unit tests and Integration tests
  - The docker-compose.yml implements an integration test to ensure the backend is healthy as the frontend depends on it. There's also a health endpoint which can be used to programatically check if the backend API is active. Further unit tests for the functions grabbing metrics and news need to be implemented.

# Disclaimer:

This project was created purely, and is intended only, for educational purposes and does not constitute financial advice of any sort. User discretion is advised.
