# Standard commands for humans, agents and CI. Run `make help` for the list.
# Projects created from the template fill in the stack-specific targets
# (test, build, typecheck) and keep the names, so every repository works the
# same way (AGENTS.md §4).

.DEFAULT_GOAL := help
.PHONY: help setup lint format links security test ci

PRE_COMMIT ?= pre-commit

help: ## List the commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  make %-10s %s\n", $$1, $$2}'

setup: ## Install the Git hooks and build them (once per clone)
	$(PRE_COMMIT) install --install-hooks

lint: ## All checks on every file: style, syntax, links, workflows
	$(PRE_COMMIT) run --all-files

format: ## Fix what can be fixed automatically (end of files, trailing spaces)
	-$(PRE_COMMIT) run end-of-file-fixer --all-files
	-$(PRE_COMMIT) run trailing-whitespace --all-files

links: ## Check relative links and headings in Markdown
	python3 scripts/check_links.py

security: ## Scan every commit in the Git history for secrets
	$(PRE_COMMIT) run gitleaks-history --hook-stage manual --all-files

test: ## Run the tests (this template has none; projects add theirs here)
	@echo "No tests in this template. Projects: replace this with the test command."

ci: lint security test ## What CI runs on every pull request
