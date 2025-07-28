#!/usr/bin/env python3
"""
Deployment Verification Script for XMRT Eliza on Render
This script checks the status of all services deployed on Render
"""

import requests
import json
import time
import sys
import os

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def check_service_status(url):
    """Check if a service is online by making a GET request"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code < 300:
            return True, response.status_code
        return False, response.status_code
    except Exception as e:
        return False, str(e)

def main():
    print(f"{Colors.HEADER}XMRT Eliza Deployment Verification{Colors.ENDC}")
    print(f"{Colors.BOLD}Checking service status...{Colors.ENDC}")

    # Replace these URLs with your actual deployed service URLs
    services = {
        "Frontend": "FRONTEND_URL_HERE",
        "Backend API": "BACKEND_API_URL_HERE",
        "Eliza AI Service": "ELIZA_AI_URL_HERE"
    }

    all_ok = True

    for name, url in services.items():
        if url == "FRONTEND_URL_HERE" or url == "BACKEND_API_URL_HERE" or url == "ELIZA_AI_URL_HERE":
            print(f"{Colors.WARNING}⚠️ {name}: URL not configured{Colors.ENDC}")
            all_ok = False
            continue

        print(f"Checking {name} ({url})...")
        online, status = check_service_status(url)

        if online:
            print(f"{Colors.GREEN}✅ {name}: Online (Status: {status}){Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ {name}: Offline (Status: {status}){Colors.ENDC}")
            all_ok = False

    if all_ok:
        print(f"\n{Colors.GREEN}✅ All services are online!{Colors.ENDC}")
        print(f"{Colors.BOLD}Your XMRT Eliza deployment is working correctly.{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}⚠️ Some services are not responding.{Colors.ENDC}")
        print(f"{Colors.BOLD}Please check the Render dashboard and logs for more information.{Colors.ENDC}")

if __name__ == "__main__":
    main()
