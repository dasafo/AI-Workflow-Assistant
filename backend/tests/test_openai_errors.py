# Este archivo puede estar vacío, es solo para marcar el directorio como un paquete Python

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from openai import AsyncOpenAI, APITimeoutError, RateLimitError, APIError
import os
from fastapi import FastAPI
from typing import List

# Import our application
from main import app
from core.errors import OpenAITimeoutError, OpenAIRateLimitError, OpenAIError
from services.tasks.summarize import call_openai_with_retry

# Importar el router MCP
from mcp.router import router as mcp_router
from mcp.config import get_mcp_settings


# Fixture para crear un cliente de prueba para nuestra app FastAPI
@pytest.fixture
def test_client():
    """Create a test client for our FastAPI app"""
    return TestClient(app)


# Fixture para crear un cliente de prueba para nuestra app FastAPI
@pytest.fixture
def mock_openai_client():
    """Create a mock AsyncOpenAI client"""
    with patch("services.tasks.summarize.client") as mock_client:
        yield mock_client


# Test para manejar el error de timeout de OpenAI
@pytest.mark.asyncio
async def test_openai_timeout_error(mock_openai_client):
    """Test handling of OpenAI timeout error"""
    # Setup mock to raise a timeout error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = asyncio.TimeoutError(
        "Connection timed out"
    )
    mock_openai_client.chat = mock_chat

    # Test direct function call
    with pytest.raises(OpenAITimeoutError) as exc_info:
        await call_openai_with_retry("Test text")

    # Verify the error details
    assert "Timeout" in str(exc_info.value)
    assert exc_info.value.code == "E302"


# Test para manejar el error de rate limit de OpenAI
@pytest.mark.asyncio
async def test_openai_rate_limit_error(mock_openai_client):
    """Test handling of OpenAI rate limit error"""
    # Setup mock to raise a rate limit error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
    mock_openai_client.chat = mock_chat

    # Test direct function call
    with pytest.raises(OpenAIRateLimitError) as exc_info:
        await call_openai_with_retry("Test text")

    # Verify the error details
    assert "límite" in str(exc_info.value)
    assert exc_info.value.code == "E303"


# Test para manejar el error general de OpenAI
@pytest.mark.asyncio
async def test_openai_api_error(mock_openai_client):
    """Test handling of general OpenAI API error"""
    # Setup mock to raise a general API error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = APIError("Invalid request")
    mock_openai_client.chat = mock_chat

    # Test direct function call
    with pytest.raises(OpenAIError) as exc_info:
        await call_openai_with_retry("Test text")

    # Verify the error details
    assert "API" in str(exc_info.value)
    assert exc_info.value.code == "E301"


def test_api_endpoint_timeout_error(test_client, mock_openai_client):
    """Test API endpoint behavior on OpenAI timeout"""
    # Setup mock to raise a timeout error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = asyncio.TimeoutError(
        "Connection timed out"
    )
    mock_openai_client.chat = mock_chat

    # Call the API endpoint
    response = test_client.post(
        "/api/v1/procesar",
        json={"chat_id": 123456, "texto": "Test text", "tipo_tarea": "resumir"},
        headers={"x-api-key": "test_api_key"},
    )

    # Check response
    assert response.status_code == 504
    assert response.json()["code"] == "E302"
    assert "timeout" in response.json()["message"].lower()


# Test para manejar el error de rate limit de OpenAI
def test_api_endpoint_rate_limit_error(test_client, mock_openai_client):
    """Test API endpoint behavior on OpenAI rate limit error"""
    # Setup mock to raise a rate limit error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
    mock_openai_client.chat = mock_chat

    # Call the API endpoint
    response = test_client.post(
        "/api/v1/procesar",
        json={"chat_id": 123456, "texto": "Test text", "tipo_tarea": "resumir"},
        headers={"x-api-key": "test_api_key"},
    )

    # Check response
    assert response.status_code == 429
    assert response.json()["code"] == "E303"
    assert "límite" in response.json()["message"].lower()


def test_api_endpoint_general_error(test_client, mock_openai_client):
    """Test API endpoint behavior on general OpenAI error"""
    # Setup mock to raise a general API error
    mock_chat = AsyncMock()
    mock_chat.completions.create.side_effect = APIError("Invalid request")
    mock_openai_client.chat = mock_chat

    # Call the API endpoint
    response = test_client.post(
        "/api/v1/procesar",
        json={"chat_id": 123456, "texto": "Test text", "tipo_tarea": "resumir"},
        headers={"x-api-key": "test_api_key"},
    )

    # Check response
    assert response.status_code == 502
    assert response.json()["code"] == "E301"
    assert "api" in response.json()["message"].lower()


# Test para validar cuando no se proporciona un tipo de tarea y no existe un modo activo
def test_missing_task_type_validation(test_client):
    """Test validation when no task type is provided and no active mode exists"""
    # Call the API endpoint with no tipo_tarea
    response = test_client.post(
        "/api/v1/procesar",
        json={"chat_id": 123456, "texto": "Test text"},
        headers={"x-api-key": "test_api_key"},
    )

    # Check response (assuming no active mode for this chat_id)
    assert response.status_code == 400
    assert "no hay modo activo" in response.json()["message"].lower()
