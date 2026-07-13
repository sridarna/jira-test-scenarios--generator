#!/usr/bin/env python3
"""
Jira Epic to Test Scenarios Generator

This script works with Cursor AI agent for test scenario generation:
1. Fetches epic and child issues from Jira (--fetch)
2. You use Cursor agent to generate test scenarios from the fetched data
3. Writes the test scenarios to a Google Doc (--write)

Usage:
    # Step 1: Fetch Jira data
    python3 main.py --fetch EPIC-KEY
    
    # Step 2: Ask Cursor agent to generate test scenarios from epic_data.md
    
    # Step 3: Write to Google Docs (after saving AI output to test_scenarios.md)
    python3 main.py --write EPIC-KEY

Prerequisites:
    1. Run auth_setup.py to authenticate with Google Docs
    2. Have your Jira API token ready
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

# Configuration - load from environment variables
JIRA_SERVER = os.environ.get("JIRA_SERVER")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_API_TOKEN")
JIRA_AC_FIELD = os.environ.get("JIRA_AC_FIELD", None)
JIRA_PR_FIELD = os.environ.get("JIRA_PR_FIELD")  # Git Pull Request field (optional)
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

# File paths
EPIC_DATA_FILE = "epic_data.md"
TEST_SCENARIOS_FILE = "test_scenarios.md"


def get_pull_request_from_field(issue) -> str:
    """Extract pull request URL from the custom field."""
    if not JIRA_PR_FIELD:
        return ""
    
    pr_field = getattr(issue.fields, JIRA_PR_FIELD, None)
    
    if pr_field:
        # Handle different field formats
        if isinstance(pr_field, dict):
            return pr_field.get('value', '') or pr_field.get('url', '')
        elif isinstance(pr_field, str):
            return pr_field
    
    return ""


def get_epic_with_tasks(epic_key: str) -> dict:
    """Fetch an epic and all its child issues from Jira."""
    print(f"Connecting to Jira at {JIRA_SERVER}...")
    
    jira = JIRA(
        server=JIRA_SERVER,
        basic_auth=(JIRA_EMAIL, JIRA_TOKEN)
    )
    
    epic = jira.issue(epic_key)
    print(f"Found epic: {epic.fields.summary}")
    
    # Get PR from custom field
    epic_pr = get_pull_request_from_field(epic)
    if epic_pr:
        print(f"  Found PR for epic: {epic_pr}")
    else:
        print(f"  No PR found for epic")
    
    jql_queries = [
        f'"Epic Link" = {epic_key}',
        f'parent = {epic_key}',
        f'"Parent" = {epic_key}',
    ]
    
    tasks = []
    for jql in jql_queries:
        try:
            results = jira.search_issues(jql, maxResults=100)
            if results:
                tasks.extend(results)
                print(f"Found {len(results)} issues with query: {jql}")
        except Exception as e:
            print(f"Query failed (this is okay): {jql}")
    
    seen = set()
    unique_tasks = []
    for task in tasks:
        if task.key not in seen:
            seen.add(task.key)
            unique_tasks.append(task)
    
    print(f"Total unique child issues: {len(unique_tasks)}")
    
    def get_acceptance_criteria(issue):
        if JIRA_AC_FIELD:
            return getattr(issue.fields, JIRA_AC_FIELD, '') or ''
        for field in ['customfield_10001', 'customfield_10014', 'customfield_10016']:
            value = getattr(issue.fields, field, None)
            if value:
                return str(value)
        return ''
    
    print("\nFetching pull request information for child issues...")
    tasks_with_prs = []
    for task in unique_tasks:
        task_pr = get_pull_request_from_field(task)
        if task_pr:
            print(f"  Found PR for {task.key}: {task_pr}")
        tasks_with_prs.append({
            "key": task.key,
            "summary": task.fields.summary,
            "description": task.fields.description or "(No description)",
            "type": task.fields.issuetype.name,
            "status": task.fields.status.name,
            "acceptance_criteria": get_acceptance_criteria(task),
            "pull_request": task_pr  # Single PR URL string
        })
    
    return {
        "epic": {
            "key": epic.key,
            "summary": epic.fields.summary,
            "description": epic.fields.description or "(No description)",
            "pull_request": epic_pr  # Single PR URL string
        },
        "tasks": tasks_with_prs
    }


def save_epic_data_for_cursor(epic_data: dict):
    """Save epic data in a format ready for Cursor agent to generate test scenarios."""
    
    epic_pr = epic_data['epic'].get('pull_request', '')
    
    content = f"""# Epic Data for Test Scenario Generation

## Epic: {epic_data['epic']['key']} - {epic_data['epic']['summary']}

### Epic Description:
{epic_data['epic']['description']}

### Epic Git Pull Request:
{epic_pr if epic_pr else "NO PR FOUND"}

---

## Child Issues ({len(epic_data['tasks'])} total)

"""
    
    for task in epic_data['tasks']:
        task_pr = task.get('pull_request', '')
        content += f"""### {task['key']} - {task['summary']}
- **Type:** {task['type']}
- **Status:** {task['status']}
- **Description:** {task['description']}
"""
        if task['acceptance_criteria']:
            content += f"- **Acceptance Criteria:** {task['acceptance_criteria']}\n"
        
        content += f"- **Git Pull Request:** {task_pr if task_pr else 'NO PR FOUND'}\n"
        
        content += "\n---\n\n"
    
    content += """
---

## Instructions for Cursor Agent

Please generate comprehensive test scenarios for each user story/task above. 

For each scenario, use this format:

### [Descriptive Title]
**Related Issue:** [JIRA-KEY] ({JIRA_SERVER}/browse/JIRA-KEY)
**Git Pull Request:** [PR link or "NO PR FOUND"]
**Priority:** High / Medium / Low
**Type:** Functional / UI / Integration / Edge Case / Negative

**Preconditions:**
- List any setup required

**Test Steps:**
1. Step one
2. Step two
3. ...

**Expected Results:**
- What should happen

---

Guidelines:
- Create at least 2-3 test scenarios per user story (happy path, edge cases, error handling)
- Focus on user-facing functionality
- Include both positive and negative test cases
- Be specific and actionable
- Group related scenarios together
- Include the Git Pull Request section for each test scenario
"""
    
    with open(EPIC_DATA_FILE, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Epic data saved to: {EPIC_DATA_FILE}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {EPIC_DATA_FILE} in Cursor")
    print(f"   2. Ask Cursor agent: 'Generate test scenarios from this epic data'")
    print(f"   3. Save the generated scenarios to: {TEST_SCENARIOS_FILE}")
    print(f"   4. Run: python3 main.py --write {epic_data['epic']['key']}")


def get_google_credentials():
    """Load and refresh Google credentials."""
    if not os.path.exists('token.json'):
        print("ERROR: token.json not found!")
        print("Run 'python3 auth_setup.py' first to authenticate with Google.")
        sys.exit(1)
    
    creds = Credentials.from_authorized_user_file('token.json')
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds


import re

def parse_and_format_content(content: str, tab_id: str = None, start_index: int = 1) -> tuple:
    """Parse content and return formatted requests for Google Docs."""
    requests = []
    links = []
    current_index = start_index
    next_is_scenario_title = False  # Flag to track if next non-empty line is a scenario title
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        # Handle separator lines - insert horizontal rule
        if stripped_line == '---':
            # Add newline then horizontal line characters then newline
            separator_text = '\n' + '─' * 50 + '\n\n'
            location = {'index': current_index}
            if tab_id:
                location['tabId'] = tab_id
            requests.append({
                'insertText': {
                    'location': location,
                    'text': separator_text
                }
            })
            current_index += len(separator_text)
            next_is_scenario_title = True  # Next non-empty line will be a scenario title
            i += 1
            continue
        
        # Handle empty lines - add blank line for spacing
        if not stripped_line:
            location = {'index': current_index}
            if tab_id:
                location['tabId'] = tab_id
            requests.append({
                'insertText': {
                    'location': location,
                    'text': '\n'
                }
            })
            current_index += 1
            i += 1
            continue
        
        # Check if line is indented (has tab or spaces at start)
        is_indented = line.startswith('\t') or line.startswith('    ')
        
        # Use original line with indentation for indented items, otherwise use stripped
        if is_indented:
            # Replace tab with spaces for Google Docs compatibility
            text = '    ' + stripped_line  # 4 spaces indent
        else:
            text = stripped_line
        
        heading_type = None
        is_bold = False
        
        # Title line (first non-empty line with "Test Scenarios for")
        if stripped_line.startswith('Test Scenarios for'):
            heading_type = 'HEADING_1'
            text = stripped_line
            next_is_scenario_title = False
        
        # Test Scenario heading (first non-empty line after ---)
        elif next_is_scenario_title and not stripped_line.startswith(('Related Issue:', 'Git Pull Request:', 'Priority:', 'Type:', 'Preconditions:', 'Test Steps:', 'Expected Results:', 'Screenshots:', 'IMPORTANT:')):
            heading_type = 'HEADING_2'
            text = stripped_line
            next_is_scenario_title = False
        
        # Section headers
        elif stripped_line == 'Test Steps:' or stripped_line == 'Expected Results:' or stripped_line == 'Screenshots:':
            is_bold = True
            text = stripped_line
        
        # Check for GitHub PR link
        pr_link_match = re.search(r'(https://github\.com/[^\s]+/pull/(\d+))', text)
        link_info = None
        if pr_link_match and 'Git Pull Request:' in text:
            url = pr_link_match.group(1)
            pr_number = pr_link_match.group(2)
            pr_text = f'PR-{pr_number}'
            text = text.replace(url, pr_text)
            link_info = {'url': url, 'text': pr_text}
        
        # Add text
        text_to_insert = text + '\n'
        location = {'index': current_index}
        if tab_id:
            location['tabId'] = tab_id
        
        requests.append({
            'insertText': {
                'location': location,
                'text': text_to_insert
            }
        })
        
        text_start = current_index
        text_end = current_index + len(text)
        
        # Build range with optional tab_id
        range_obj = {'startIndex': text_start, 'endIndex': text_end + 1}
        if tab_id:
            range_obj['tabId'] = tab_id
        
        # Apply heading style
        if heading_type:
            requests.append({
                'updateParagraphStyle': {
                    'range': range_obj,
                    'paragraphStyle': {
                        'namedStyleType': heading_type
                    },
                    'fields': 'namedStyleType'
                }
            })
        
        # Apply bold
        if is_bold:
            bold_range = {'startIndex': text_start, 'endIndex': text_end}
            if tab_id:
                bold_range['tabId'] = tab_id
            requests.append({
                'updateTextStyle': {
                    'range': bold_range,
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
        
        # Store link info
        if link_info:
            pr_text_pos = text.find(link_info['text'])
            if pr_text_pos >= 0:
                links.append({
                    'url': link_info['url'],
                    'start': text_start + pr_text_pos,
                    'end': text_start + pr_text_pos + len(link_info['text']),
                    'tab_id': tab_id
                })
        
        current_index += len(text_to_insert)
        i += 1
    
    return requests, links, current_index


def parse_and_format_content_v2(content: str, start_index: int = 1) -> tuple:
    """Parse content and return text + formatting ranges separately.
    
    Returns: (text_content, format_ranges, links, end_index)
    """
    text_content = ""
    format_ranges = []  # (start, end, type, extra)
    links = []
    current_index = start_index
    next_is_scenario_title = False  # Flag to track if next non-empty line is a scenario title
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        # Handle separator lines
        if stripped_line == '---':
            separator_text = '\n' + '─' * 50 + '\n\n'
            text_content += separator_text
            current_index += len(separator_text)
            next_is_scenario_title = True  # Next non-empty line will be a scenario title
            i += 1
            continue
        
        # Handle empty lines
        if not stripped_line:
            text_content += '\n'
            current_index += 1
            i += 1
            continue
        
        # Check if line is indented
        is_indented = line.startswith('\t') or line.startswith('    ')
        
        if is_indented:
            text = '    ' + stripped_line
        else:
            text = stripped_line
        
        heading_type = None
        is_bold = False
        
        # Title line
        if stripped_line.startswith('Test Scenarios for'):
            heading_type = 'HEADING_1'
            text = stripped_line
            next_is_scenario_title = False
        
        # Test Scenario heading (first non-empty line after ---)
        elif next_is_scenario_title and not stripped_line.startswith(('Related Issue:', 'Git Pull Request:', 'Priority:', 'Type:', 'Preconditions:', 'Test Steps:', 'Expected Results:', 'Screenshots:', 'IMPORTANT:')):
            heading_type = 'HEADING_2'
            text = stripped_line
            next_is_scenario_title = False
        
        # Section headers
        elif stripped_line in ['Test Steps:', 'Expected Results:', 'Screenshots:']:
            is_bold = True
            text = stripped_line
        
        # Check for GitHub PR link
        pr_link_match = re.search(r'(https://github\.com/[^\s]+/pull/(\d+))', text)
        link_info = None
        if pr_link_match and 'Git Pull Request:' in text:
            url = pr_link_match.group(1)
            pr_number = pr_link_match.group(2)
            pr_text = f'PR-{pr_number}'
            text = text.replace(url, pr_text)
            link_info = {'url': url, 'text': pr_text}
        
        text_to_insert = text + '\n'
        text_start = current_index
        text_end = current_index + len(text)
        
        # Track formatting
        if heading_type:
            format_ranges.append((text_start, text_end + 1, heading_type, None))
        
        if is_bold:
            format_ranges.append((text_start, text_end, 'BOLD', None))
        
        # Store link info
        if link_info:
            pr_text_pos = text.find(link_info['text'])
            if pr_text_pos >= 0:
                links.append({
                    'url': link_info['url'],
                    'start': text_start + pr_text_pos,
                    'end': text_start + pr_text_pos + len(link_info['text']),
                    'tab_id': None
                })
        
        text_content += text_to_insert
        current_index += len(text_to_insert)
        i += 1
    
    return text_content, format_ranges, links, current_index


def build_general_info_content(epic_data: dict) -> str:
    """Build the General Information tab content."""
    epic = epic_data.get('epic', {})
    tasks = epic_data.get('tasks', [])
    
    epic_key = epic.get('key', 'Unknown')
    epic_summary = epic.get('summary', 'Unknown')
    epic_description = epic.get('description', '')
    
    # Find QA Verification task
    qa_jira_link = "Not found"
    qa_jira_key = ""
    for task in tasks:
        if 'QA Verification' in task.get('summary', ''):
            qa_jira_key = task.get('key', '')
            qa_jira_link = f"{JIRA_SERVER}/browse/{qa_jira_key}"
            break
    
    # Extract mocks link from epic description if exists
    mocks_link = "Not found"
    if epic_description:
        import re
        mocks_match = re.search(r'(https?://[^\s\]|]+(?:mocks?|figma|pages\.redhat)[^\s\]|]*)', epic_description, re.IGNORECASE)
        if mocks_match:
            mocks_link = mocks_match.group(1)
    
    # Extract feature/RFE link
    feature_link = "Not found"
    if epic_description:
        rfe_match = re.search(r'(https?://[^\s\]|]*(?:RHAIRFE|RFE)[^\s\]|]*)', epic_description, re.IGNORECASE)
        if rfe_match:
            feature_link = rfe_match.group(1)
    
    content = f"""QA Verification: {epic_summary}

General Information

Epic Link:
{JIRA_SERVER}/browse/{epic_key}

Feature Link:
{feature_link}

Release Performed:
Need to assign

RHOAI Build used:
Need to update

Supporting Documentation:

Mocks:
{mocks_link}

QA Jira:
{qa_jira_link}
"""
    return content


def write_to_google_doc(title: str, content: str, epic_data: dict = None) -> str:
    """Create a new Google Doc with sections for General Info, Test Scenarios, and Bugs."""
    print("Creating Google Doc...")
    
    creds = get_google_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Create the document
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    
    # Build all content as one string first, then insert, then format
    full_content = ""
    format_ranges = []  # Store formatting info: (start, end, type, extra)
    
    current_index = 1
    
    # ===== SECTION 1: GENERAL INFORMATION =====
    if epic_data:
        general_info_content = build_general_info_content(epic_data)
        lines = general_info_content.split('\n')
        
        for line in lines:
            if not line.strip():
                full_content += '\n'
                current_index += 1
                continue
            
            text = line + '\n'
            text_start = current_index
            
            # Track formatting
            if 'QA Verification:' in line:
                format_ranges.append((text_start, text_start + len(line) + 1, 'HEADING_1', None))
            elif line == 'General Information':
                format_ranges.append((text_start, text_start + len(line) + 1, 'HEADING_2', None))
            elif line.endswith(':') and not line.startswith('http') and not line.startswith('Need') and not line.startswith('Not'):
                format_ranges.append((text_start, text_start + len(line), 'BOLD', None))
            
            full_content += text
            current_index += len(text)
        
        # Add separator before Test Scenarios
        separator = '\n\n' + '═' * 60 + '\n\n'
        full_content += separator
        current_index += len(separator)
    
    # ===== SECTION 2: TEST SCENARIOS =====
    section_header = "TEST SCENARIOS\n\n"
    header_start = current_index
    full_content += section_header
    format_ranges.append((header_start, header_start + len("TEST SCENARIOS") + 1, 'HEADING_1', None))
    current_index += len(section_header)
    
    # Parse test scenarios content
    test_content, test_formats, links, end_index = parse_and_format_content_v2(content, current_index)
    full_content += test_content
    format_ranges.extend(test_formats)
    current_index = end_index
    
    # ===== SECTION 3: BUGS =====
    bugs_section = '\n\n' + '═' * 60 + '\n\nBUGS\n\n(No bugs recorded yet)\n'
    # Calculate BUGS header position: \n\n (2) + ═*60 (60) + \n\n (2) = 64
    bugs_header_start = current_index + 64
    full_content += bugs_section
    # BUGS is 4 chars, +1 for newline in paragraph style
    format_ranges.append((bugs_header_start, bugs_header_start + 5, 'HEADING_1', None))
    
    # BATCH 1: Insert all text at once
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{'insertText': {'location': {'index': 1}, 'text': full_content}}]}
    ).execute()
    print("Text inserted")
    
    # BATCH 2: Apply all formatting
    format_requests = []
    for start, end, fmt_type, extra in format_ranges:
        if fmt_type in ['HEADING_1', 'HEADING_2', 'HEADING_3']:
            format_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'paragraphStyle': {'namedStyleType': fmt_type},
                    'fields': 'namedStyleType'
                }
            })
        elif fmt_type == 'BOLD':
            format_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start, 'endIndex': end},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })
    
    if format_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': format_requests}
        ).execute()
        print(f"Applied {len(format_requests)} formatting styles")
    
    # Apply hyperlinks
    if links:
        hyperlink_requests = []
        for link in links:
            link_range = {
                'startIndex': link['start'],
                'endIndex': link['end']
            }
            if link.get('tab_id'):
                link_range['tabId'] = link['tab_id']
            
            hyperlink_requests.append({
                'updateTextStyle': {
                    'range': link_range,
                    'textStyle': {
                        'link': {
                            'url': link['url']
                        }
                    },
                    'fields': 'link'
                }
            })
        
        if hyperlink_requests:
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': hyperlink_requests}
                ).execute()
                print(f"Applied {len(hyperlink_requests)} hyperlinks")
            except Exception as e:
                print(f"Warning: Could not apply hyperlinks: {e}")
    
    # Move to shared drive folder
    if GOOGLE_DRIVE_FOLDER_ID:
        try:
            file = drive_service.files().get(
                fileId=doc_id,
                fields='parents',
                supportsAllDrives=True
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            drive_service.files().update(
                fileId=doc_id,
                addParents=GOOGLE_DRIVE_FOLDER_ID,
                removeParents=previous_parents,
                supportsAllDrives=True,
                fields='id, parents'
            ).execute()
            
            print(f"Document moved to shared folder")
        except Exception as e:
            print(f"Warning: Could not move to shared folder: {e}")
            print("Document created in your personal Drive instead.")
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}"
    print(f"Document created: {doc_url}")
    
    return doc_url


def fetch_command(epic_key: str):
    """Fetch Jira data and save for Cursor agent."""
    missing = []
    if not JIRA_SERVER:
        missing.append("JIRA_SERVER")
    if not JIRA_EMAIL:
        missing.append("JIRA_EMAIL")
    if not JIRA_TOKEN:
        missing.append("JIRA_API_TOKEN")
    
    if missing:
        print("ERROR: Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print(f"Fetching Jira data for: {epic_key}")
    print(f"{'='*50}\n")
    
    epic_data = get_epic_with_tasks(epic_key)
    save_epic_data_for_cursor(epic_data)
    
    # Also save as JSON for later use
    with open('epic_data.json', 'w') as f:
        json.dump(epic_data, f, indent=2)


def write_command(epic_key: str):
    """Write test scenarios to Google Doc."""
    if not os.path.exists(TEST_SCENARIOS_FILE):
        print(f"ERROR: {TEST_SCENARIOS_FILE} not found!")
        print(f"\nPlease create {TEST_SCENARIOS_FILE} with the test scenarios first.")
        print("You can ask Cursor agent to generate them from epic_data.md")
        sys.exit(1)
    
    if not os.path.exists('epic_data.json'):
        print("ERROR: epic_data.json not found!")
        print("Run --fetch first to get the epic data.")
        sys.exit(1)
    
    with open('epic_data.json', 'r') as f:
        epic_data = json.load(f)
    
    with open(TEST_SCENARIOS_FILE, 'r') as f:
        test_scenarios = f.read()
    
    print(f"\n{'='*50}")
    print(f"Writing test scenarios to Google Doc")
    print(f"{'='*50}\n")
    
    doc_title = f"QA Verification - {epic_data['epic']['key']} - {epic_data['epic']['summary']}"
    doc_url = write_to_google_doc(doc_title, test_scenarios, epic_data)
    
    print(f"\n{'='*50}")
    print("Done!")
    print(f"{'='*50}")
    print(f"\nGoogle Doc: {doc_url}")
    print(f"Epic: {epic_data['epic']['key']} - {epic_data['epic']['summary']}")
    print(f"Tasks analyzed: {len(epic_data['tasks'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate test scenarios from Jira epics using Cursor agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
  1. Fetch Jira data:     python3 main.py --fetch EPIC-KEY
  2. Generate scenarios:  Ask Cursor agent to generate from epic_data.md
  3. Save AI output to:   test_scenarios.md
  4. Write to Google Doc: python3 main.py --write EPIC-KEY

Examples:
  python3 main.py --fetch PROJ-123
  python3 main.py --write PROJ-123
        """
    )
    
    parser.add_argument('--fetch', metavar='EPIC_KEY', 
                        help='Fetch epic data from Jira and save for Cursor agent')
    parser.add_argument('--write', metavar='EPIC_KEY',
                        help='Write test_scenarios.md to Google Doc')
    
    args = parser.parse_args()
    
    if args.fetch:
        fetch_command(args.fetch)
    elif args.write:
        write_command(args.write)
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python3 main.py --fetch YOUR-EPIC-KEY")


if __name__ == "__main__":
    main()
