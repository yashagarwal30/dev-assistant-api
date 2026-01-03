# Dev Assistant API

AI-powered development assistant backend using Claude API and FastAPI. A production-ready REST API for code analysis, chat assistance, and intelligent code review.

## Features

- **Intelligent Chat**: Context-aware conversations with code understanding
- **Code Analysis**: Automated code review, refactoring suggestions, explanations, and test generation
- **Response Caching**: Smart caching system to reduce API costs and improve response times
- **Conversation History**: Persistent conversation storage with SQLite/PostgreSQL
- **RESTful API**: Well-documented FastAPI endpoints with automatic OpenAPI docs
- **Database Integration**: SQLAlchemy async ORM with support for SQLite and PostgreSQL
- **Production Ready**: Async operations, proper error handling, and scalable architecture

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **Claude API**: Anthropic's powerful language model
- **SQLAlchemy**: Async ORM for database operations
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server
- **SQLite/PostgreSQL**: Database options

## Project Structure

```
dev-assistant-api/
├── app/
│   ├── api/                 # API route handlers
│   │   ├── chat.py          # Chat endpoints
│   │   ├── code_analysis.py # Code analysis endpoints
│   │   └── admin.py         # Admin & utility endpoints
│   ├── core/                # Core configuration
│   │   └── config.py        # Settings management
│   ├── db/                  # Database setup
│   │   └── database.py      # DB connection & session
│   ├── models/              # SQLAlchemy models
│   │   └── conversation.py  # DB models
│   ├── schemas/             # Pydantic schemas
│   │   └── conversation.py  # Request/response schemas
│   ├── services/            # Business logic
│   │   └── claude_service.py # Claude API integration
│   └── main.py             # FastAPI application
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── run.py                  # Application runner
└── setup.sh                # Setup script

```

## Quick Start

### 1. Setup

```bash
# Clone or navigate to project directory
cd dev-assistant-api

# Run setup script (creates venv, installs dependencies)
chmod +x setup.sh
./setup.sh
```

### 2. Configuration

Edit `.env` file and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./dev_assistant.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 3. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python run.py
```

The API will be available at `http://localhost:8000`

### 4. Explore the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/admin/health

## API Endpoints

### Chat Endpoints

#### POST `/chat/`
Send a chat message and get AI response

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the difference between async and sync in Python?",
    "temperature": 0.7
  }'
```

#### POST `/chat/` (with context)
Chat with code context

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I optimize this code?",
    "context": "def slow_function():\n    for i in range(1000000):\n        print(i)"
  }'
```

#### GET `/chat/conversations`
List all conversations

```bash
curl "http://localhost:8000/chat/conversations?limit=10"
```

#### GET `/chat/conversations/{session_id}`
Get specific conversation with messages

### Code Analysis Endpoints

#### POST `/code/analyze`
Analyze code with AI

```bash
curl -X POST "http://localhost:8000/code/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calculate(a, b):\n    return a + b",
    "analysis_type": "review",
    "file_path": "calculator.py"
  }'
```

**Analysis Types:**
- `review`: Comprehensive code review
- `refactor`: Refactoring suggestions
- `explain`: Code explanation
- `optimize`: Performance optimization
- `test`: Generate unit tests

#### GET `/code/analysis/history`
Get analysis history

```bash
curl "http://localhost:8000/code/analysis/history?analysis_type=review&limit=10"
```

### Admin Endpoints

#### GET `/admin/stats`
Get API usage statistics

```bash
curl "http://localhost:8000/admin/stats"
```

#### GET `/admin/cache/stats`
Get cache statistics

```bash
curl "http://localhost:8000/admin/cache/stats"
```

#### DELETE `/admin/cache/clear`
Clear all cache entries

## Usage Examples

### Python Example

```python
import httpx
import asyncio

async def chat_example():
    async with httpx.AsyncClient() as client:
        # Send a message
        response = await client.post(
            "http://localhost:8000/chat/",
            json={
                "message": "Explain list comprehensions in Python",
                "temperature": 0.5
            }
        )
        data = response.json()
        print(f"Response: {data['message']}")
        print(f"Session ID: {data['session_id']}")

        # Continue conversation
        response = await client.post(
            "http://localhost:8000/chat/",
            json={
                "message": "Can you show me an example?",
                "session_id": data['session_id']
            }
        )
        print(response.json()['message'])

asyncio.run(chat_example())
```

### Code Analysis Example

```python
import httpx
import asyncio

async def analyze_code():
    code = """
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/code/analyze",
            json={
                "code": code,
                "analysis_type": "optimize",
                "file_path": "fibonacci.py"
            }
        )
        print(response.json()['result'])

asyncio.run(analyze_code())
```

## Database

### SQLite (Default)
The application uses SQLite by default, perfect for development and small deployments.

### PostgreSQL (Production)
For production, use PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dev_assistant
```

Install PostgreSQL driver:
```bash
pip install asyncpg
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
ruff check app/
```

## Deployment

### Using Docker (Coming Soon)

```bash
docker build -t dev-assistant-api .
docker run -p 8000:8000 --env-file .env dev-assistant-api
```

### Cloud Deployment

Deploy to:
- **Railway**: One-click deployment
- **Render**: Auto-deploy from Git
- **AWS/GCP**: Use with proper environment configuration

## Future Enhancements

- [ ] GitHub OAuth integration
- [ ] GitHub API integration for PR reviews
- [ ] GitHub Webhooks for automated analysis
- [ ] WebSocket support for streaming responses
- [ ] API authentication with API keys
- [ ] Rate limiting
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Frontend dashboard
- [ ] Multi-model support (GPT, Gemini, etc.)

## Contributing

Contributions are welcome! This project demonstrates:
- Modern Python async patterns
- RESTful API design
- Database design and ORM usage
- AI API integration
- Production-ready code structure

## License

MIT License

## Resume Highlights

**Key Technical Skills Demonstrated:**
- ✅ FastAPI & async Python
- ✅ RESTful API design
- ✅ Database design (SQLAlchemy ORM)
- ✅ AI/LLM integration (Claude API)
- ✅ Caching strategies
- ✅ Clean architecture & separation of concerns
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Production-ready code patterns

**MAANG Interview Topics Covered:**
- System design (caching, database schema)
- Async programming
- API design best practices
- Database optimization
- Error handling & validation
- Testing strategies
