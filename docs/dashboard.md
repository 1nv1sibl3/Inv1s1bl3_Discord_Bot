# Inv1s1bl3 Bot — Web Management Dashboard

## 1. Overview

The Inv1s1bl3 Bot web dashboard is built using **Flask 3.x** and styled with a custom, responsive Discord dark theme. It provides an intuitive interface for server administrators to configure bot behavior without running command line syntax.

---

## 2. Authentication Flow (Discord OAuth2)

```
User               Web Dashboard                   Discord OAuth2
 |                       |                               |
 |--- Click Login ------>|                               |
 |                       |--- Generate State & URL ----->|
 |<-- Redirect to Discord |                               |
 |                                                       |
 |--- Authorize Application (identify + guilds) -------->|
 |                                                       |
 |<-- Callback with code & state ------------------------|
 |                       |                               |
 |--- GET /callback ---->|                               |
 |                       |--- Verify State CSRF Token ---|
 |                       |--- Exchange code for token -->|
 |                       |<-- Access & Refresh Tokens ---|
 |                       |                               |
 |                       |--- Fetch User Profile (@me) ->|
 |                       |<-- User Profile JSON ---------|
 |                       |                               |
 |<-- 302 /dashboard ----|                               |
```

### Security Measures:
1. **CSRF Protection**: A 32-byte cryptographic token (`state`) is generated per authorization attempt and verified upon callback return.
2. **Permission Guarding**: Endpoints like `/servers/<guild_id>` inspect the authenticated user's guild permission bitmask to ensure they possess `ADMINISTRATOR (0x8)` or `MANAGE_GUILD (0x20)` before allowing view or edit access.
3. **Session Hardening**: Cookies are signed with `SECRET_KEY`, flagged `HttpOnly`, and configured with `SameSite=Lax`.

---

## 3. Server Configuration Features

Administrators can configure the following per-server options:
- **Custom Prefix**: Modify the server prefix (e.g. from `i.` to `!` or `?`).
- **Welcome System**:
  - Toggle welcome greetings on/off.
  - Designate welcome announcement text channel.
  - Customize greeting template with `{user}` and `{server}` placeholders.
- **Farewell System**:
  - Toggle leave announcements on/off.
  - Designate farewell text channel.
  - Customize departure message template.
