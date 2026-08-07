# AI Travel Agent

AI-powered travel assistant built with **FastAPI, React, TypeScript, AWS DynamoDB, Google OAuth 2.0, Ollama Qwen2.5:7b, and external APIs**.

Designed to provide conversational travel planning through a local LLM-powered agent capable of retrieving real-time travel data, maintaining conversation memory, and executing multi-step planning workflows.

> *Combines local AI inference with external travel APIs to deliver*
> *personalized travel recommendations, weather insights, location discovery,*
> *and context-aware trip planning through an intelligent agent system.*

---

## Features

- AI travel assistant powered by Ollama Qwen2.5:7b
- Local LLM inference with function calling capabilities
- Multi-step agent planning and reasoning workflows
- Persistent conversation memory using AWS DynamoDB
- Google OAuth 2.0 authentication
- Real-time weather and forecast retrieval
- Geocoding and location discovery integration
- Async FastAPI backend architecture
- React + TypeScript conversational interface

---

## Architecture

```text
                         User
                           │
                           ▼
                  React + TypeScript
                           │
                           ▼
                    FastAPI Backend
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     AI Agent Layer     DynamoDB      External APIs
          │                                 │
          ▼                                 ▼
  Ollama Qwen2.5:7b              Weather / Forecast /
  Function Calling                Location Services
```
---
## Agent Workflow
```text
User Request
      │
      ▼
FastAPI Agent Controller
      │
      ▼
Local LLM (Qwen2.5:7b)
      │
      ├── Analyze user intent
      │
      ├── Determine required tools
      │
      ├── Execute external API calls
      │
      ├── Retrieve conversation memory
      │
      └── Generate final response
```

The AI agent uses function calling to determine when additional information is required. External tools are executed asynchronously, and retrieved data is combined with conversation context before generating a response.
---
## Engineering Challenges
- Designed an asynchronous agent architecture capable of handling multi-step planning workflows
- Integrated 5+ real-time APIs for weather, forecasting, geocoding, and location discovery
- Implemented LLM function calling for dynamic tool execution
- Built persistent conversation memory using AWS DynamoDB
- Connected local LLM inference with cloud-based application infrastructure
- Implemented Google OAuth 2.0 authentication and user sessions
- Structured backend services to support future AI tools and agent capabilities
---
## Technology Stack
### Backend
- FastAPI
- Python
- AWS DynamoDB
- Google OAuth 2.0
- Ollama Qwen2.5:7b
### Frontend
- React
- TypeScript
### AI Infrastructure
- Local LLM inference
- Function calling
- Agent-based reasoning
- Conversation memory
- External Integrations
- Weather APIs
- Forecast APIs
- Geocoding APIs
- Location discovery APIs

---

## API Overview
### Chat With Agent
```
POST /api/v1/chat
```
**Authentication:** Google OAuth 2.0

**Content-Type:** application/json

### Example Request:

{
  "message": "Plan a 5 day trip to Japan in April",
  "conversationId": "abc123"
}

### Example Response:

{
  "response": "Here is your personalized Japan itinerary...",
  "toolsUsed": [
    "weather",
    "location_search"
  ]
}
---

## Retrieve Conversation History
```
GET /api/v1/conversations/{id}
```
Returns previous messages and stored agent context for the authenticated user.

## Agent Capabilities
### Capability	Description
- Travel Planning	Creates personalized multi-step itineraries
- Weather Retrieval	Retrieves current weather and forecasts
- Location Discovery	Finds destinations, attractions, and points of interest
- Geocoding	Converts locations into geographic coordinates
- Conversation Memory	Maintains previous user interactions
- Tool Calling	Dynamically executes external API functions
---
## Authentication
Authentication is handled through Google OAuth 2.0.
```text
User
 │
 ▼
Google OAuth Login
 │
 ▼
FastAPI Authentication Layer
 │
 ▼
Authenticated User Session
 │
 ▼
Agent Conversation Memory
```
Authenticated user data and conversation history are persisted using AWS DynamoDB.
---
## Requirements
- Python 3.11+
- Node.js 18+
- AWS DynamoDB
- Ollama
- Qwen2.5:7b
---
## Installation
### Backend Setup
Create a virtual environment:
```http
python -m venv venv

source venv/bin/activate
```
### Install dependencies:

pip install -r requirements.txt
Install Ollama Model

### Install Ollama and download the required model:

ollama pull qwen2.5:7b

### Verify installation:

ollama list
### Frontend Setup

Navigate to the frontend directory:

cd frontend

### Install dependencies:

npm install

### Run development server:

npm run dev
---
## Running the Application

### Start Ollama:

ollama run qwen2.5:7b

### Start FastAPI backend:

uvicorn main:app --reload

### Start React frontend:

npm run dev
