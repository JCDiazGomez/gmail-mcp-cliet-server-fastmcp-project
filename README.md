# 📧 Gmail MCP Project

**MCP Server and MCP Client** created with **FastMCP** and **Python** for Gmail and OpenAI integration.

A complete Model Context Protocol (MCP) implementation that enables AI assistants to interact with Gmail through a FastMCP server, with a Streamlit web interface for easy interaction.

MCP Server + MCP Client for Gmail and OpenAI/
├── .venv/                    ← Entorno virtual (Python aislado)
│   ├── Scripts/
│   │   ├── Activate.ps1     ← Script para activar en PowerShell
│   │   └── python.exe       ← Python del entorno virtual
│   └── Lib/
│       └── site-packages/   ← Paquetes instalados
│           ├── mcp/         ← Librería MCP (types.py está aquí)
│           ├── openai/      ← Cliente OpenAI
│           ├── google-api-python-client/
│           └── fastmcp/
│
├── .env                      ← Variables de entorno (OPENAI_API_KEY)
├── credentials.json          ← Credenciales OAuth de Google
├── token.pickle              ← Token de autenticación guardado
├── client.py                 ← MCP Client (OpenAI)
├── gmail_mcp_server.py       ← MCP Server (Gmail)
└── app_openAI.py            ← Aplicación principal

---

## 🌟 Features

- **MCP Server** - FastMCP-based server exposing Gmail operations
- **MCP Client** - Python client integrating OpenAI GPT-4o-mini with Gmail toolsç
- **MCP Client** - also with Ollama Now
- **Streamlit Frontend** - Web interface for the MCP client
- **Gmail Integration** - List, send, and manage emails
- **Resource Templates** - Dynamic PDF manual access
- **Prompt Templates** - Pre-built workflows for email automation

---

## 🏗️ Architecture

### 1. **MCP Server** (`gmail_mcp_server.py`)
The server exposes Gmail functionality through the MCP protocol:
- **Tools**: `list_emails`, `send_email`
- **Resources**: Gmail profile information
- **Resource Templates**: PDF manual access with versioning
- **Prompts**: Email summarization, professional email composition, automation workflows

### 2. **MCP Client** (`client.py`)  or (`client_ollama.py`)
The client bridges OpenAI and the MCP server:
- Connects to the MCP server using FastMCP Client
- Converts MCP tools to OpenAI function calling format or Ollama format
- Handles chat completions with tool execution
- Manages resources and prompts

### 3. **Streamlit App** (`app.py`)
Frontend interface providing:
- Interactive chat with the Gmail assistant
- Quick access to prompt templates
- System information display
- Real-time email management

---

## 📋 Prerequisites

- **Python 3.10+**
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Google Cloud Credentials** - Create OAuth 2.0 credentials in [Google Cloud Console](https://console.cloud.google.com/)
- **Ollama** - get From (https://ollama.com/)

---

## 🚀 Installation

### 1. Create Virtual Environment

Using `venv`:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install openai fastmcp python-dotenv
pip install streamlit
pip install google-auth-oauthlib google-api-python-client PyPDF2
pip install ollama
```

---

## ⚙️ Configuration

### 1. OpenAI API Key

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Important**: Add `.env` to `.gitignore` to keep your API key secure.

### 2. Google Gmail Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API**
4. Create **OAuth 2.0 Client ID** credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in the project root

**Important**: Add `credentials.json` and `token.pickle` to `.gitignore`.

### 3. File Structure

```
.
├── app.py                    # Streamlit frontend
├── client.py                 # MCP Client
├── gmail_mcp_server.py       # MCP Server
├── credentials.json          # Google OAuth credentials (not in git)
├── .env                      # OpenAI API key (not in git)
├── token.pickle             # Gmail auth token (auto-generated, not in git)
├── manuals/                  # PDF manuals directory
└── README.md
```

---

## 🎯 Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Or with the full virtual environment path:
```bash
".venv/Scripts/streamlit.exe" run app.py  # Windows
.venv/bin/streamlit run app.py            # Linux/Mac
```

### Run the MCP Server Standalone

```bash
python gmail_mcp_server.py
```

### First Run - Gmail Authentication

On first execution, the app will:
1. Open your browser for Google authentication
2. Request permissions to read and send emails
3. Save authentication token to `token.pickle`

---

## 💡 How It Works

### Client Workflow

1. **OpenAI Integration**
   - Client connects to OpenAI using the API key from `.env`
   - Uses GPT-4o-mini model for intelligent responses

2. **Gmail Connection**
   - Client loads `credentials.json` for Google authentication
   - Manages OAuth flow and token refresh automatically

3. **FastMCP Client Methods**
   - `list_tools()` - Retrieves available MCP tools
   - `call_tool()` - Executes tools on the MCP server
   - `get_prompt()` - Loads prompt templates
   - `read_resource()` - Accesses resource data

4. **OpenAI Tool Format Conversion**
   - Converts MCP tools to OpenAI's function calling JSON structure
   - Each LLM has specific JSON requirements
   - Client handles translation between MCP and OpenAI formats

---

## 📚 Available Commands

### List Recent Emails
```
"Show me my last 10 emails"
```

### Send an Email
```
"Send an email to john@example.com with subject 'Meeting' and body 'Let's meet tomorrow'"
```

### Use Prompt Templates
- **Daily Email Summary** - Get organized overview of today's emails
- **Compose Professional Email** - AI-assisted email writing

---

## 🔧 Troubleshooting

### Import Errors
Make sure you're using the virtual environment Python:
```bash
which python  # Should show .venv path
```

### Google Authentication Issues
Delete `token.pickle` and authenticate again:
```bash
del token.pickle  # Windows
rm token.pickle   # Linux/Mac
```

### OpenAI API Errors
Verify your `.env` file contains a valid API key:
```bash
cat .env  # Should show OPENAI_API_KEY=sk-...
```

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Author JCDiaz

Created with FastMCP and OpenAI integration.

diagrams
<img width="831" height="358" alt="Captura de pantalla 2025-12-29 225733" src="https://github.com/user-attachments/assets/d6ae20a7-2e28-4195-848b-10cbed63da52" />


<img width="1340" height="987" alt="Captura de pantalla 2025-12-29 225634" src="https://github.com/user-attachments/assets/2fab07b0-9e41-41db-bb1c-a211096bfc10" />



<img width="1230" height="1008" alt="Captura de pantalla 2025-12-29 224828" src="https://github.com/user-attachments/assets/30f914f9-4544-4b5f-82ff-aeddf746a564" />









