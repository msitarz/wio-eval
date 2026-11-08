# Thin entry points. The checks themselves are defined in prek.toml (hooks) and
# pyproject.toml (tool settings), so local runs and CI use the same commands.

.DEFAULT_GOAL := help
.PHONY: help install lint test check build slow audit secrets clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-z-]+:.*## / {printf "  %-8s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# A linked worktree gets its own hooks directory through a per-worktree
# core.hooksPath, so installing there never rewrites the hooks of another
# worktree, which would point at the venv of the worktree that ran it last.
install: ## Sync the environment and install the git hooks
	uv sync --locked
	@if [ "$$(git rev-parse --absolute-git-dir)" != "$$(git rev-parse --path-format=absolute --git-common-dir)" ]; then \
		hooks="$$(git rev-parse --absolute-git-dir)/hooks"; \
		mkdir -p "$$hooks"; \
		git config extensions.worktreeConfig true; \
		git config --worktree core.hooksPath "$$hooks"; \
	fi
	uv run prek install

# Extra hook ids to skip, e.g. `make lint SKIP=gitleaks` (prek's --skip flag
# replaces the SKIP environment variable, so lint forwards it explicitly).
SKIP ?=

lint: ## Run every hook except pytest on all files
	uv run prek run --all-files --skip pytest $(addprefix --skip ,$(SKIP)) --show-diff-on-failure

test: ## Run the fast tests with coverage
	uv run prek run pytest --all-files --show-diff-on-failure

check: lint test ## Run lint and tests

build: ## Build the package and verify the artifacts
	uv run pytest -m slow tests/packaging

slow: ## Run every slow test: subprocesses and packaging
	uv run pytest -m slow

audit: ## Check the locked dependencies for known vulnerabilities
	uv audit --locked --preview-features audit-command

secrets: ## Scan the full git history for secrets (needs gitleaks)
	@command -v gitleaks >/dev/null || { echo "gitleaks not found: brew install gitleaks"; exit 1; }
	gitleaks git --redact --verbose

clean: ## Remove build outputs and tool caches
	rm -rf dist htmlcov .coverage .pytest_cache .ruff_cache .rumdl_cache .complexipy_cache
