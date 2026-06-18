---
title: "How I Found My First $500 Bug — IDOR on a Popular Platform"
description: "A writeup of my first real bug bounty finding. How I found an IDOR vulnerability that earned me $500."
date: 2026-06-17
draft: false
tags: ["writeup", "idor", "bug-bounty", "first-bounty"]
categories: ["Writeups", "Bug Bounty"]
---

# How I Found My First $500 Bug

Everyone remembers their first bounty. Here's how I found an IDOR vulnerability that earned me $500 on my first serious hunting attempt.

## The Target

A popular SaaS platform with a bug bounty program on HackerOne. The program had a $500 minimum bounty for medium-severity findings.

## The Recon

I started by creating two accounts:
- **Account A** (attacker): testuser1@mailinator.com
- **Account B** (victim): testuser2@mailinator.com

I mapped the application by browsing every feature:
- User profiles
- Projects
- Messages
- Documents
- Settings
- API endpoints (from JS bundles)

## The Discovery

While testing the messaging feature, I noticed an API endpoint:
```
GET /api/messages/{message_id}
```

I sent a message from Account A and noted the message ID: `12345`

Then I logged in as Account B and tried to access Account A's message:
```
GET /api/messages/12345
```

**It worked.** I could see Account A's private messages.

## The Impact

- Any user could read any other user's private messages
- Messages contained sensitive business information
- No authentication check on the message ID parameter

## The Report

```
Title: IDOR on /api/messages/{id} allows reading any user's private messages

Description:
The /api/messages/{id} endpoint does not verify message ownership.
Any authenticated user can read any other user's private messages
by changing the message ID.

Steps to Reproduce:
1. Log in as Account A
2. Send a message, note the message ID (e.g., 12345)
3. Log in as Account B
4. Send: GET /api/messages/12345
5. Response contains Account A's private message

Impact:
- Private message exposure
- Sensitive business information leakage
- Affects all users on the platform

Remediation:
Verify that the authenticated user is either the sender
or recipient of the message before returning data.
```

## The Result

- **Status:** Triaged within 24 hours
- **Severity:** Medium
- **Bounty:** $500
- **Time to payout:** 2 weeks

## Lessons Learned

1. **Always create 2 accounts** — IDOR testing requires it
2. **Map everything** — The more endpoints you test, the more bugs you find
3. **Check every ID parameter** — URLs, POST bodies, cookies, headers
4. **Write clear reports** — Triage teams love step-by-step PoCs
5. **Don't give up** — My first 5 targets had no bugs. The 6th did.

## Your Turn

You can find IDOR vulnerabilities too. Here's what you need:
1. A HackerOne account (free)
2. A target with a public program
3. Two test accounts
4. curl or Burp Suite
5. Patience

**Start hunting today. Your first $500 is closer than you think.**
