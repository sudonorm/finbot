#!/bin/bash
### The lsof argument below can be used to forcefully close open ports in a Unix environment
## lsof -ti :8282 | xargs --no-run-if-empty kill -9
### Use Uvicorn in development or on Windows
uvicorn app.main:app --host 127.0.0.1 --port 8282 --timeout-keep-alive 0 --reload
### Use Gunicorn in production. On Linux, make sure 0.0.0.0 does not expose port 8282 to the internet. In the very least, make sure incoming communication with the port is blocked in the firewall.
### The docker-compose.yml is setup to restrict communication to localhost only
# gunicorn app.main:app --bind 0.0.0.0:8282 -w 1 -k uvicorn.workers.UvicornWorker --timeout 600
