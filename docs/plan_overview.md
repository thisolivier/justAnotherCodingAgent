**Project Document: LangGraph-Based Code Agent Setup with Rule Configuration and Local/Remote LLM Support**

---

### 🌟 Project Overview

This project aims to build a LangGraph-based autonomous coding agent pipeline that can accept feature requests, iteratively plan and develop solutions, and test code. It will support:

- Configurable project-specific rules
- Swappable LLM backends (local or remote) - *future enhancement*
- Adaptability to any CLI-based code project

This system is designed to be developer-assistive, semi-autonomous, and reusable across multiple codebases.

---

### ✅ Goals

1. **Enable natural-language feature requests** to trigger a code generation workflow.
2. **Guide project setup through simple rule configuration** (YAML/JSON templates).
3. **Implement modular tools** for file access, test execution, and context retrieval.
4. **Persist and reuse project-specific constraints** (e.g., linting, architecture rules, naming conventions).
5. **Support offline development** through local LLM integration (future phase).

---

### 🚀 Phase 1 MVP - Functional Requirements

#### Agent Workflow
- **Input**: Natural-language feature request
- **Steps**:
  1. Load project-specific rules from config file
  2. Plan implementation steps
  3. Retrieve relevant code context (simple file search)
  4. Generate or modify code
  5. Run project-defined tests
  6. Create review documentation
  7. Checkout feature branch for changes

#### Rule Configuration
- Simple YAML/JSON template for project rules
- Manual editing to define:
  - File boundaries and patterns
  - Testing commands
  - Code style preferences
  - Branch naming conventions

#### LLM Support
- Single configurable LLM provider (OpenAI or Anthropic)
- Configuration via environment variables

---

### 📝 Local Review Workflow

Instead of automated PR creation, the agent will facilitate local code reviews through a structured branch and documentation approach:

#### Workflow Steps:

1. **Branch Creation**
   - Agent creates a new feature branch with descriptive naming (e.g., `feature/add-user-authentication`)
   - Branch name follows project conventions defined in rules

2. **Feature Documentation**
   - Agent creates a markdown file in project root: `REVIEW-{branch-name}.md`
   - Example: `REVIEW-feature-add-user-authentication.md`

3. **Review Document Structure**
   ```markdown
   # Feature: [Feature Name]
   
   ## Summary
   Brief description of what was implemented
   
   ## Changes Made
   - List of files modified/created
   - Key implementation decisions
   - Any deviations from original request
   
   ## Testing
   - Tests added/modified
   - Test results summary
   - Any failing tests or known issues
   
   ## Review Checklist
   - [ ] Code follows project style guidelines
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No sensitive data exposed
   
   ## Next Steps
   Suggested improvements or follow-up tasks
   ```

4. **Local Review Process**
   - Developer can review changes using standard git diff tools
   - Review document provides context and rationale
   - Developer can request agent modifications before merging
   - Once approved, developer manually merges or creates PR

#### Benefits:
- Full control over code before it reaches main branch
- Paper trail of agent decisions and reasoning
- Easy rollback if needed
- Works completely offline
- Builds trust before moving to more automated workflows

---

### 🛠️ Technical Implementation Steps - Phase 1

1. **Project Scaffold**
   - Set up LangGraph with nodes for `plan`, `generate_code`, `run_tests`, `create_review_doc`
   - Define tool interfaces: `ReadFile`, `WriteFile`, `RunCommand`, `GitCheckout`

2. **LLM Provider Wrapper**
   - Simple wrapper for single provider (configurable)
   - Basic retry logic and error handling

3. **Project Context Loader**
   - File path pattern matching
   - Simple keyword search in codebase
   - Load README and key config files

4. **Rule System**
   - JSON/YAML rule parser
   - Template provided for common project types
   - Manual configuration required

5. **Testing Tool**
   - Wrap test command(s) (e.g., `npm test`, `pytest`) and return structured output
   - Parse common test output formats

---

### 🎯 Future Phases

#### Phase 2 - Scope Evaluation & Proposals:

##### Scope Assessment Node
The agent will evaluate the complexity and scope of feature requests using flexible, context-aware criteria:

**Scope Categories:**
- **New Module**: Creating entirely new functionality areas
- **Feature Addition**: Adding capabilities to existing modules (1-3 features)
- **Module Enhancement**: Significant expansion of existing module (4+ features)
- **Cross-Module Changes**: Features spanning multiple modules
- **System Refactor**: Architecture-level changes affecting the whole codebase

**Proposal Triggers:**
- Any "New Module" or "System Refactor" scope
- Cross-module changes affecting 3+ modules
- Requests containing keywords: "refactor", "redesign", "migrate", "architecture"
- Ambiguous requirements needing clarification

##### Proposal Document Format:
```markdown
# Feature Proposal: [Feature Name]

## Scope Assessment
- **Scope Type**: [New Module/Feature Addition/Module Enhancement/Cross-Module/System Refactor]
- **Affected Modules**: [List of existing modules impacted]
- **Architectural Impact**: [None/Minor/Significant]
- **Risk Level**: [Low/Medium/High]

## Proposed Solution
[Plain English explanation of the approach, focusing on the "what" and "why"]

## Implementation Strategy
1. High-level phases of work
2. Key architectural decisions
3. Integration points with existing code

## Considerations & Risks
- Technical challenges anticipated
- Potential side effects
- Dependencies or prerequisites

## Alternative Approaches
- Other solutions considered
- Trade-offs of chosen approach

## Success Criteria
- How we'll know the feature is complete
- Testing approach
- Performance expectations

## Approval
- [ ] Approved to proceed as proposed
- [ ] Approved with modifications (see comments)
- [ ] Needs revision
```

**Approval Workflow:**
- Proposal saved as `PROPOSAL-{timestamp}-{feature-name}.md`
- Agent waits for file modification indicating approval
- Developer can add comments directly in the markdown for revision requests

#### Phase 3 Enhancements:
- Multiple LLM provider support with fallback logic
- Local LLM integration (Ollama, LM Studio) for offline work
- Enhanced context retrieval with caching
- Git commit operations (still local-only)

#### Phase 4 Enhancements:
- Interactive rule authoring assistant
- Vector search for large codebases (Chroma integration)
- PR automation with safety checks
- Multi-agent collaboration

---

### ⚖️ Non-Functional Requirements

- **Simplicity**: Start with minimal complexity, add features based on real usage
- **Security**: Avoid LLM access to sensitive files unless explicitly permitted
- **Extensibility**: Easy to add tools through plugin architecture
- **Transparency**: All agent actions logged and reviewable

---

### 🔧 Phase 1 Deliverables

- LangGraph pipeline (Python) with basic nodes
- Core toolset module (filesystem, test runner, git checkout)
- Rule configuration template and parser
- Example configs for Node.js and Python projects
- Demo walkthrough with sample feature request

---

### 📋 Example Rule Configuration

```yaml
project:
  name: "my-node-app"
  language: "javascript"
  
file_rules:
  allowed_paths:
    - "src/**/*.js"
    - "tests/**/*.test.js"
  forbidden_paths:
    - "node_modules/**"
    - ".env"
    - "**/*.secret.*"

code_style:
  indent: 2
  quotes: "single"
  semicolons: false

testing:
  command: "npm test"
  required_coverage: 80

git:
  branch_prefix: "feature/"
  commit_format: "conventional" # feat:, fix:, etc.
```

---

This simplified approach focuses on getting a working system quickly while maintaining the flexibility to add advanced features as needed.