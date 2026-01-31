# Contributing Guide

Thank you for your interest in contributing to the Fleet Decision Platform!

## Ways to Contribute

- **Code:** New features, bug fixes, optimizations
- **Documentation:** Improve guides, fix typos, add examples
- **Testing:** Add test cases, improve coverage
- **Issues:** Report bugs, suggest features

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/fleet-cascade.git
cd fleet-cascade

# Add upstream remote
git remote add upstream https://github.com/yourusername/fleet-cascade.git
```

### 2. Set Up Development Environment

```bash
# Install all dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Verify setup
uv run pytest tests/ -v
```

### 3. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

## Development Workflow

### Make Changes

1. Write code following [Code Style](code-style.md) guidelines
2. Add/update tests for your changes
3. Update documentation if needed
4. Run tests locally

### Test Your Changes

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_forecasting.py -v
```

### Lint and Format

```bash
# Check code style
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Commit Changes

Follow conventional commit messages:

```bash
# Feature
git commit -m "feat(module): add new capability"

# Bug fix
git commit -m "fix(module): resolve issue with X"

# Documentation
git commit -m "docs(section): update installation guide"

# Tests
git commit -m "test(module): add unit tests for Y"

# Refactor
git commit -m "refactor(module): simplify Z implementation"
```

### Push and Create PR

```bash
# Push branch
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Title

Use conventional commit format:

```
feat(forecasting): add Prophet model support
fix(api): handle empty request body
docs(readme): update quick start section
```

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added/updated documentation
- [ ] No new warnings
```

### PR Review Process

1. Automated checks run (tests, linting)
2. Maintainer reviews code
3. Address feedback
4. Approval and merge

## Code Review Guidelines

### For Authors

- Keep PRs focused and small
- Explain the "why" in PR description
- Respond to feedback promptly
- Be open to suggestions

### For Reviewers

- Be constructive and specific
- Explain reasoning for suggestions
- Approve when satisfied
- Use suggestions feature for small fixes

## Development Standards

### Code Quality

- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] No hardcoded values (use config)
- [ ] Error handling with custom exceptions
- [ ] Logging at appropriate levels

### Testing

- [ ] Unit tests for new functions
- [ ] Integration tests for new endpoints
- [ ] Edge cases covered
- [ ] Fixtures used appropriately

### Documentation

- [ ] Docstrings updated
- [ ] README updated if needed
- [ ] API docs updated for new endpoints
- [ ] User guide updated for new features

## Issue Guidelines

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered
- Willingness to implement

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- Documentation acknowledgments

## Questions?

- Check [GitHub Discussions](https://github.com/yourusername/fleet-cascade/discussions)
- Review existing issues
- Reach out to maintainers

Thank you for contributing! 🎉
