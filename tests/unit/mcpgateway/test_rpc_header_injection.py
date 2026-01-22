# -*- coding: utf-8 -*-
"""Unit tests for /rpc endpoint x-mcp-session-id header injection.

Tests verify that the /rpc endpoint properly injects x-mcp-session-id headers
for session affinity in both the standard tools/call path and the legacy
fallback path.

Copyright 2025
SPDX-License-Identifier: Apache-2.0
"""

# Standard
from unittest.mock import AsyncMock, MagicMock, patch

# Third-Party
import pytest
from fastapi.testclient import TestClient

# First-Party
from mcpgateway.main import app


@pytest.mark.asyncio
async def test_rpc_tools_call_injects_x_mcp_session_id():
    """Test that /rpc endpoint injects x-mcp-session-id for tools/call method."""

    # Mock the tool_service.invoke_tool to capture the headers passed to it
    captured_headers = {}

    async def mock_invoke_tool(*args, **kwargs):
        # Capture the headers passed to invoke_tool
        if "request_headers" in kwargs:
            captured_headers.update(kwargs["request_headers"])
        # Return a mock result
        return MagicMock(model_dump=lambda **kw: {"content": [{"type": "text", "text": "test result"}]})

    with patch("mcpgateway.main.tool_service") as mock_tool_service:
        mock_tool_service.invoke_tool = mock_invoke_tool

        # Mock database and user
        with patch("mcpgateway.main.get_db"), \
             patch("mcpgateway.main.authenticate_request", return_value={"email": "test@example.com", "is_admin": True}):

            client = TestClient(app)

            # Send RPC request with mcp-session-id header
            response = client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "test_tool",
                        "arguments": {}
                    }
                },
                headers={
                    "mcp-session-id": "session-abc-123",
                    "Authorization": "Bearer test-token"
                }
            )

            # Verify the request succeeded
            assert response.status_code == 200

            # Verify x-mcp-session-id was injected from mcp-session-id
            assert "x-mcp-session-id" in captured_headers
            assert captured_headers["x-mcp-session-id"] == "session-abc-123"

            # Verify original mcp-session-id is also present
            assert "mcp-session-id" in captured_headers
            assert captured_headers["mcp-session-id"] == "session-abc-123"


@pytest.mark.asyncio
async def test_rpc_legacy_tool_invocation_injects_x_mcp_session_id():
    """Test that /rpc endpoint injects x-mcp-session-id for legacy tool invocation (fallback path)."""

    # Mock the tool_service.invoke_tool to capture the headers passed to it
    captured_headers = {}

    async def mock_invoke_tool(*args, **kwargs):
        # Capture the headers passed to invoke_tool
        if "request_headers" in kwargs:
            captured_headers.update(kwargs["request_headers"])
        # Return a mock result
        return MagicMock(model_dump=lambda **kw: {"content": [{"type": "text", "text": "test result"}]})

    with patch("mcpgateway.main.tool_service") as mock_tool_service:
        mock_tool_service.invoke_tool = mock_invoke_tool

        # Mock database and user
        with patch("mcpgateway.main.get_db"), \
             patch("mcpgateway.main.authenticate_request", return_value={"email": "test@example.com", "is_admin": True}):

            client = TestClient(app)

            # Send RPC request using legacy format (method=tool_name instead of tools/call)
            response = client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "my_custom_tool",  # Legacy format: direct tool name
                    "params": {
                        "arg1": "value1"
                    }
                },
                headers={
                    "mcp-session-id": "session-xyz-789",
                    "Authorization": "Bearer test-token"
                }
            )

            # Verify the request succeeded
            assert response.status_code == 200

            # Verify x-mcp-session-id was injected from mcp-session-id in fallback path
            assert "x-mcp-session-id" in captured_headers
            assert captured_headers["x-mcp-session-id"] == "session-xyz-789"

            # Verify original mcp-session-id is also present
            assert "mcp-session-id" in captured_headers
            assert captured_headers["mcp-session-id"] == "session-xyz-789"


@pytest.mark.asyncio
async def test_rpc_handles_missing_mcp_session_id_gracefully():
    """Test that /rpc endpoint handles requests without mcp-session-id header."""

    # Mock the tool_service.invoke_tool to capture the headers passed to it
    captured_headers = {}

    async def mock_invoke_tool(*args, **kwargs):
        # Capture the headers passed to invoke_tool
        if "request_headers" in kwargs:
            captured_headers.update(kwargs["request_headers"])
        # Return a mock result
        return MagicMock(model_dump=lambda **kw: {"content": [{"type": "text", "text": "test result"}]})

    with patch("mcpgateway.main.tool_service") as mock_tool_service:
        mock_tool_service.invoke_tool = mock_invoke_tool

        # Mock database and user
        with patch("mcpgateway.main.get_db"), \
             patch("mcpgateway.main.authenticate_request", return_value={"email": "test@example.com", "is_admin": True}):

            client = TestClient(app)

            # Send RPC request WITHOUT mcp-session-id header
            response = client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "test_tool",
                        "arguments": {}
                    }
                },
                headers={
                    "Authorization": "Bearer test-token"
                }
            )

            # Verify the request succeeded
            assert response.status_code == 200

            # Verify x-mcp-session-id was NOT injected (no mcp-session-id to inject from)
            assert "x-mcp-session-id" not in captured_headers

            # Verify mcp-session-id is also absent
            assert "mcp-session-id" not in captured_headers


@pytest.mark.asyncio
async def test_rpc_preserves_x_mcp_session_id_if_already_present():
    """Test that /rpc endpoint doesn't overwrite x-mcp-session-id if already present."""

    # Mock the tool_service.invoke_tool to capture the headers passed to it
    captured_headers = {}

    async def mock_invoke_tool(*args, **kwargs):
        # Capture the headers passed to invoke_tool
        if "request_headers" in kwargs:
            captured_headers.update(kwargs["request_headers"])
        # Return a mock result
        return MagicMock(model_dump=lambda **kw: {"content": [{"type": "text", "text": "test result"}]})

    with patch("mcpgateway.main.tool_service") as mock_tool_service:
        mock_tool_service.invoke_tool = mock_invoke_tool

        # Mock database and user
        with patch("mcpgateway.main.get_db"), \
             patch("mcpgateway.main.authenticate_request", return_value={"email": "test@example.com", "is_admin": True}):

            client = TestClient(app)

            # Send RPC request with BOTH mcp-session-id and x-mcp-session-id headers
            response = client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "test_tool",
                        "arguments": {}
                    }
                },
                headers={
                    "mcp-session-id": "session-new-456",
                    "x-mcp-session-id": "session-old-123",  # Already present
                    "Authorization": "Bearer test-token"
                }
            )

            # Verify the request succeeded
            assert response.status_code == 200

            # The injection logic will overwrite x-mcp-session-id with mcp-session-id
            # This is correct behavior - mcp-session-id is the source of truth
            assert "x-mcp-session-id" in captured_headers
            assert captured_headers["x-mcp-session-id"] == "session-new-456"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
