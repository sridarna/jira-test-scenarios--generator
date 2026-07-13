---
name: generate-test-scenarios
description: Generate comprehensive test scenarios from Jira epic data and create Google Doc. Use when the user asks to generate test scenarios, create test cases, or provides a Jira epic URL/key.
---

# Generate Test Scenarios from Jira Epic

Generate comprehensive test scenarios from Jira epic data and output to Google Docs.

## Workflow

When the user provides a Jira epic URL or key:

1. **Fetch epic data from Jira**
   ```bash
   cd jira-test-generator
   python3 main.py --fetch EPIC-KEY
   ```

2. **Read the generated `epic_data.md` file**

3. **Generate test scenarios** following the format below

4. **Save to `test_scenarios.md`** in the `jira-test-generator/` folder

5. **Create Google Doc**
   ```bash
   python3 main.py --write EPIC-KEY
   ```

6. **Return the Google Doc link** to the user

## Test Scenario Format

Generate each scenario using this exact format:

```
[Descriptive Title]
Related Issue: JIRA-KEY (https://jira-server/browse/JIRA-KEY)
Git Pull Request: [PR link from epic data or "NO PR FOUND"]
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

---
```

## Generation Guidelines

For each user story/task in the epic:

1. **Create 2-3 test scenarios minimum:**
   - Happy path (normal flow)
   - Edge cases
   - Error handling / negative cases

2. **Include these scenario types:**
   - Functional tests
   - UI verification
   - Integration tests
   - Feature flag behavior (enabled/disabled)

3. **Be specific and actionable:**
   - Clear step-by-step instructions
   - Specific expected results
   - Reference actual UI elements and field names

4. **Include Related Issue and PR:**
   - Link to the Jira ticket
   - Include PR link if available in epic data

## Output Structure

Start the output with:

```
Test Scenarios for [EPIC-KEY] - [Epic Title]

IMPORTANT: [Any feature flags or prerequisites]

---
```

Then add each test scenario separated by `---`.

## Example Scenario

```
Feature Flag Enabled - Topology Type Dropdown Appears
Related Issue: RHOAIENG-70582 (https://redhat.atlassian.net/browse/RHOAIENG-70582)
Git Pull Request: https://github.com/opendatahub-io/odh-dashboard/pull/8312
Priority: High
Type: Functional

Preconditions:
	- RHOAI Dashboard deployed
	- llmdTopologyConfigs feature flag is ENABLED
	- At least one topology config exists on the cluster

Test Steps:
	1. Log in to RHOAI Dashboard as a regular user
	2. Navigate to Data Science Projects
	3. Create or open a project
	4. Go to Models section and click "Deploy model"
	5. Select a Generative model type
	6. Select LLM-d as the deployment method
	7. Observe the "Topology type" dropdown

Expected Results:
	- "Topology type" dropdown is visible
	- Dropdown shows 4 options: Single node, Multi-node, Single node disaggregated, Multi-node disaggregated
	- Single node option is always enabled
	- Topology types without matching configs are disabled (greyed out)

Screenshots:
(To be added during testing)

---
```

## Final Output

After creating the Google Doc, provide the user with:

1. **Google Doc link** (the primary output)
2. Summary of scenarios generated
3. Epic key and title

Example response:
```
✅ Test scenarios generated and saved to Google Docs!

**Google Doc:** https://docs.google.com/document/d/[doc-id]

**Summary:**
- Epic: RHOAIENG-70569 - LLM-D Deployment in Wizard
- Test scenarios: 45
- Child issues analyzed: 14
```
