# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/common/enums.py
Copyright 2026
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Shared enums for MCP Gateway.
"""

# Standard
from enum import Enum


class TransportType(Enum):
    """Supported MCP transport types."""

    SSE = "sse"
    STREAMABLE_HTTP = "streamablehttp"
