### The lsof argument below can be used to forcefully close open ports
#lsof -ti :8282 | xargs --no-run-if-empty kill -9
### Use Uvicorn in development
uvicorn app.main:app --host 0.0.0.0 --port 8282 --timeout-keep-alive 0 --reload
### Use Gunicorn in production
# gunicorn app.main:app --bind 0.0.0.0:8282 -w 1 -k uvicorn.workers.UvicornWorker --timeout 600