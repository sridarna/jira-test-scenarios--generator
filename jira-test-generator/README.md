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
| `JIRA_API_TOKEN` | Jira API token | [Generate here](https://id.atlassian.com/manage-profile/security/api-tokens) |

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

Here's a complete example of generating test scenarios for an epic:

### Step 1: Fetch Epic Data from Jira

```bash
# Activate virtual environment
source venv/bin/activate

# Fetch epic data (replace with your epic key)
python3 main.py --fetch PROJ-12345
```

**Output:** Creates `epic_data.md` with epic details and all child issues.

### Step 2: Generate Test Scenarios with Cursor AI

1. Open `epic_data.md` in Cursor IDE
2. Open the AI chat (Cmd+L or Ctrl+L)
3. Ask the agent:

   ```
   Generate test scenarios from this epic data
   ```

4. The agent generates comprehensive test scenarios
5. Save the output to `test_scenarios.md`

**Tips for better results:**
- Ask for "at least 2-3 test scenarios per user story"
- Request "both positive and negative test cases"
- Ask to "include edge cases and error handling scenarios"

### Step 3: Create Google Doc

```bash
python3 main.py --write PROJ-12345
```

**Output:** Creates a formatted Google Doc with:
- General Information section
- All test scenarios with headings
- Hyperlinked PR and Jira ticket references

The Google Doc URL is printed in the terminal.

## Complete Example

```bash
# 1. Setup (first time only)
cd jira-test-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python3 auth_setup.py

# 2. Generate test scenarios for an epic
python3 main.py --fetch RHOAIENG-12345

# 3. Open epic_data.md in Cursor, ask AI to generate test scenarios
# 4. Save AI output to test_scenarios.md

# 5. Create Google Doc
python3 main.py --write RHOAIENG-12345
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

## License

MIT
