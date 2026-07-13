---
name: generate-test-scenarios
description: Generate comprehensive test scenarios from Jira epic data. Use when the user asks to generate test scenarios, create test cases, or when working with epic_data.md files.
---

# Generate Test Scenarios from Jira Epic

Generate comprehensive test scenarios from Jira epic data for QA verification.

## Quick Start

When the user asks to generate test scenarios:

1. Read the `epic_data.md` file (or specified file)
2. Generate test scenarios for each user story/task
3. Save output to `test_scenarios.md`

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

## After Generation

Remind the user:
1. Review and adjust the generated scenarios
2. Save to `test_scenarios.md` in the `jira-test-generator/` folder
3. Run `python3 main.py --write EPIC-KEY` to create Google Doc
