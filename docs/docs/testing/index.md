# 🧪 Testing MCP Gateway

This section contains guides for testing your MCP Gateway deployment.

## 🔹 Basic Smoke Test

Use the [Basic Smoke Test](basic.md) to verify:

- JWT token generation and authentication
- Gateway registration
- Tool registration
- Server creation and event streaming
- Tool invocation via JSON-RPC

This test is ideal for validating local development environments or freshly deployed test instances.

---

## 🔹 Microsoft Entra ID E2E Tests

Use the [Entra ID E2E Testing Guide](entra-id-e2e.md) to validate:

- SSO integration with Microsoft Entra ID (Azure AD)
- Group-based `platform_admin` role assignment
- Dynamic user and group management via Microsoft Graph API
- OIDC discovery and JWKS validation

These tests are fully automated and self-contained, creating and cleaning up Azure resources automatically.

---

For additional scenarios (e.g., completion APIs, multi-hop toolchains), expand the test suite as needed.
