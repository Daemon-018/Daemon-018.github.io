---
title: "IDOR Hunting Methodology — How to Find Insecure Direct Object References"
description: "Complete guide to finding IDOR vulnerabilities in web applications and APIs. Methodology, tools, and real-world examples."
date: 2026-06-17
draft: false
tags: ["idor", "api-security", "methodology", "bug-bounty"]
categories: ["Bug Bounty", "Methodology"]
---

# IDOR Hunting Methodology

IDOR (Insecure Direct Object Reference) is the #1 most rewarded vulnerability class in bug bounty programs. It's simple to find, easy to explain, and has high impact.

## What is IDOR?

IDOR occurs when an application uses user-supplied input to directly access an object without verifying that the user is authorized to access it.

**Example:**
```
# Your own profile
GET /api/users/1234/profile → 200 OK (your data)

# Attacker changes ID
GET /api/users/1235/profile → 200 OK (someone else's data!)
```

## Why IDOR Pays So Well

- **High impact:** Access to other users' private data
- **Easy to demonstrate:** Just change a number
- **Consistent payouts:** $500-$25,000 across platforms
- **High frequency:** Found in almost every web application

## Types of IDOR

### 1. Horizontal IDOR
Access another user's data at the same privilege level.
```
GET /api/orders/1001 → Your order
GET /api/orders/1002 → Someone else's order
```

### 2. Vertical IDOR
Access data at a higher privilege level.
```
GET /api/users/1234 → Your profile
GET /api/admin/settings → Admin settings (should be blocked)
```

### 3. Bulk IDOR
Access many users' data at once.
```
GET /api/users?id=1,2,3,4,5 → Multiple users' data
```

## Methodology

### Step 1: Create Two Accounts
- Account A (attacker)
- Account B (victim)

### Step 2: Map the Application
- Browse all features as Account A
- Note all API endpoints and parameters
- Record all IDs (user IDs, order IDs, message IDs, etc.)

### Step 3: Test Each Endpoint
For each endpoint that takes an ID parameter:

1. **Replace your ID with another user's ID**
2. **Change numeric IDs sequentially** (1001, 1002, 1003...)
3. **Test with UUIDs** (if applicable)
4. **Try negative numbers, zero, very large numbers**
5. **Test array parameters** (id[]=1&id[]=2)

### Step 4: Document Findings
- Record the exact request/response
- Show that Account B's data is accessible
- Explain the business impact

## Common IDOR Locations

| Location | Example |
|----------|---------|
| URL parameters | `/api/users/{id}` |
| POST body | `{"user_id": 1234}` |
| Cookies | `user_id=1234` |
| Headers | `X-User-ID: 1234` |
| GraphQL queries | `query { user(id: 1234) { email } }` |

## Tools for IDOR Hunting

### Manual Testing
```bash
# Test with Account A's token
curl -H "Authorization: Bearer TOKEN_A" \
  https://api.target.com/users/1234

# Test with Account B's ID
curl -H "Authorization: Bearer TOKEN_A" \
  https://api.target.com/users/1235
```

### Automated Testing
Use Burp Suite's Authz extension or custom scripts to swap tokens automatically.

## Real-World Examples

### Example 1: Order Access
```
GET /api/orders/1001 → Your order details
GET /api/orders/1002 → Someone else's order (name, address, items)
```
**Impact:** PII exposure, order manipulation
**Payout:** $500-$5,000

### Example 2: Message Access
```
GET /api/messages/5001 → Your messages
GET /api/messages/5002 → Someone else's private messages
```
**Impact:** Private communication exposure
**Payout:** $1,000-$10,000

### Example 3: Document Access
```
GET /api/documents/3001 → Your documents
GET /api/documents/3002 → Someone else's confidential documents
```
**Impact:** Confidential data exposure
**Payout:** $2,000-$25,000

## Tips for Success

1. **Focus on high-value endpoints** — orders, messages, documents, profiles
2. **Test both read and write** — can you also modify/delete?
3. **Check for IDOR in state-changing operations** — PUT, DELETE, POST
4. **Look for IDOR in exports** — CSV, PDF exports often leak data
5. **Test cross-tenant access** — can you access another organization's data?

## Report Template

```
Title: IDOR on /api/orders/{id} allows accessing any user's orders

Description:
The /api/orders/{id} endpoint does not verify that the
authenticated user owns the requested order ID. An attacker
can enumerate order IDs and access any user's order details.

Steps to Reproduce:
1. Log in as Account A (attacker)
2. Note your order ID: 1001
3. Change the ID to 1002 (victim's order)
4. Send: GET /api/orders/1002
5. Response contains victim's PII

Impact:
- Access to any user's order history
- PII exposure (name, address, phone, email)
- Potential for order manipulation

Remediation:
Verify that the authenticated user owns the requested
order ID before returning data.
```

---

*Happy hunting! Remember: IDOR is everywhere. You just need to look.*
