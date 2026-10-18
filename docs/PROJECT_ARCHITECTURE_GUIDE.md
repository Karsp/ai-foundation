# Project Architecture & Engineering Decisions Guide

## Purpose

This document defines the decisions that must be made when establishing the engineering architecture for a new project.

It is intentionally project-agnostic.

The goal is not to force every repository into the same architecture, but to ensure that important decisions are:

- explicit;
- deliberate;
- documented;
- reviewable;
- reproducible;
- understandable by both humans and AI agents.

Use this document during project initialization and update it whenever the project's fundamental constraints change.

---

# 1. Project Classification

First determine what kind of project this is.

Examples:

- Web application
- Backend/API
- Frontend
- Mobile application
- CLI
- Desktop application
- Library/package
- SDK
- Infrastructure project
- Data/ML project
- Research project
- Automation
- Internal tool
- Monorepo
- Personal project
- Other

Record:

```text
Project type:
Primary purpose:
Primary users:
Expected lifetime:
Expected scale:
Criticality:
```

The answers influence every subsequent architectural decision.

---

# 2. Project Constraints

Identify the constraints before choosing technologies.

Consider:

### Functional constraints

What must the system do?

### Technical constraints

Are specific:

- languages;
- runtimes;
- frameworks;
- APIs;
- databases;
- cloud providers;

required?

### Business constraints

Consider:

- budget;
- delivery deadlines;
- team size;
- maintenance capacity;
- licensing.

### Operational constraints

Consider:

- availability;
- latency;
- scalability;
- offline operation;
- deployment environments;
- geographic requirements.

### Security constraints

Consider:

- authentication;
- authorization;
- sensitive data;
- compliance;
- isolation;
- auditability.

### Team constraints

Consider:

- developer expertise;
- expected contributors;
- AI-agent usage;
- onboarding requirements.

Document constraints before selecting architecture.

---

# 3. Language and Runtime

Choose:

- primary language;
- secondary languages;
- runtime;
- supported versions;
- package manager;
- dependency management strategy.

Questions:

- What language best fits the domain?
- What ecosystem maturity is required?
- What tooling is available?
- How easy is it for agents to work with the ecosystem?
- What is the expected maintenance horizon?

Avoid selecting technologies solely because they are fashionable.

---

# 4. Repository Structure

Decide whether the project should use:

- single package/repository;
- modular monolith;
- monorepo;
- multiple repositories.

For a monorepo, determine:

- workspace strategy;
- package boundaries;
- dependency rules;
- shared tooling;
- build strategy.

For a modular project, define explicit module boundaries.

The architecture should make dependencies visible rather than accidental.

---

# 5. Application Architecture

Select the simplest architecture that satisfies the requirements.

Possible approaches include:

- layered architecture;
- modular monolith;
- hexagonal architecture;
- ports and adapters;
- event-driven architecture;
- microservices;
- serverless;
- plugin architecture;
- pipeline architecture;
- other domain-specific approaches.

Document why the chosen architecture is appropriate.

Do not introduce distributed systems unless the problem actually requires them.

---

# 6. Domain Boundaries

Identify major domains or modules.

For each boundary determine:

```text
Responsibility
Public interface
Owned data
Dependencies
Allowed consumers
Forbidden dependencies
```

Make boundaries enforceable where practical.

---

# 7. Data Architecture

Determine whether the project requires persistent data.

If yes, decide:

- database type;
- schema strategy;
- migrations;
- transactions;
- consistency model;
- caching;
- backups;
- retention;
- data ownership;
- encryption.

If multiple data stores exist, document why each exists.

---

# 8. API and Interface Strategy

Determine how components communicate.

Potential interfaces include:

- REST;
- GraphQL;
- gRPC;
- events;
- message queues;
- command interfaces;
- files;
- internal APIs.

For each public interface define:

- versioning;
- validation;
- error handling;
- authentication;
- authorization;
- compatibility policy;
- documentation.

---

# 9. Configuration and Secrets

Decide:

- configuration format;
- environment variables;
- configuration files;
- secret management;
- local development configuration;
- production configuration.

Never commit secrets.

Clearly distinguish:

```text
Configuration
vs.
Secret
vs.
Runtime state
```

---

# 10. External Dependencies

List important external systems.

For each dependency record:

```text
Purpose
Owner
Authentication
Failure behavior
Rate limits
Versioning
Fallback strategy
Testing strategy
```

Avoid unnecessary external dependencies.

Consider the consequences if an external service becomes unavailable or changes its API.

---

# 11. Testing Strategy

Define the testing pyramid appropriate for the project.

Determine the expected balance between:

- unit tests;
- integration tests;
- contract tests;
- end-to-end tests;
- smoke tests;
- property-based tests;
- performance tests;
- security tests.

Define what must run:

- locally;
- on every PR;
- on merge;
- before release;
- periodically.

Testing should verify behavior, not merely increase coverage numbers.

---

# 12. Quality Standards

Define:

- formatting;
- linting;
- type checking;
- static analysis;
- coverage expectations;
- complexity rules;
- dependency policies;
- code review expectations.

Decide which checks are:

```text
Mandatory
Recommended
Optional
```

Automate mandatory checks.

---

# 13. CI/CD

Determine:

### CI

What happens on:

- push;
- pull request;
- merge?

### CD

Is deployment:

- manual;
- automatic;
- environment-promoted?

Define environments where applicable:

```text
local
development
staging
production
```

Document promotion rules and rollback procedures.

---

# 14. Deployment Architecture

Determine:

- where the application runs;
- how it is packaged;
- how it is deployed;
- how configuration is injected;
- how versions are identified;
- how rollback works.

Potential environments include:

- local machines;
- VMs;
- containers;
- Kubernetes;
- serverless;
- managed platforms;
- self-hosted infrastructure.

Choose based on requirements rather than complexity.

---

# 15. Observability

Determine what needs to be observable.

Consider:

- structured logs;
- metrics;
- tracing;
- health checks;
- audit logs;
- alerts.

Define how an engineer can answer:

> "What is the system doing right now, and why did this operation fail?"

For agent-heavy systems, also consider recording:

- agent actions;
- tool invocations;
- task identifiers;
- relevant execution metadata;
- failures;
- human approvals.

Do not log secrets or sensitive data.

---

# 16. Security Architecture

Determine:

- authentication;
- authorization;
- trust boundaries;
- secret management;
- encryption;
- dependency security;
- input validation;
- sandboxing;
- audit requirements.

For AI-agent systems additionally determine:

```text
What can agents read?
What can agents write?
What can agents execute?
What requires approval?
What actions are forbidden?
```

Use least privilege.

If the product itself uses an LLM or agent (not only for development), also determine:

```text
Which inputs are untrusted (users, documents, web, emails, tool output)?
Which sensitive data or systems can the model reach?
Which actions can it take (write data, send messages, call APIs)?
Which features combine all three (Rule of Two), and where does a human confirm?
How is model output validated before it is executed, rendered or stored?
What is logged, and how are prompts and outputs kept free of secrets?
```

Use the OWASP Top 10 for Agentic Applications (ASI01 to ASI10) as the checklist (`docs/security/threat-model.md` once it exists).

---

# 17. AI Agent Architecture

If AI agents are part of the project, decide whether the project needs:

- a common Agent Contract;
- agent-specific adapters;
- skills;
- tools;
- MCP integrations;
- subagents;
- orchestration;
- persistent task state;
- agent memory;
- approval gates;
- execution sandboxing.

If agents keep persistent memory, decide what may be stored, who reviews it, and how it is reset. Memory must not hold secrets or instructions copied from untrusted sources.

Separate:

```text
Project rules
from
Agent implementation details
```

The project rules should remain model/provider independent.

---

# 18. Skills and Tools

For each proposed skill or tool ask:

1. What problem does it solve?
2. Why should it be reusable?
3. What inputs does it accept?
4. What outputs does it produce?
5. What permissions does it require?
6. Can it fail safely?
7. How is it tested?
8. Who owns it?

Do not create a skill when a simple command or documented procedure is sufficient.

---

# 19. Subagent Strategy

Determine whether subagents actually provide value.

Potential specialist roles:

- Architect
- Developer
- Tester
- Reviewer
- Security Reviewer
- Documentation Agent
- Release Agent

For each subagent define:

```text
Responsibilities
Inputs
Outputs
Allowed tools
Required approvals
Success criteria
```

Prefer deterministic workflows for simple tasks.

Use multi-agent orchestration when complexity justifies it.

---

# 20. Agent Autonomy Levels

Define explicit autonomy levels.

For example:

### Level 0: Read-only

Agent can inspect but cannot modify the repository.

### Level 1: Local development

Agent may modify code and run local commands.

### Level 2: Repository contribution

Agent may create branches, commits, Issues, and PRs.

### Level 3: Automated integration

Agent may merge or trigger controlled workflows.

### Level 4: Operational automation

Agent may interact with deployment or infrastructure systems.

The exact levels should be adapted to the project's risk profile.

Production access should generally require stronger controls than local development.

---

# 21. Git and GitHub Strategy

Define:

- default branch;
- branch naming;
- commit conventions;
- PR requirements;
- review requirements;
- merge strategy;
- release strategy;
- tagging;
- changelog policy.

Determine whether commits should follow a convention such as Conventional Commits.

Do not impose one unless it provides value.

---

# 22. Release Strategy

Determine:

- versioning strategy;
- release cadence;
- changelog generation;
- release notes;
- tags;
- artifacts;
- rollback;
- compatibility guarantees.

For libraries and APIs, explicitly define compatibility policy.

---

# 23. Documentation Strategy

Determine which documentation is required.

Potential categories:

```text
README
Architecture
ADR
Development
API
Operations
Security
Runbooks
Agent documentation
Troubleshooting
Release documentation
```

Every document should have an owner or clear maintenance mechanism.

Avoid documentation that merely duplicates the code.

---

# 24. ADR Strategy

Use ADRs for decisions that would be expensive or confusing to rediscover later.

Good ADR candidates include:

- major architecture;
- database selection;
- framework selection;
- deployment model;
- authentication strategy;
- API strategy;
- agent architecture;
- orchestration strategy;
- security boundaries;
- major technology replacements.

Do not create ADRs for trivial implementation details.

---

# 25. Failure and Recovery

For important components determine:

- expected failures;
- retry behavior;
- timeout behavior;
- fallback behavior;
- idempotency;
- recovery;
- rollback;
- data consistency.

For agent workflows additionally consider:

- agent interruption;
- tool failure;
- partial execution;
- duplicate execution;
- context loss;
- conflicting agents;
- abandoned branches;
- stale Issues.

---

# 26. Scalability

Do not optimize for hypothetical scale.

Instead identify actual expected growth:

```text
Users:
Requests:
Data:
Repositories:
Agents:
Concurrent tasks:
Deployment frequency:
```

Then determine which components actually require scalability.

---

# 27. Cost

For professional or production projects, identify significant cost drivers:

- infrastructure;
- databases;
- external APIs;
- AI model usage;
- CI;
- storage;
- observability;
- networking.

For personal projects, explicitly optimize for simplicity and low maintenance where appropriate.

---

# 28. Maintenance

Consider the expected maintenance burden.

Ask:

- Who will maintain this?
- How often will dependencies change?
- How easy is onboarding?
- How much infrastructure must be operated?
- Can another agent understand the system?
- What happens if the original author disappears?

Prefer architectures that remain understandable over time.

---

# 29. Decision Record

After completing the analysis, create a concise project architecture summary.

It should answer:

```text
Project type:
Primary language:
Runtime:
Repository structure:
Application architecture:
Data architecture:
API strategy:
Testing strategy:
CI/CD:
Deployment:
Observability:
Security model:
Agent model:
Agent autonomy:
Skills/tools:
Subagent strategy:
Release strategy:
Documentation strategy:
Major constraints:
Known risks:
```

Then create ADRs for the decisions that deserve long-term historical context.

---

# 30. Architecture Review Checklist

Before declaring the initial architecture complete, verify:

- [ ] Requirements are understood
- [ ] Constraints are documented
- [ ] Technology choices have justification
- [ ] Module boundaries are defined
- [ ] Data ownership is clear
- [ ] External dependencies are understood
- [ ] Testing strategy exists
- [ ] CI strategy exists
- [ ] Security boundaries are defined
- [ ] Deployment strategy exists
- [ ] Observability requirements are understood
- [ ] Failure modes have been considered
- [ ] Agent permissions are defined
- [ ] Agent workflow is documented
- [ ] Documentation structure exists
- [ ] Important decisions have ADRs
- [ ] Initial Issues have been created
- [ ] The architecture is no more complex than necessary

---

# 31. Guiding Principle

Architecture is not a collection of technologies.

Architecture is the set of decisions that determine:

```text
What exists
+
How components interact
+
Who owns what
+
What is allowed
+
What happens when things fail
+
How the system evolves
```

Make those decisions explicit.

When requirements change, revisit the relevant decisions rather than silently accumulating exceptions.