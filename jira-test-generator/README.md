# Jira Epic to Test Scenarios Generator

Generate comprehensive test scenarios from Jira epics using Cursor AI agent and save them to Google Docs.

## Features

- Fetches epics and child issues (stories, tasks, bugs) from Jira
- Extracts pull request links from Jira custom fields
- Uses Cursor AI agent to generate comprehensive test scenarios
- Outputs formatted test scenarios to a new Google Doc with:
  - General Information section (epic link, feature link, release info)
  - Test Scenarios section with proper formatting
  - Bugs section for tracking issues found during testing

## Prerequisites

- Python 3.9+
- Jira account with API access
- Google Cloud project with Docs API enabled
- Cursor IDE with AI agent access

## Setup

### 1. Install Dependencies

```bash
cd jira-test-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env  # or open in your editor
```

**⚠️ IMPORTANT: You MUST update these values in `.env`:**

| Variable | Description | How to Get |
|----------|-------------|------------|
| `JIRA_SERVER` | Your Jira instance URL | e.g., `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email | Your login email |
| `JIRA_API_TOKEN` | Jira API token | Your Jira API token |

**Optional variables:**

| Variable | Description |
|----------|-------------|
| `JIRA_AC_FIELD` | Custom field ID for Acceptance Criteria (e.g., `customfield_10014`) |
| `JIRA_PR_FIELD` | Custom field ID for Pull Request links (e.g., `customfield_10875`) |
| `GOOGLE_DRIVE_FOLDER_ID` | Shared Drive folder ID to move created docs |

### 3. Setup Google Docs API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - Google Docs API
   - Google Drive API (optional, for moving to shared folders)
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Desktop app**
6. Download the JSON file
7. Save it as `credentials.json` in this folder

### 4. Authenticate with Google

```bash
python3 auth_setup.py
```

This opens a browser for you to sign in. After success, `token.json` is created.

## Quick Start Guide

After setup, open Cursor AI chat and run:

```
@generate-test-scenarios EPIC-KEY
```

or with a Jira URL:

```
@generate-test-scenarios https://your-jira.atlassian.net/browse/EPIC-KEY
```

The skill automatically fetches Jira data, generates test scenarios, creates a Google Doc, and returns the link.

## Manual Steps (Alternative)

If you prefer manual control over each step:

```bash
# 1. Fetch epic data from Jira
python3 main.py --fetch EPIC-KEY

# 2. Open epic_data.md in Cursor, ask AI to generate test scenarios
# 3. Save output to test_scenarios.md

# 4. Create Google Doc
python3 main.py --write EPIC-KEY
```

## Test Scenario Format

Each test scenario should follow this structure:

```
[Descriptive Title]
Related Issue: JIRA-KEY (https://your-jira-server/browse/JIRA-KEY)
Git Pull Request: [PR link or "NO PR FOUND"]
Priority: High / Medium / Low
Type: Functional / UI / Integration / Edge Case / Negative

Preconditions:
- List any setup required

Test Steps:
1. Step one
2. Step two
3. ...

Expected Results:
- What should happen

Screenshots:
(To be added during testing)
```

## Files Reference

| File | Purpose | Committed? |
|------|---------|------------|
| `.env` | Your credentials (Jira token, etc.) | No (gitignored) |
| `.env.example` | Template for .env | Yes |
| `credentials.json` | Google OAuth client ID | No (gitignored) |
| `token.json` | Google OAuth access token | No (gitignored) |
| `epic_data.md` | Fetched Jira data | No (gitignored) |
| `epic_data.json` | Fetched Jira data (JSON) | No (gitignored) |
| `test_scenarios.md` | Generated test scenarios | No (gitignored) |

## Troubleshooting

### "pip command not found"
Use `pip3` instead of `pip`, or run from within the virtual environment.

### Jira connection errors
- Verify your API token is correct and not expired
- Check if your Jira URL includes `https://`
- Ensure you have permission to read the epic
- Verify JIRA_SERVER, JIRA_EMAIL, and JIRA_API_TOKEN are set in `.env`

### Google Docs errors
- Run `auth_setup.py` again if token expired
- Verify APIs are enabled in Google Cloud Console
- Ensure `credentials.json` exists in the folder

### "Issue does not exist" error
- Verify you have access to the Jira project
- Check that the epic key is correct (e.g., `PROJ-123`)
- Try accessing the epic in your browser first

### "JIRA_SERVER not set" error
- Make sure you copied `.env.example` to `.env`
- Verify all required variables are set in `.env`
