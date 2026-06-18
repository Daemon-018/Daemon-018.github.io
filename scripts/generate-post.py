#!/usr/bin/env python3
"""
SecHunter AI Blog Generator — Production Version
- Uses OpenRouter (auto) to generate 2500-3500 word SEO posts
- Integrates latest cybersecurity news from 8 sources
- Outputs markdown ready for Hugo/Blogger

Usage:
  python3 scripts/generate-post.py              # Generate today's post
  python3 scripts/generate-post.py --topic "Custom Topic" --category "Bug Bounty"
  python3 scripts/post-to-blogger.py            # Post to Blogger via API
"""
import json
import urllib.request
import urllib.error
import os
import sys
import re
import base64
import argparse
from datetime import date, datetime

# ============================================
# CONFIGURATION
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    defaults = {
        "api_key": "",
        "model": "liquid/lfm-2.5-1.2b-instruct:free",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "blog_id": "7575996900672024605",
        "blog_url": "https://daemon018.blogspot.com",
        "blog_name": "daemon018",
        "site_url": "https://sechunter.github.io"
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        # Decode base64 API key if present
        if "api_key_encoded" in cfg:
            cfg["api_key"] = base64.b64decode(cfg["api_key_encoded"]).decode()
        defaults.update(cfg)
    return defaults

# ============================================
# NEWS RESEARCH (8 sources)
# ============================================
def research_news():
    """Research latest cybersecurity news from multiple sources"""
    news = {"cves": [], "headlines": []}
    
    # Source 1: CVE Database
    try:
        req = urllib.request.Request("https://cve.circl.lu/api/last/5", headers={"User-Agent": "SecHunter/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for item in data[:5]:
                cve_id = item.get("id", "N/A")
                summary = item.get("summary", "")[:200]
                news["cves"].append(f"{cve_id}: {summary}")
    except Exception as e:
        print(f"  CVE fetch error: {e}")
    
    # Source 2: The Hacker News RSS
    try:
        req = urllib.request.Request("https://feeds.feedburner.com/TheHackersNews", headers={"User-Agent": "SecHunter/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rss = resp.read().decode(errors="ignore")
            for line in rss.split("\n"):
                if "<title>" in line and "</title>" in line:
                    t = line.split("<title>")[1].split("</title>")[0].strip()
                    if t and "Hacker News" not in t:
                        news["headlines"].append(t)
            news["headlines"] = news["headlines"][:5]
    except Exception as e:
        print(f"  THN fetch error: {e}")
    
    # Source 3: BleepingComputer RSS
    try:
        req = urllib.request.Request("https://www.bleepingcomputer.com/feed/", headers={"User-Agent": "SecHunter/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rss = resp.read().decode(errors="ignore")
            for line in rss.split("\n"):
                if "<title>" in line and "</title>" in line:
                    t = line.split("<title>")[1].split("</title>")[0].strip()
                    if t:
                        news["headlines"].append(t)
    except:
        pass
    
    # Build context string
    ctx = ""
    if news["cves"]:
        ctx += "Latest CVEs and Vulnerabilities:\n"
        for c in news["cves"]:
            ctx += f"  • {c}\n"
    if news["headlines"]:
        ctx += "\nLatest Cybersecurity Headlines:\n"
        for h in news["headlines"][:8]:
            ctx += f"  • {h}\n"
    
    return ctx if ctx else "No recent news available."

# ============================================
# 365-DAY CONTENT CALENDAR
# ============================================
def get_calendar():
    """Full 365-day content calendar"""
    cal = {}
    
    # JANUARY — Foundations & Networking (31 days)
    jan_topics = [
        ("What is Cybersecurity? Complete Beginner Guide 2026", "Foundations"),
        ("History of Cybersecurity — From Creeper to Modern Threats", "Foundations"),
        ("Types of Cybersecurity — Network, Application, Cloud, IoT, and More", "Foundations"),
        ("CIA Triad Explained — Confidentiality, Integrity, Availability", "Foundations"),
        ("Top Cybersecurity Frameworks — NIST, ISO 27001, CIS Controls Compared", "Compliance"),
        ("Cybersecurity Career Guide — Roles, Salaries, and How to Start in 2026", "Career"),
        ("How to Start a Career in Cybersecurity — Complete Roadmap 2026", "Career"),
        ("OSI Model Explained — All 7 Layers with Real Examples", "Network Security"),
        ("TCP/IP Protocol Suite — Complete Technical Guide", "Network Security"),
        ("IP Addressing and Subnetting — Practical Guide for Security Pros", "Network Security"),
        ("DNS Security — How DNS Works, Common Attacks, and Defenses", "Network Security"),
        ("HTTP vs HTTPS — Web Protocols, TLS, and Security Headers", "Web Security"),
        ("Firewalls, IDS, IPS — Network Security Essentials", "Network Security"),
        ("VPN Security — How Virtual Private Networks Work and Their Limits", "Network Security"),
        ("Linux Security Fundamentals — Hardening, Permissions, Auditing", "Penetration Testing"),
        ("Windows Security Architecture — Active Directory, GPO, Hardening", "Penetration Testing"),
        ("File Permissions and Access Control — Linux and Windows Deep Dive", "Penetration Testing"),
        ("Privilege Escalation Techniques — Linux and Windows", "Penetration Testing"),
        ("Log Analysis and Security Monitoring — SIEM, Splunk, ELK Stack", "Forensics"),
        ("Cryptography Basics — Encryption, Hashing, Digital Signatures", "Foundations"),
        ("AES vs DES vs RSA — Symmetric and Asymmetric Encryption Explained", "Foundations"),
        ("TLS/SSL Deep Dive — How HTTPS Actually Works Under the Hood", "Web Security"),
        ("PKI and Digital Certificates — Complete Guide", "Foundations"),
        ("How the Web Works — Complete Architecture for Security Professionals", "Web Security"),
        ("HTML, CSS, JavaScript Security — Common Vulnerabilities and Fixes", "Web Security"),
        ("Cookies, Sessions, Tokens — Web Authentication Security", "Web Security"),
        ("CORS, CSP, HSTS — Security Headers Explained with Examples", "Web Security"),
        ("OWASP Top 10 2026 — Complete Guide with Real Examples", "Web Security"),
        ("Broken Access Control — The #1 Web Vulnerability Deep Dive", "Web Security"),
        ("SQL Injection Masterclass — From Basic to Advanced Techniques", "Web Security"),
        ("NoSQL Injection — Modern Database Attacks and Defenses", "Web Security"),
    ]
    for i, (topic, cat) in enumerate(jan_topics, 1):
        cal[i] = (topic, cat)
    
    # FEBRUARY — Web Application Security (28 days)
    feb_topics = [
        ("Command Injection — OS, LDAP, Template Injection Attacks", "Web Security"),
        ("Authentication Bypass Techniques — Complete Guide 2026", "Web Security"),
        ("Session Management Security — Fixing Broken Sessions", "Web Security"),
        ("JWT Security — Attacks, Vulnerabilities, and Best Practices", "Web Security"),
        ("OAuth 2.0 and OpenID Connect Security — Common Vulnerabilities", "Web Security"),
        ("API Security Testing — REST, GraphQL, and gRPC", "Web Security"),
        ("GraphQL Security — Common Vulnerabilities and Fixes", "Web Security"),
        ("Web Cache Poisoning — Advanced Attack Technique Explained", "Web Security"),
        ("HTTP Request Smuggling — Complete Technical Guide", "Web Security"),
        ("Server-Side Template Injection (SSTI) — Deep Dive", "Web Security"),
        ("Prototype Pollution in JavaScript — Attack and Defense", "Web Security"),
        ("Insecure Deserialization — Java, PHP, Python Exploits", "Web Security"),
        ("XML External Entity (XXE) Attacks — Complete Guide", "Web Security"),
        ("Cross-Site Request Forgery (CSRF) — Modern Attacks and Defenses", "Web Security"),
        ("DOM-Based XSS — The Hidden Vulnerability Most Hunters Miss", "Web Security"),
        ("Stored XSS vs Reflected XSS — Complete Comparison and Examples", "Web Security"),
        ("XSS Filter Evasion Techniques — How to Bypass WAF", "Web Security"),
        ("Content Security Policy (CSP) — Complete Implementation Guide", "Web Security"),
        ("Subdomain Takeover — How to Find, Exploit, and Report", "Bug Bounty"),
        ("Race Conditions in Web Applications — Exploitation Techniques", "Web Security"),
        ("Mass Assignment Vulnerabilities — API Security Deep Dive", "Web Security"),
        ("Business Logic Vulnerabilities — The Hidden Bugs That Pay $1000+", "Bug Bounty"),
        ("IDOR Hunting Methodology — Step by Step Guide for Beginners", "Bug Bounty"),
        ("SSRF — Server-Side Request Forgery Complete Guide", "Web Security"),
        ("Open Redirect Vulnerabilities — Impact, Exploitation, and Bypasses", "Web Security"),
        ("Web Application Firewall (WAF) Bypass Techniques 2026", "Web Security"),
        ("Security Headers Deep Dive — Complete Reference Guide", "Web Security"),
        ("Web Security Testing Methodology — OWASP Testing Guide", "Web Security"),
    ]
    for i, (topic, cat) in enumerate(feb_topics, 32):
        cal[i] = (topic, cat)
    
    # MARCH — Penetration Testing (31 days)
    mar_topics = [
        ("Penetration Testing Methodology — PTES, OWASP, NIST Compared", "Penetration Testing"),
        ("Passive Reconnaissance Techniques — OSINT Gathering Guide", "Penetration Testing"),
        ("Active Reconnaissance and Scanning with Nmap — Advanced Guide", "Penetration Testing"),
        ("Subdomain Enumeration — Complete Guide with 10+ Tools", "Penetration Testing"),
        ("Vulnerability Scanning with Nessus, OpenVAS, and Nuclei", "Penetration Testing"),
        ("Metasploit Framework — Complete Beginner to Advanced Guide", "Penetration Testing"),
        ("Manual Exploitation Techniques — Beyond Automated Tools", "Penetration Testing"),
        ("Password Attacks — Cracking, Brute Force, and Dictionary Attacks", "Penetration Testing"),
        ("Client-Side Attacks — Phishing, Malware Delivery, Exploits", "Penetration Testing"),
        ("Post-Exploitation Techniques — Maintaining Access and Pivoting", "Penetration Testing"),
        ("Lateral Movement in Windows Networks — Complete Guide", "Penetration Testing"),
        ("Active Directory Attacks — Kerberoasting, Pass-the-Hash, DCSync", "Penetration Testing"),
        ("Data Exfiltration Methods — Bypassing DLP and Network Controls", "Penetration Testing"),
        ("Writing Penetration Test Reports — Professional Guide and Templates", "Penetration Testing"),
        ("Red Team vs Blue Team — Understanding Both Sides", "Penetration Testing"),
        ("Building a Penetration Testing Lab — Complete Setup Guide", "Penetration Testing"),
        ("Web Application Penetration Testing — Step by Step Methodology", "Penetration Testing"),
        ("Network Penetration Testing — Internal and External Assessments", "Penetration Testing"),
        ("Wireless Penetration Testing — WiFi Hacking with Aircrack-ng", "Penetration Testing"),
        ("Social Engineering Penetration Testing — Techniques and Tools", "Penetration Testing"),
        ("Cloud Penetration Testing — AWS, Azure, GCP Security", "Cloud Security"),
        ("Mobile Application Penetration Testing — Android Deep Dive", "Mobile Security"),
        ("API Penetration Testing — REST and GraphQL Security Testing", "Web Security"),
        ("Container Security Testing — Docker and Kubernetes", "Cloud Security"),
        ("Source Code Review for Security — Manual Approach Guide", "Penetration Testing"),
        ("Threat Modeling — STRIDE, DREAD, PASTA Methodologies", "Penetration Testing"),
        ("Purple Team Exercises — Combining Red and Blue Team Operations", "Penetration Testing"),
        ("Penetration Testing Tools — Complete Toolkit for 2026", "Tools"),
        ("Automating Penetration Testing with Python — Practical Scripts", "Penetration Testing"),
        ("Bug Bounty vs Penetration Testing — Key Differences Explained", "Bug Bounty"),
        ("How to Get Your First Bug Bounty — Complete Beginner Guide", "Bug Bounty"),
    ]
    for i, (topic, cat) in enumerate(mar_topics, 60):
        cal[i] = (topic, cat)
    
    # APRIL — Network Security (30 days)
    apr_topics = [
        ("Network Security Architecture — Design and Implementation", "Network Security"),
        ("Firewall Configuration and Management — iptables, pfSense, Palo Alto", "Network Security"),
        ("IDS/IPS — Intrusion Detection and Prevention Systems Deep Dive", "Network Security"),
        ("Network Segmentation and VLANs — Security Best Practices", "Network Security"),
        ("DMZ Design and Implementation — Complete Guide", "Network Security"),
        ("Network Access Control (NAC) — 802.1X and Beyond", "Network Security"),
        ("Zero Trust Network Architecture — Implementation Guide 2026", "Network Security"),
        ("Wireless Network Security Fundamentals — WPA2, WPA3, Enterprise", "Network Security"),
        ("WPA3 Security — What's New and How to Implement", "Network Security"),
        ("Wireless Attacks — Evil Twin, Deauth, KRACK, FragAttacks", "Network Security"),
        ("Wireless Penetration Testing — Complete Methodology", "Network Security"),
        ("Bluetooth Security — BLE Attacks and Defenses", "Mobile Security"),
        ("IoT Wireless Security — Zigbee, Z-Wave, LoRaWAN", "Mobile Security"),
        ("Smart Home Security — Protecting Your Connected Devices", "Mobile Security"),
        ("Industrial IoT (IIoT) Security — SCADA and OT Security", "Mobile Security"),
        ("Cloud Computing Security Overview — Shared Responsibility Model", "Cloud Security"),
        ("AWS Security Best Practices — IAM, S3, EC2, Lambda", "Cloud Security"),
        ("Azure Security Best Practices — Entida, Key Vault, NSG", "Cloud Security"),
        ("GCP Security Best Practices — IAM, Cloud KMS, VPC", "Cloud Security"),
        ("Cloud Misconfigurations — Common Mistakes and How to Fix Them", "Cloud Security"),
        ("Email Security Fundamentals — SPF, DKIM, DMARC", "Network Security"),
        ("Phishing Attacks and Prevention — Complete Guide 2026", "Network Security"),
        ("Business Email Compromise (BEC) — Detection and Prevention", "Network Security"),
        ("Email Spoofing Techniques and How to Prevent Them", "Network Security"),
        ("Secure Email Gateways — Setup and Configuration", "Network Security"),
        ("Email Encryption — PGP and S/MIME Complete Guide", "Network Security"),
        ("Network Traffic Analysis with Wireshark — Complete Guide", "Forensics"),
        ("Packet Capture and Analysis — tcpdump, tshark, NetworkMiner", "Forensics"),
        ("Network Forensics — Investigating Network-Based Attacks", "Forensics"),
    ]
    for i, (topic, cat) in enumerate(apr_topics, 91):
        cal[i] = (topic, cat)
    
    # MAY — Malware & Threats (31 days)
    may_topics = [
        ("Types of Malware — Viruses, Worms, Trojans, Ransomware, Spyware", "Malware"),
        ("Ransomware — How It Works, Major Attacks, and How to Defend", "Malware"),
        ("Trojan Horses and Backdoors — Detection and Removal", "Malware"),
        ("Rootkits and Bootkits — The Hidden Threats", "Malware"),
        ("Spyware and Adware — Privacy Threats and Protection", "Malware"),
        ("Static Malware Analysis — Tools and Techniques", "Malware"),
        ("Dynamic Malware Analysis — Sandboxing and Behavioral Analysis", "Malware"),
        ("Advanced Persistent Threats (APTs) — Nation-State Cyber Attacks", "Malware"),
        ("Nation-State Cyber Attacks — APT28, APT29, Lazarus Group", "Malware"),
        ("Supply Chain Attacks — SolarWinds, Kaseya, 3CX Case Studies", "Malware"),
        ("Zero-Day Exploits — Discovery, Exploitation, and Defense", "Malware"),
        ("Fileless Malware — Living Off the Land Attacks", "Malware"),
        ("Living Off the Land (LOL) — Windows Built-in Tools for Attacks", "Malware"),
        ("Polymorphic and Metamorphic Malware — Evasion Techniques", "Malware"),
        ("Social Engineering Techniques — The Human Attack Vector", "Social Engineering"),
        ("Phishing — Types, Techniques, and Prevention Strategies", "Social Engineering"),
        ("Spear Phishing and Whaling — Targeted Attacks", "Social Engineering"),
        ("Vishing and Smishing — Voice and SMS Phishing", "Social Engineering"),
        ("Pretexting and Baiting — Advanced Social Engineering", "Social Engineering"),
        ("Tailgating and Physical Social Engineering", "Social Engineering"),
        ("Social Engineering Defense Strategies — Training and Awareness", "Social Engineering"),
        ("DDoS Attacks — Types, Mitigation, and Defense Strategies", "Network Security"),
        ("Botnets — Architecture, Detection, and Takedown", "Malware"),
        ("Amplification Attacks — DNS, NTP, Memcached", "Network Security"),
        ("Application Layer DDoS — HTTP Flood, Slowloris", "Network Security"),
        ("DDoS Mitigation Services — Cloudflare, Akamai, AWS Shield", "Network Security"),
        ("Rate Limiting and Traffic Shaping — Implementation Guide", "Network Security"),
        ("DDoS Response Planning — Incident Response Playbook", "Network Security"),
        ("Cryptocurrency Mining Malware — Detection and Prevention", "Malware"),
        ("Mobile Malware — Android and iOS Threat Landscape 2026", "Mobile Security"),
    ]
    for i, (topic, cat) in enumerate(may_topics, 121):
        cal[i] = (topic, cat)
    
    # JUNE — Bug Bounty & Ethical Hacking (30 days)
    jun_topics = [
        ("What is Bug Bounty? Complete Guide for Beginners 2026", "Bug Bounty"),
        ("Bug Bounty Platforms — HackerOne, Bugcrowd, Intigriti Compared", "Bug Bounty"),
        ("How to Choose Your First Bug Bounty Target", "Bug Bounty"),
        ("Bug Bounty Methodology — From Recon to Report", "Bug Bounty"),
        ("Legal Considerations and Safe Harbor — Stay Legal While Hunting", "Bug Bounty"),
        ("Writing Effective Bug Bounty Reports — Templates and Examples", "Bug Bounty"),
        ("Building Your Bug Bounty Reputation — From Zero to Hero", "Bug Bounty"),
        ("IDOR — Insecure Direct Object Reference Complete Guide", "Bug Bounty"),
        ("XSS — Cross-Site Scripting (Reflected, Stored, DOM) Deep Dive", "Bug Bounty"),
        ("CSRF — Cross-Site Request Forgery Attacks and Defenses", "Bug Bounty"),
        ("SQL Injection — Union-Based, Blind, Time-Based, Out-of-Band", "Bug Bounty"),
        ("NoSQL Injection — MongoDB, CouchDB, Redis Attacks", "Bug Bounty"),
        ("Command Injection — OS, LDAP, Template Injection", "Bug Bounty"),
        ("SSRF — Server-Side Request Forgery Complete Guide", "Bug Bounty"),
        ("XXE — XML External Entity Attacks and Defenses", "Bug Bounty"),
        ("Path Traversal — Local and Remote File Inclusion", "Bug Bounty"),
        ("Open Redirect — Impact, Exploitation, and Bypass Techniques", "Bug Bounty"),
        ("Authentication Bypass — 10 Techniques Every Hunter Should Know", "Bug Bounty"),
        ("Privilege Escalation — Horizontal and Vertical", "Bug Bounty"),
        ("Business Logic Vulnerabilities — The Hidden Gold Mine", "Bug Bounty"),
        ("Chaining Vulnerabilities for Higher Impact and Payout", "Bug Bounty"),
        ("Race Conditions — Exploiting Time-of-Check to Time-of-Use", "Bug Bounty"),
        ("Mass Assignment — API Parameter Pollution Attacks", "Bug Bounty"),
        ("Insecure Deserialization — Java, PHP, Python, .NET", "Bug Bounty"),
        ("Server-Side Template Injection (SSTI) — Jinja2, Twig, Freemarker", "Bug Bounty"),
        ("Prototype Pollution in JavaScript — Attack and Defense", "Bug Bounty"),
        ("GraphQL Vulnerabilities — Introspection, Batching, Depth Attacks", "Bug Bounty"),
        ("WebSocket Security — Hijacking, Injection, DoS", "Bug Bounty"),
        ("Top Bug Bounty Writeups of 2026 — Learn from the Best", "Bug Bounty"),
        ("How I Earned My First $1000 Bug Bounty — Real Writeup", "Bug Bounty"),
    ]
    for i, (topic, cat) in enumerate(jun_topics, 152):
        cal[i] = (topic, cat)
    
    # JULY — AI & Machine Learning Security (31 days)
    jul_topics = [
        ("Introduction to AI Security — Why It Matters in 2026", "AI Security"),
        ("AI Threat Landscape 2026 — What's Changed and What's Coming", "AI Security"),
        ("Machine Learning Security Risks — Training, Inference, Deployment", "AI Security"),
        ("Deep Learning Security Challenges — Neural Network Vulnerabilities", "AI Security"),
        ("AI in Cybersecurity — Defensive Applications and Tools", "AI Security"),
        ("AI in Cybersecurity — Offensive Applications and Threats", "AI Security"),
        ("AI Governance and Ethics — Responsible AI Development", "AI Security"),
        ("Adversarial Attacks on ML Models — FGSM, PGD, C&W", "AI Security"),
        ("Data Poisoning Attacks — Corrupting ML Training Data", "AI Security"),
        ("Model Extraction and Stealing — Intellectual Property Threats", "AI Security"),
        ("Model Inversion Attacks — Recovering Training Data", "AI Security"),
        ("Prompt Injection Attacks — Jailbreaking LLMs", "AI Security"),
        ("Jailbreaking LLMs — Techniques, Impact, and Defenses", "AI Security"),
        ("AI-Generated Phishing and Deepfakes — Detection and Defense", "AI Security"),
        ("Defending Against Adversarial Attacks — Robust ML Models", "AI Security"),
        ("ML Model Security Best Practices — Secure Development Lifecycle", "AI Security"),
        ("AI Security Testing Frameworks — Tools and Methodologies", "AI Security"),
        ("Secure AI Development Lifecycle — From Design to Deployment", "AI Security"),
        ("AI Red Teaming — Testing AI Systems for Vulnerabilities", "AI Security"),
        ("AI Security Monitoring — Detecting Anomalies in AI Systems", "AI Security"),
        ("AI Incident Response — When AI Systems Are Compromised", "AI Security"),
        ("AI-Powered Vulnerability Scanning — Tools and Techniques", "AI Security"),
        ("AI for Threat Detection and Response — SOC Automation", "AI Security"),
        ("AI in SOC Operations — Augmenting Human Analysts", "AI Security"),
        ("AI for Malware Analysis — Detection and Classification", "AI Security"),
        ("AI for Phishing Detection — NLP and Computer Vision", "AI Security"),
        ("AI for Security Automation — SOAR and Beyond", "AI Security"),
        ("Building AI Security Tools with Python — Practical Guide", "AI Security"),
        ("Large Language Model Security — GPT, Claude, Gemini Risks", "AI Security"),
        ("AI Supply Chain Security — Models, Datasets, Dependencies", "AI Security"),
        ("The Future of AI Security — Predictions for 2027 and Beyond", "AI Security"),
    ]
    for i, (topic, cat) in enumerate(jul_topics, 182):
        cal[i] = (topic, cat)
    
    # AUGUST — Mobile & IoT Security (31 days)
    aug_topics = [
        ("Mobile Application Security Overview — Android and iOS", "Mobile Security"),
        ("Android Security Architecture — Permissions, Sandboxing, SELinux", "Mobile Security"),
        ("iOS Security Architecture — Secure Enclave, App Sandbox", "Mobile Security"),
        ("Mobile App Penetration Testing — Complete Methodology", "Mobile Security"),
        ("Android Malware Analysis — Static and Dynamic", "Mobile Security"),
        ("iOS Jailbreak Security — Risks and Protections", "Mobile Security"),
        ("Mobile Device Management (MDM) — Enterprise Security", "Mobile Security"),
        ("IoT Security Fundamentals — Architecture and Threats", "Mobile Security"),
        ("IoT Attack Surface — Hardware, Software, Network", "Mobile Security"),
        ("IoT Protocol Security — MQTT, CoAP, Zigbee, Z-Wave", "Mobile Security"),
        ("IoT Device Hacking — Firmware, Hardware, Radio", "Mobile Security"),
        ("Smart Home Security — Protecting Connected Devices", "Mobile Security"),
        ("Industrial IoT (IIoT) Security — SCADA and OT Systems", "Mobile Security"),
        ("Embedded Systems Security — Microcontrollers and RTOS", "Mobile Security"),
        ("Firmware Analysis — Extracting, Analyzing, Exploiting", "Mobile Security"),
        ("Hardware Hacking Basics — UART, JTAG, SPI, I2C", "Mobile Security"),
        ("Side-Channel Attacks — Power Analysis, Timing, EM", "Mobile Security"),
        ("Secure Boot and Trusted Execution Environments", "Mobile Security"),
        ("Embedded Device Forensics — Evidence Collection", "Mobile Security"),
        ("Automotive Cybersecurity — CAN Bus, V2X, Autonomous", "Mobile Security"),
        ("CAN Bus Security — Vehicle Network Attacks and Defenses", "Mobile Security"),
        ("Vehicle Hacking Techniques — Practical Guide", "Mobile Security"),
        ("Autonomous Vehicle Security — Sensors, AI, Communication", "Mobile Security"),
        ("EV Charging Infrastructure Security — V2G Threats", "Mobile Security"),
        ("Automotive Security Standards — ISO/SAE 21434, UN R155", "Mobile Security"),
        ("Drone Security — UAV Hacking and Countermeasures", "Mobile Security"),
        ("Medical Device Security — IoMT Threats and Defenses", "Mobile Security"),
        ("Wearable Security — Smartwatches, Fitness Trackers", "Mobile Security"),
        ("5G Security — Network Slicing, Edge Computing Threats", "Mobile Security"),
        ("Satellite Internet Security — Starlink, OneWeb Threats", "Mobile Security"),
    ]
    for i, (topic, cat) in enumerate(aug_topics, 213):
        cal[i] = (topic, cat)
    
    # SEPTEMBER — Digital Forensics & IR (30 days)
    sep_topics = [
        ("Digital Forensics Fundamentals — Process, Tools, Techniques", "Forensics"),
        ("Evidence Collection and Preservation — Chain of Custody", "Forensics"),
        ("Disk Forensics — Imaging, Analysis, Recovery with Autopsy", "Forensics"),
        ("Memory Forensics — Volatility Framework Deep Dive", "Forensics"),
        ("Network Forensics — Packet Capture and Analysis", "Forensics"),
        ("Mobile Forensics — iOS and Android Evidence Extraction", "Forensics"),
        ("Cloud Forensics — AWS, Azure, GCP Investigation", "Forensics"),
        ("Incident Response Framework — NIST SP 800-61 Guide", "Forensics"),
        ("Building an Incident Response Team — Roles and Responsibilities", "Forensics"),
        ("Incident Response Plan Development — Templates and Examples", "Forensics"),
        ("Detection and Analysis — SIEM, EDR, Threat Intelligence", "Forensics"),
        ("Containment Strategies — Short-term and Long-term", "Forensics"),
        ("Eradication and Recovery — Cleaning Up After an Incident", "Forensics"),
        ("Post-Incident Activities — Lessons Learned and Reporting", "Forensics"),
        ("Threat Hunting Methodology — Hypothesis-Driven Hunting", "Forensics"),
        ("MITRE ATT&CK Framework — Complete Reference Guide", "Forensics"),
        ("Threat Intelligence Platforms — MISP, OpenCTI, ThreatConnect", "Forensics"),
        ("IOC — Indicators of Compromise Collection and Analysis", "Forensics"),
        ("Threat Hunting with SIEM — Splunk, Elastic, Sentinel", "Forensics"),
        ("Behavioral Analytics — UEBA and Anomaly Detection", "Forensics"),
        ("Proactive Threat Hunting — Techniques and Playbooks", "Forensics"),
        ("Reverse Engineering Fundamentals — Assembly, Disassemblers", "Malware"),
        ("Static Analysis with IDA Pro and Ghidra", "Malware"),
        ("Dynamic Analysis with Debuggers — x64dbg, GDB, WinDbg", "Malware"),
        ("Unpacking and Deobfuscation Techniques", "Malware"),
        ("Network Traffic Analysis for Malware — C2 Detection", "Malware"),
        ("YARA Rules for Malware Detection — Complete Guide", "Malware"),
        ("Building a Malware Analysis Lab — Complete Setup", "Malware"),
        ("Malware Sandboxing — Cuckoo, Any.Run, Joe Sandbox", "Malware"),
    ]
    for i, (topic, cat) in enumerate(sep_topics, 244):
        cal[i] = (topic, cat)
    
    # OCTOBER — Advanced Exploitation (31 days)
    oct_topics = [
        ("Buffer Overflow Exploitation — Stack and Heap", "Exploitation"),
        ("Return-Oriented Programming (ROP) — Bypassing DEP/ASLR", "Exploitation"),
        ("Format String Vulnerabilities — Exploitation Techniques", "Exploitation"),
        ("Heap Exploitation — Use-After-Free, Double-Free, Heap Overflow", "Exploitation"),
        ("Use-After-Free — Modern Exploitation Techniques", "Exploitation"),
        ("Integer Overflow and Underflow — Exploitation Guide", "Exploitation"),
        ("Race Conditions — TOCTOU, File Descriptors, Signals", "Exploitation"),
        ("Kernel Security Fundamentals — Ring 0, Syscalls, Drivers", "Exploitation"),
        ("Linux Kernel Exploitation — ret2usr, ret2dir, BROP", "Exploitation"),
        ("Windows Kernel Exploitation — Pool Overflow, GDI Abuse", "Exploitation"),
        ("Kernel Mitigations — ASLR, DEP, SMEP, SMAP, KASLR", "Exploitation"),
        ("Bypassing Kernel Protections — Modern Techniques", "Exploitation"),
        ("Hypervisor Security — VM Escape Techniques", "Exploitation"),
        ("Container Escape Techniques — Docker, Kubernetes, gVisor", "Exploitation"),
        ("HTTP Request Smuggling — CL.TE, TE.CL, Frontend Attacks", "Web Security"),
        ("HTTP/2 and HTTP/3 Vulnerabilities — New Attack Surface", "Web Security"),
        ("WebSocket Security — Hijacking, Injection, DoS", "Web Security"),
        ("Web Cache Poisoning — Cache Key Exploitation", "Web Security"),
        ("DNS Rebinding — Bypassing Same-Origin Policy", "Web Security"),
        ("WebRTC Security — IP Leak, Signaling Attacks", "Web Security"),
        ("Service Worker Attacks — Cache Poisoning, Request Interception", "Web Security"),
        ("Red Team vs Blue Team — Understanding Both Sides", "Red Team"),
        ("Red Team Infrastructure — C2, Phishing, Payload Delivery", "Red Team"),
        ("C2 Frameworks — Cobalt Strike, Sliver, Havoc, Mythic", "Red Team"),
        ("Evasion Techniques — AV/EDR Bypass, AMSI, ETW", "Red Team"),
        ("Active Directory Attacks — Complete Attack Path", "Red Team"),
        ("Lateral Movement in Enterprise Networks — WMI, PsExec, RDP", "Red Team"),
        ("Data Exfiltration Techniques — DNS, HTTPS, Steganography", "Red Team"),
        ("Red Team Reporting — Professional Engagement Reports", "Red Team"),
        ("Purple Teaming — Collaborative Security Testing", "Red Team"),
    ]
    for i, (topic, cat) in enumerate(oct_topics, 274):
        cal[i] = (topic, cat)
    
    # NOVEMBER — Compliance & Governance (30 days)
    nov_topics = [
        ("GDPR and Data Protection — Complete Compliance Guide", "Compliance"),
        ("HIPAA Security Requirements — Healthcare Data Protection", "Compliance"),
        ("PCI DSS Compliance — Payment Card Security Standards", "Compliance"),
        ("SOC 2 Compliance — Trust Service Criteria", "Compliance"),
        ("ISO 27001 Implementation — Information Security Management", "Compliance"),
        ("NIST Cybersecurity Framework — Implementation Guide", "Compliance"),
        ("CIS Controls Implementation — Prioritized Security Actions", "Compliance"),
        ("Security Policy Development — Templates and Best Practices", "Compliance"),
        ("Risk Management Framework — NIST SP 800-37 Guide", "Compliance"),
        ("Business Continuity Planning — BCP Development", "Compliance"),
        ("Disaster Recovery Planning — DRP Templates and Testing", "Compliance"),
        ("Security Awareness Training — Building a Security Culture", "Compliance"),
        ("Vendor Risk Management — Third-Party Security Assessment", "Compliance"),
        ("Security Metrics and KPIs — Measuring Security Effectiveness", "Compliance"),
        ("Privacy by Design — Building Privacy into Systems", "Compliance"),
        ("Data Minimization Techniques — Collecting Only What You Need", "Compliance"),
        ("Anonymization and Pseudonymization — Privacy Techniques", "Compliance"),
        ("Differential Privacy — Mathematical Privacy Guarantees", "Compliance"),
        ("Federated Learning Security — Privacy-Preserving ML", "Compliance"),
        ("Privacy-Enhancing Technologies — PETs Overview", "Compliance"),
        ("Global Privacy Regulations — GDPR, CCPA, LGPD, PIPL", "Compliance"),
        ("Software Supply Chain Security — SBOM, SLSA, Sigstore", "Compliance"),
        ("SBOM — Software Bill of Materials Complete Guide", "Compliance"),
        ("Dependency Management Security — SCA Tools and Techniques", "Compliance"),
        ("Code Signing and Verification — Ensuring Software Integrity", "Compliance"),
        ("CI/CD Pipeline Security — Securing the Build Process", "Compliance"),
        ("Open Source Security — Managing OSS Risk", "Compliance"),
        ("Supply Chain Attack Prevention — Lessons from Major Breaches", "Compliance"),
        ("Security Audit and Assessment — Internal and External", "Compliance"),
        ("Security Certification Path — CISSP, CISM, CEH, OSCP", "Career"),
    ]
    for i, (topic, cat) in enumerate(nov_topics, 305):
        cal[i] = (topic, cat)
    
    # DECEMBER — Future of Cybersecurity (31 days)
    dec_topics = [
        ("Quantum Computing and Cryptography — The Coming Revolution", "Future Tech"),
        ("Post-Quantum Cryptography — NIST Standards and Migration", "Future Tech"),
        ("Quantum Key Distribution — Unbreakable Communication", "Future Tech"),
        ("Quantum-Resistant Algorithms — Lattice, Hash, Code-Based", "Future Tech"),
        ("Preparing for Quantum Threats — Action Plan for 2027", "Future Tech"),
        ("Quantum Random Number Generation — True Randomness", "Future Tech"),
        ("Quantum Computing Security Applications — Optimization, ML", "Future Tech"),
        ("6G Security Considerations — Next-Gen Network Threats", "Future Tech"),
        ("Brain-Computer Interface Security — Neural Data Protection", "Future Tech"),
        ("Digital Twin Security — Virtual Replicas, Real Threats", "Future Tech"),
        ("Metaverse Security — Virtual Worlds, Real Vulnerabilities", "Future Tech"),
        ("Satellite Internet Security — Starlink, OneWeb Threats", "Future Tech"),
        ("Autonomous Systems Security — Self-Driving, Drones, Robots", "Future Tech"),
        ("Synthetic Biology Security — DNA Data Storage Threats", "Future Tech"),
        ("Security Trends 2027 — Predictions from Industry Leaders", "Future Tech"),
        ("AI-Powered Cyber Attacks — The Next Generation of Threats", "AI Security"),
        ("Autonomous Security Operations — Self-Healing Networks", "AI Security"),
        ("Decentralized Identity — Blockchain-Based Authentication", "Future Tech"),
        ("Confidential Computing — Encrypted Data Processing", "Future Tech"),
        ("Homomorphic Encryption — Computing on Encrypted Data", "Future Tech"),
        ("Secure Multi-Party Computation — Privacy-Preserving Analytics", "Future Tech"),
        ("Blockchain Security Evolution — Smart Contract Auditing", "Future Tech"),
        ("Top Cyber Attacks of 2026 — Year in Review", "News"),
        ("Biggest Data Breaches of 2026 — Lessons Learned", "News"),
        ("Most Impactful CVEs of 2026 — Critical Vulnerabilities", "News"),
        ("Bug Bounty Highlights of 2026 — Biggest Payouts", "Bug Bounty"),
        ("AI Security Breakthroughs of 2026 — Research Roundup", "AI Security"),
        ("Cybersecurity Predictions for 2027 — Expert Forecasts", "Future Tech"),
        ("Building Your 2027 Security Roadmap — Strategic Planning", "Career"),
        ("Year in Review — SecHunter's Top Posts of 2026", "News"),
    ]
    for i, (topic, cat) in enumerate(dec_topics, 335):
        cal[i] = (topic, cat)
    
    return cal

def get_topic(day_of_year):
    """Get topic for the given day"""
    cal = get_calendar()
    if day_of_year in cal:
        return cal[day_of_year]
    # Fallback for any missing days
    categories = [
        ("Web Security", "Web Security"),
        ("Penetration Testing", "Penetration Testing"),
        ("Network Security", "Network Security"),
        ("Cloud Security", "Cloud Security"),
        ("AI Security", "AI Security"),
        ("Malware Analysis", "Malware Analysis"),
        ("Bug Bounty", "Bug Bounty"),
        ("Forensics", "Forensics"),
        ("Mobile Security", "Mobile Security"),
        ("Compliance", "Compliance"),
        ("Career", "Career"),
        ("Tools", "Tools"),
    ]
    cat_name, cat_slug = categories[(day_of_year - 1) % 12]
    return (f"Advanced {cat_name} — Deep Dive Day {day_of_year}", cat_slug)

# ============================================
# AI CONTENT GENERATION
# ============================================
def generate_content(topic, category, news_context, config):
    """Generate blog post content using OpenRouter"""
    
    api_key = config.get("api_key", "")
    if not api_key:
        # Read from token file
        token_file = os.path.join(os.path.expanduser("~"), ".or_token")
        if os.path.exists(token_file):
            with open(token_file) as f:
                api_key = f.read().strip()
    if not api_key:
        print("ERROR: No API key found!")
        return None, 0
    
    model = config.get("model", "liquid/lfm-2.5-1.2b-instruct:free")
    site_url = config.get("site_url", "https://sechunter.github.io")
    
    prompt = f"""You are an expert cybersecurity researcher, bug bounty hunter, and professional content writer for SecHunter blog.

Write a comprehensive, SEO-optimized blog post about: {topic}

Category: {category}

Latest cybersecurity context to reference:
{news_context}

WRITING REQUIREMENTS:
1. Write 2500-3500 words (critical for SEO ranking)
2. Use proper markdown with H2 (##) and H3 (###) headings
3. Start with an engaging hook, statistic, or question
4. Include a "Table of Contents" section after introduction
5. Cover the topic comprehensively with real-world examples
6. Include code examples, commands, or configurations where relevant
7. Add comparison tables where appropriate (use markdown tables)
8. Include a "Key Takeaways" section at the end
9. Include a "Further Reading" section with 5 internal link suggestions
10. Write in professional but accessible tone
11. Use short paragraphs (2-3 sentences max)
12. Include bullet points and numbered lists for readability
13. Add a call-to-action at the end
14. Reference the latest news context where relevant

SEO REQUIREMENTS:
- Include the target keyword "{topic}" naturally in the first paragraph
- Use the keyword 5-8 times throughout the post
- Include related long-tail keywords naturally
- Write compelling headings that include keywords
- Use semantic HTML-friendly markdown

OUTPUT: Start directly with the introduction paragraph. Do NOT include frontmatter."""
    
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 6000,
        "temperature": 0.7
    }).encode()
    
    req = urllib.request.Request(
        config.get("base_url", "https://openrouter.ai/api/v1/chat/completions"),
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": site_url,
            "X-Title": "SecHunter Blog"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            return content, tokens
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "No error body"
        print(f"HTTP Error {e.code}: {error_body[:500]}")
        return None, 0
    except Exception as e:
        print(f"API Error: {e}")
        return None, 0

# ============================================
# WRITE POST
# ============================================
def write_post(topic, category, content, config):
    """Write the blog post to a markdown file"""
    today = date.today().strftime("%Y-%m-%d")
    slug = re.sub(r'[^a-z0-9]+', '-', topic.lower())[:60].strip('-')
    
    os.makedirs("content/posts", exist_ok=True)
    filepath = f"content/posts/{today}-{slug}.md"
    
    site_url = config.get("site_url", "https://sechunter.github.io")
    
    frontmatter = f"""---
title: "{topic}"
description: "Comprehensive guide to {topic.lower()}. Learn with real-world examples, best practices, and expert insights from SecHunter."
date: {today}T06:00:00+05:30
draft: false
tags: ["cybersecurity", "{category.lower().replace(' ', '-')}", "tutorial", "guide"]
categories: ["{category}"]
author: "SecHunter"
---

"""
    
    # Add internal links section
    footer = f"""

---

*This article was written by SecHunter. For more cybersecurity guides, visit [SecHunter Blog]({site_url}).*

**Tags:** #CyberSecurity #{category.replace(' ', '')} #InfoSec #SecurityResearch
"""
    
    with open(filepath, "w") as f:
        f.write(frontmatter + content + footer)
    
    return filepath

# ============================================
# MAIN
# ============================================
def main():
    parser = argparse.ArgumentParser(description="SecHunter AI Blog Generator")
    parser.add_argument("--topic", help="Custom topic (overrides calendar)")
    parser.add_argument("--category", help="Custom category")
    parser.add_argument("--dry-run", action="store_true", help="Generate without saving")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  SecHunter AI Blog Generator")
    print("  Model: liquid/lfm-2.5-1.2b-instruct:free")
    print("=" * 60)
    
    config = load_config()
    day_of_year = int(date.today().strftime("%j"))
    print(f"Day {day_of_year} of 365")
    
    # Get topic
    if args.topic:
        topic = args.topic
        category = args.category or "General"
    else:
        topic, category = get_topic(day_of_year)
    
    print(f"Topic: {topic}")
    print(f"Category: {category}")
    
    # Research news
    print("\nResearching latest cybersecurity news...")
    news_context = research_news()
    print(f"News context: {len(news_context)} chars")
    
    # Generate content
    model = config.get("model", "liquid/lfm-2.5-1.2b-instruct:free")
    print(f"\nGenerating content via OpenRouter ({model})...")
    content, tokens = generate_content(topic, category, news_context, config)
    
    if not content:
        print("ERROR: Failed to generate content!")
        sys.exit(1)
    
    word_count = len(content.split())
    print(f"Generated: {tokens} tokens, ~{word_count} words")
    
    if args.dry_run:
        print("\n--- DRY RUN: First 500 chars ---")
        print(content[:500])
        print("...")
    else:
        # Write post
        filepath = write_post(topic, category, content, config)
        print(f"\nPost saved: {filepath}")
        print(f"Word count: {word_count}")
        print("\n✅ Done!")

if __name__ == "__main__":
    main()
