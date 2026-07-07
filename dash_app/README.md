# Dash Chat App

A lightweight Dash-based chat interface for the Databricks agent backend.

## Local Development

### Prerequisites
- Backend running on port 8000: `uv run start-app --no-ui`

### Setup

```bash
pip install dash dash-bootstrap-components requests python-dotenv
python dash_app/app.py
```

The app will start on `http://localhost:5000` (configurable via `CHAT_APP_PORT` in `.env`)

## Deployment to Databricks Apps

### 1. Create a Databricks App

```bash
databricks apps create --name agent-chat-dash
```

### 2. Update `databricks.yml`

Add a resource for the Dash app:

```yaml
resources:
  apps:
    agent_chat_dash:
      name: agent-chat-dash
      source_code_path: ./dash_app
      config:
        command: python app.py
        environment:
          - name: CHAT_APP_PORT
            value: "8080"
          - name: BACKEND_URL
            value: "https://<your-databricks-instance>/api/2.0/serving-endpoints/<agent-endpoint>"
```

### 3. Deploy

```bash
databricks bundle deploy
```

## Configuration

Environment variables (from `.env`):

- `CHAT_APP_PORT`: Port to run the app on (default: 5000)
- `BACKEND_URL`: Backend agent URL (default: http://localhost:8000)

## Features

- Simple chat interface
- Conversation history stored in browser
- Real-time streaming responses (currently uses polling; can add WebSocket for true streaming)
- Error handling with user feedback
- Bootstrap-based responsive design
