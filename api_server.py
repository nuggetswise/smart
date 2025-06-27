#!/usr/bin/env python3
"""
FastAPI server for handling webhooks from Activepieces
This runs alongside the Streamlit app to provide webhook endpoints.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import json
import logging
from datetime import datetime
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartDesk AI Webhook Server",
    description="Webhook endpoints for Activepieces integration",
    version="1.0.0"
)

# Initialize webhook handler
webhook_handler = WebhookHandler()

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "SmartDesk AI Webhook Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SmartDesk AI Webhook Server",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/webhook")
async def webhook_endpoint(request: Request):
    """Main webhook endpoint for Activepieces."""
    try:
        # Get request body
        body = await request.body()
        payload = json.loads(body)
        
        # Get headers
        headers = dict(request.headers)
        
        # Process webhook
        result = webhook_handler.process_webhook(payload, headers)
        
        logger.info(f"Webhook processed: {result['success']}")
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/test-webhook")
async def test_webhook():
    """Test webhook endpoint."""
    test_payload = {
        "event_type": "test",
        "timestamp": datetime.now().isoformat(),
        "test_data": "SmartDesk AI webhook test"
    }
    
    test_headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test_key"
    }
    
    result = webhook_handler.process_webhook(test_payload, test_headers)
    
    return JSONResponse(content={
        "message": "Test webhook processed",
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/api/status")
async def get_status():
    """Get server status and configuration."""
    return {
        "server": "SmartDesk AI Webhook Server",
        "status": "running",
        "endpoints": {
            "webhook": "/api/webhook",
            "test": "/api/test-webhook",
            "health": "/health",
            "status": "/api/status"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8509,  # Different port from Streamlit
        reload=True,
        log_level="info"
    ) 