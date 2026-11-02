# Research Blog & Project Discussion Board

For Assignment 1, it includes a basic FastAPI status endpoint,
an automated test, and a multi-stage Docker setup with Docker Compose.

Run the following commands from the project folder.

## Setup

1. Create a local virtual environment:

   ```bash
   python3 -m venv .venv
   ```

2. Activate the environment:

   ```bash
   source .venv/bin/activate
   ```

3. Install the application and test dependencies:

   ```bash
   python -m pip install -r requirements.txt -r requirements-dev.txt
   ```

## Run the App Locally

With the virtual environment activated, run:

```bash
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/health in the browser.

Expected response:

```json
{ "status": "ok" }
```

Press Ctrl+C in the terminal to stop the server.

## Run the Tests

With the virtual environment activated, run:

```bash
python -m pytest -q
```

The test checks that `/health` returns HTTP 200 and
`{"status":"ok"}`.

## Run with Docker Compose

Make sure Docker Desktop is running.

Build the image:

```bash
docker compose build
```

Start the app in the background:

```bash
docker compose up -d
```

Check the health endpoint:

```bash
curl -sS -i http://127.0.0.1:8001/health
```

The response should include HTTP 200 and this JSON body:

```json
{ "status": "ok" }
```

If the first request fails while the app is starting,
check the logs and retry the request:

```bash
docker compose logs app
```

Stop and remove the Compose container:

```bash
docker compose down
```

## Run with Docker Directly

This is an alternative to Docker Compose. Both methods use
the same container name and host port. If the Compose
container exists, run `docker compose down` before using
the commands below.

Build the image:

```bash
docker build -t cs763-a1 .
```

Start the container, mapping host `127.0.0.1:8001` to
container port `8000`:

```bash
docker run --name cs763-a1-check -d -p 127.0.0.1:8001:8000 cs763-a1
```

Check the health endpoint:

```bash
curl -sS -i http://127.0.0.1:8001/health
```

The response should include HTTP 200 and this JSON body:

```json
{ "status": "ok" }
```

If needed, inspect the startup logs and retry the request:

```bash
docker logs cs763-a1-check
```

Stop and remove the container before switching to Compose
or creating another container with the same name:

```bash
docker stop cs763-a1-check
docker rm cs763-a1-check
```
