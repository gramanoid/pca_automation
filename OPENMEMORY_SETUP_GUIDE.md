# OpenMemory MCP Server Setup Guide

## 🎉 Installation Complete!

Your OpenMemory MCP server is now running successfully. Here's everything you need to know:

## 🚀 Running Services

1. **OpenMemory MCP Server**: http://localhost:8765
   - API Documentation: http://localhost:8765/docs
   - MCP Endpoint: http://localhost:8765/mcp/messages/

2. **OpenMemory UI**: http://localhost:3000
   - Web interface for viewing and managing memories

3. **Qdrant Vector Store**: http://localhost:6333/dashboard
   - Vector database for semantic search

## 🔧 How to Use OpenMemory

### 1. Via REST API

Create a memory:
```bash
curl -X POST http://localhost:8765/api/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "text": "Remember this information",
    "app": "your_app_name"
  }'
```

Get user stats:
```bash
curl "http://localhost:8765/api/v1/stats/?user_id=your_user_id"
```

### 2. Via MCP Client Configuration

To use OpenMemory with Claude, Cursor, or other MCP-compatible clients:

#### For Claude Desktop App

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openmemory": {
      "url": "http://localhost:8765/mcp/messages/",
      "transport": "sse",
      "config": {
        "user_id": "alexgrama",
        "client_name": "claude"
      }
    }
  }
}
```

#### For Cursor IDE

Add to your `.cursor/mcp/config.json`:

```json
{
  "servers": {
    "openmemory": {
      "endpoint": "http://localhost:8765/mcp/messages/",
      "transport": "sse",
      "config": {
        "user_id": "alexgrama",
        "client_name": "cursor"
      }
    }
  }
}
```

### 3. Via Python Client

```python
import requests

# Create a memory
response = requests.post(
    "http://localhost:8765/api/v1/memories/",
    json={
        "user_id": "alexgrama",
        "text": "Important information to remember",
        "app": "python_app"
    }
)
```

## 📊 What We've Tested

✅ API is running and accessible
✅ Memory creation works (1 memory created successfully)
✅ User stats endpoint works
✅ Apps are automatically created when memories are added

## 🛑 Managing the Services

**To stop the services:**
```bash
cd mem0/openmemory && docker-compose down
```

**To restart the services:**
```bash
cd mem0/openmemory && make up
```

**To view logs:**
```bash
docker logs openmemory-openmemory-mcp-1 -f  # MCP server logs
docker logs openmemory-openmemory-ui-1 -f   # UI logs
```

## 🎯 Next Steps

1. **Access the UI**: Open http://localhost:3000 in your browser to see your memories
2. **Configure your MCP client**: Use the configuration examples above
3. **Start creating memories**: The system will automatically extract and store facts from your conversations

## 🐛 Troubleshooting

- If you see "Internal Server Error" when listing memories, this is a known issue with the current version
- Use the stats endpoint to verify memories are being created
- Check the logs if you encounter any issues

## 📝 Your Test Results

- **User ID**: alexgrama
- **Memories Created**: 1
- **Apps Registered**: 2 (openmemory, test_app)
- **Memory Content**: "Name is Alex" (extracted from "My name is Alex and I am testing the OpenMemory system")

The system successfully extracted the fact from your test message and stored it!