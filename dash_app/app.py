"""
Simple Dash chat app that calls the Databricks agent backend.

Run locally:
    pip install dash requests python-dotenv
    python dash_app/app.py

Deploy to Databricks Apps:
    See README.md
"""

import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CHAT_APP_PORT = int(os.getenv("CHAT_APP_PORT", 5000))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Agent Chat", className="text-center mt-4 mb-4"),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                id="chat-messages",
                                style={
                                    "height": "400px",
                                    "overflowY": "auto",
                                    "marginBottom": "20px",
                                    "border": "1px solid #ddd",
                                    "borderRadius": "4px",
                                    "padding": "10px",
                                    "backgroundColor": "#f9f9f9",
                                },
                                children=[
                                    html.Div(
                                        "Start a conversation with the agent...",
                                        style={"color": "#999", "fontStyle": "italic"},
                                    )
                                ],
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.Input(
                                        id="user-input",
                                        placeholder="Type your message...",
                                        type="text",
                                        className="form-control",
                                    ),
                                    dbc.Button(
                                        "Send",
                                        id="send-button",
                                        className="btn btn-primary",
                                        n_clicks=0,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    className="shadow",
                ),
                width=12,
                lg=8,
                className="offset-lg-2",
            )
        ),
        # Store for conversation history
        dcc.Store(id="conversation-store", data=[]),
        # Loading indicator
        dcc.Loading(
            id="loading",
            type="default",
            children=html.Div(id="loading-output"),
        ),
    ],
    fluid=True,
    className="mt-4",
)


@callback(
    [
        Output("conversation-store", "data"),
        Output("user-input", "value"),
        Output("chat-messages", "children"),
    ],
    Input("send-button", "n_clicks"),
    State("user-input", "value"),
    State("conversation-store", "data"),
    prevent_initial_call=True,
)
def send_message(n_clicks, user_message, conversation):
    if not user_message or not user_message.strip():
        return conversation, "", _render_messages(conversation)

    # Add user message to conversation
    conversation.append(
        {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()}
    )

    try:
        # Call backend agent - only send role and content, not timestamps
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in conversation]
        response = requests.post(
            f"{BACKEND_URL}/invocations",
            json={"input": messages},
            timeout=300,
        )
        response.raise_for_status()
        result = response.json()

        # Extract agent response
        agent_response = result.get("output", "No response from agent")
        if isinstance(agent_response, dict):
            agent_response = json.dumps(agent_response, indent=2)

        # Add agent message to conversation
        conversation.append(
            {
                "role": "assistant",
                "content": str(agent_response),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except requests.exceptions.RequestException as e:
        # Add error message
        conversation.append(
            {
                "role": "assistant",
                "content": f"Error calling backend: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
        )

    # Render messages and clear input
    return conversation, "", _render_messages(conversation)


def _render_messages(conversation):
    """Render conversation messages as HTML."""
    if not conversation:
        return [
            html.Div(
                "Start a conversation with the agent...",
                style={"color": "#999", "fontStyle": "italic"},
            )
        ]

    messages = []
    for msg in conversation:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        is_user = role == "user"

        # Style based on role
        if is_user:
            bg_color = "#e3f2fd"
            text_align = "right"
            margin = "10px 0 10px 30%"
        else:
            bg_color = "#f5f5f5"
            text_align = "left"
            margin = "10px 30% 10px 0"

        messages.append(
            html.Div(
                [
                    html.Div(
                        role.capitalize(),
                        style={"fontWeight": "bold", "fontSize": "0.85rem", "color": "#666"},
                    ),
                    html.Div(
                        content,
                        style={
                            "backgroundColor": bg_color,
                            "padding": "10px",
                            "borderRadius": "4px",
                            "marginTop": "4px",
                            "whiteSpace": "pre-wrap",
                            "wordWrap": "break-word",
                        },
                    ),
                ],
                style={"margin": margin, "textAlign": text_align},
            )
        )

    return messages


if __name__ == "__main__":
    print(f"Starting Dash app on http://localhost:{CHAT_APP_PORT}")
    print(f"Backend URL: {BACKEND_URL}")
    app.run(debug=False, host="0.0.0.0", port=CHAT_APP_PORT)
