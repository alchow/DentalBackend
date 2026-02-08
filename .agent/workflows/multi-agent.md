---
description: How to use the multi-agent workflow with @manager routing to specialized agents
---

# Multi-Agent Workflow

This workflow enables the manager to create work packages that YOU route to specialized agents.

## Architecture

```
USER Request
    ↓
@manager (analyzes, creates work packages)
    ↓
USER routes work packages to:
    ├── @backend_cto (implementation)
    ├── @product (UX/API design)
    └── @devops (deployment)
    ↓
Agents update TeamCommunication.md
    ↓
@manager reviews and coordinates
```

## How It Works

### Step 1: Start with @manager
```
@manager [describe your request]
```

Manager will:
1. Analyze the request
2. Create work packages in `docs/TeamCommunication.md`
3. Specify which agent should handle each package

### Step 2: Route Work Packages
Manager output will look like:
```markdown
## Work Packages

### WP-1: Implement GET /notes endpoint
**Assign to**: @backend_cto
**Input**: [requirements]
**Expected Output**: [deliverables]
```

YOU then start a new conversation:
```
@backend_cto 

Please complete WP-1 from docs/TeamCommunication.md:
[paste or reference the work package]
```

### Step 3: Agent Reports Back
Each agent updates `docs/TeamCommunication.md` with:
- Work completed
- Decisions made
- Blockers or questions

### Step 4: Manager Reviews
Return to manager:
```
@manager Review the completed work in TeamCommunication.md
```

## Work Package Format

```markdown
### WP-[N]: [Title]
**Assign to**: @[agent_name]
**Priority**: P0/P1/P2
**Status**: PENDING | IN_PROGRESS | BLOCKED | DONE

**Context**:
[Background the agent needs]

**Requirements**:
1. [Specific deliverable]
2. [Specific deliverable]

**Acceptance Criteria**:
- [ ] [Testable criterion]

**Files to Modify**:
- `path/to/file.py`

**Dependencies**:
- WP-[X] must be done first (if any)
```

## Agent Responsibilities

### @manager
- Creates work packages
- Reviews completed work
- Coordinates between agents
- Maintains `TeamCommunication.md`

### @backend_cto
- Implements API endpoints
- Database changes (Alembic)
- Updates `BackendImplementation.md`

### @product
- API contract design
- UX considerations
- Updates `FRONTEND_API_GUIDE.md`

### @devops
- Deployment scripts
- Infrastructure changes
- Performance/security review

## Example Flow

```
1. USER: @manager I need to add a new API endpoint

2. MANAGER: Creates WP-1 in TeamCommunication.md
   "WP-1: Design API contract - Assign to @product"
   "WP-2: Implement endpoint - Assign to @backend_cto (after WP-1)"

3. USER: @product Please complete WP-1...

4. PRODUCT: Designs API, updates TeamCommunication.md
   "WP-1: DONE - See FRONTEND_API_GUIDE.md"

5. USER: @backend_cto Please complete WP-2...

6. BACKEND_CTO: Implements, updates TeamCommunication.md
   "WP-2: DONE - See notes.py"

7. USER: @manager Review completed work

8. MANAGER: Reviews, creates WP-3 for deployment if needed
```

## Tips

// turbo-all
- Keep conversations focused: one agent per conversation
- Reference `docs/TeamCommunication.md` as the source of truth
- Agents should read their skill file first for context
- Use specific file paths when routing
