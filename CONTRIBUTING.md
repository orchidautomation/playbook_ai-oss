# Contributing to OctaveHQ Clone

Thank you for your interest in contributing to the OctaveHQ Clone project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Agno SDK installed
- API keys for required services (see `.env.example`)

### First Time Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/octave-clone.git
   cd octave-clone
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Run tests** to verify setup:
   ```bash
   python test_simplifications.py
   ```

## Development Setup

### Understanding the Codebase

Before contributing, familiarize yourself with:
1. **[Developer Documentation](docs/developers/README.md)** - Complete technical documentation
2. **[Architecture](docs/developers/architecture/ARCHITECTURE.md)** - System design and patterns
3. **[Simplification Guide](docs/developers/simplification/SIMPLIFICATION_V2.md)** - Code quality standards

### Key Concepts

This project uses the **Agno workflow framework** for orchestrating multi-step AI agent workflows.

**Important patterns:**
- **Parallel Blocks**: Concurrent step execution
- **Fail-Fast Validation**: Workflows stop on errors using `stop=True`
- **Structured Outputs**: Custom executors return dicts
- **Helper Functions**: Use `utils/workflow_helpers.py` for common operations

Example:
```python
from agno.workflow.types import StepInput, StepOutput
from utils.workflow_helpers import get_parallel_step_content

def your_step(step_input: StepInput) -> StepOutput:
    """Your step function with fail-fast validation"""

    # Get data from previous parallel block
    vendor_data = get_parallel_step_content(
        step_input,
        "parallel_validation",
        "validate_vendor"
    )

    # Fail-fast validation
    if not vendor_data:
        error_msg = "❌ Vendor data missing - cannot proceed"
        print(f"\n{error_msg}")
        return StepOutput(content=error_msg, stop=True)

    # Your step logic here...

    return StepOutput(content={"result": "success"})
```

## Project Structure

```
octave-clone/
├── workflows/              # Agno workflow definitions
├── steps/                  # Individual step functions
│   ├── step1_*.py
│   ├── step2_*.py
│   └── ...
├── agents/                 # AI agent definitions
├── models/                 # Pydantic data models
├── utils/                  # Helper functions
│   └── workflow_helpers.py # Centralized helpers
├── tests/                  # Test suite
├── docs/                   # Documentation
│   ├── developers/        # Technical documentation
│   ├── research/          # Business research
│   └── phases/            # Project milestones
├── marketing/             # Marketing materials
├── artifacts/             # Workflow outputs
└── archive/               # Archived experiments
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and returns
- Use descriptive variable names

### Agno Framework Best Practices

1. **Use centralized helpers**:
   ```python
   # ✅ Good - use helper
   from utils.workflow_helpers import get_parallel_step_content
   data = get_parallel_step_content(step_input, "block_name", "step_name")

   # ❌ Bad - manual deserialization
   data = step_input.get_step_content("block_name")["step_name"]
   if isinstance(data, str):
       data = ast.literal_eval(data)
   ```

2. **Always use fail-fast validation**:
   ```python
   # ✅ Good - stop on error
   if not data:
       return StepOutput(content="Error message", stop=True)

   # ❌ Bad - graceful degradation
   if not data:
       data = {}  # Don't do this!
   ```

3. **Pass Pydantic models directly** (don't use `.dict()` or `.model_dump()`):
   ```python
   # ✅ Good
   workflow.print_response(message=workflow_input)

   # ❌ Bad
   workflow.print_response(message=workflow_input.model_dump())
   ```

### Code Comments

- Use docstrings for all functions
- Explain *why*, not *what*
- Reference file:line for complex logic

### Git Commits

- Use descriptive commit messages
- Follow conventional commits format:
  ```
  feat: Add new vendor extraction step
  fix: Resolve serialization issue in step 3
  docs: Update architecture documentation
  test: Add tests for parallel block helpers
  refactor: Simplify step 2 validation logic
  ```

## Testing

### Running Tests

```bash
# Run all tests
python test_simplifications.py

# Run specific workflow phase
python test_phase2.py
```

### Writing Tests

- Test all new step functions
- Test edge cases and error handling
- Mock API calls when possible

Example test structure:
```python
def test_your_step():
    """Test your step function"""
    # Setup
    step_input = create_test_input()

    # Execute
    result = your_step(step_input)

    # Assert
    assert isinstance(result, StepOutput)
    assert result.content is not None
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test thoroughly**:
   ```bash
   python test_simplifications.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill out the PR template
   - Link any related issues
   - Wait for review

### PR Guidelines

- Keep PRs focused and single-purpose
- Write clear PR descriptions
- Include screenshots for UI changes
- Respond to review feedback promptly
- Ensure all tests pass

## Documentation

### When to Update Documentation

Update documentation when you:
- Add new features or steps
- Change workflow behavior
- Fix bugs that affect usage
- Add new helper functions

### Documentation Locations

- **Technical docs**: `docs/developers/`
- **API changes**: `docs/developers/architecture/ARCHITECTURE.md`
- **Code examples**: `docs/developers/examples/`
- **Setup instructions**: This file (CONTRIBUTING.md)

## Need Help?

- **Technical questions**: See [docs/developers/README.md](docs/developers/README.md)
- **Architecture questions**: See [docs/developers/architecture/ARCHITECTURE.md](docs/developers/architecture/ARCHITECTURE.md)
- **Code patterns**: See [docs/developers/simplification/SIMPLIFICATION_V2.md](docs/developers/simplification/SIMPLIFICATION_V2.md)
- **Agno framework**: See [docs/developers/examples/parallel-outputs/](docs/developers/examples/parallel-outputs/)

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Help others learn

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to OctaveHQ Clone! 🚀
