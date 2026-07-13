#!/usr/bin/env python3
"""
Google OAuth Setup Script

Run this once to authenticate with Google and create token.json.
You'll need credentials.json from Google Cloud Console first.

Steps:
1. Go to https://console.cloud.google.com/
2. Create a project (or select existing)
3. Enable "Google Docs API" and "Google Drive API"
4. Go to Credentials → Create Credentials → OAuth client ID
5. Choose "Desktop app"
6. Download the JSON and save as credentials.json in this folder
7. Run: python3 auth_setup.py
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'  # Full drive access for shared drives
]

def main():
    credentials_file = 'credentials.json'
    
    if not os.path.exists(credentials_file):
        print("ERROR: credentials.json not found!")
        print("\nTo get credentials.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create or select a project")
        print("3. Enable 'Google Docs API' and 'Google Drive API'")
        print("4. Go to Credentials → Create Credentials → OAuth client ID")
        print("5. Choose 'Desktop app'")
        print("6. Download the JSON and save as 'credentials.json' here")
        return
    
    print("Starting OAuth flow...")
    print("A browser window will open for you to sign in with Google.\n")
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("\n✅ Authentication successful!")
    print("token.json has been created.")
    print("You can now run main.py to generate test scenarios.")

if __name__ == "__main__":
    main()
