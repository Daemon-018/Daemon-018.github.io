#!/usr/bin/env python3
"""Add OpenRouter API key as GitHub secret"""
import json
import urllib.request
import urllib.error
import base64
import os
from nacl import encoding, public

# Read token
with open(os.path.expanduser("~/.gh_token")) as f:
    gh_token = f.read().strip()

# Read API key
with open(os.path.expanduser("~/.or_token")) as f:
    api_key = f.read().strip()

# Get repository public key
url = "https://api.github.com/repos/Daemon-018/Daemon-018.github.io/actions/secrets/public-key"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {gh_token}"})
with urllib.request.urlopen(req, timeout=15) as resp:
    pub_key_data = json.loads(resp.read())

key_id = pub_key_data["key_id"]
public_key = pub_key_data["key"]

# Encrypt the secret
public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
sealed_box = public.Box(public_key, public.PrivateKey.generate())
encrypted = sealed_box.encrypt(api_key.encode("utf-8"), encoder=encoding.Base64Encoder())
encrypted_value = encrypted.decode("utf-8")

# Set the secret
url = "https://api.github.com/repos/Daemon-018/Daemon-018.github.io/actions/secrets/OPENROUTER_API_KEY"
payload = json.dumps({
    "encrypted_value": encrypted_value,
    "key_id": key_id
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Authorization": f"Bearer {gh_token}",
    "Content-Type": "application/json"
}, method="PUT")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("✅ OpenRouter API key added as GitHub secret!")
        print("Secret name: OPENROUTER_API_KEY")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Error {e.code}: {body[:300]}")
except Exception as e:
    print(f"Error: {e}")
