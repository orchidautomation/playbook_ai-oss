# Developer Documentation

Welcome to the OctaveHQ Clone developer documentation. This directory contains all technical documentation for contributors and developers.

## Quick Start

New to the project? Start here:
1. Read the [Architecture Overview](architecture/ARCHITECTURE.md)
2. Review the [Implementation Plan](architecture/IMPLEMENTATION_PLAN.md)
3. Check out [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines

## Directory Structure

### `/architecture` - System Design & Technical Decisions

Technical architecture, design patterns, and compliance:
- **[ARCHITECTURE.md](architecture/ARCHITECTURE.md)** - Complete system architecture and design patterns
- **[IMPLEMENTATION_PLAN.md](architecture/IMPLEMENTATION_PLAN.md)** - Detailed implementation roadmap
- **[AGNO_COMPLIANCE_AUDIT.md](architecture/AGNO_COMPLIANCE_AUDIT.md)** - Framework compliance review (6.9/10 score, 800+ lines)

### `/simplification` - Code Quality & Optimization

Code simplification journey and future improvements:
- **[SIMPLIFICATION_COMPLETE.md](simplification/SIMPLIFICATION_COMPLETE.md)** - V1 simplification summary (current implementation)
- **[SIMPLIFICATION_EXAMPLES.md](simplification/SIMPLIFICATION_EXAMPLES.md)** - Before/after code examples
- **[SIMPLIFICATION_V2.md](simplification/SIMPLIFICATION_V2.md)** - Future optimization approach with technical deep dive

**Key Insights:**
- V1: Uses `get_step_content()` with centralized deserialization helper
- V2: Optional upgrade to `get_step_output()` with `.steps` list (no deserialization needed)
- 141 lines removed (14.2% reduction) in V1 simplification

### `/examples` - Code Examples & Patterns

Working code examples and guides:
- **[parallel-outputs/](examples/parallel-outputs/)** - Agno parallel workflow examples and guides

## Core Codebase Structure

```
octave-clone/
├── workflows/        # Agno workflow definitions
├── steps/            # Individual workflow step functions
├── agents/           # AI agent definitions
├── models/           # Pydantic data models
├── utils/            # Helper functions (includes workflow_helpers.py)
├── tests/            # Test suite
└── archive/          # Archived test files and experiments
```

## Key Technical Concepts

### Agno Workflow Framework
This project uses the [Agno framework](https://docs.agno.com) for orchestrating multi-step AI agent workflows.

**Important Patterns:**
- **Parallel Blocks**: Steps that execute concurrently
- **Fail-Fast Validation**: Workflows stop immediately on errors using `stop=True`
- **Structured Outputs**: Custom executors return dicts (get serialized in parallel blocks)
- **StepInput/StepOutput**: Interfaces for data flow between steps

### Serialization Behavior
When custom executors return structured dicts in parallel blocks, Agno serializes them to strings when accessed via `get_step_content()`. We handle this with a centralized helper:

```python
from utils.workflow_helpers import get_parallel_step_content

# Access parallel step data with automatic deserialization
vendor_data = get_parallel_step_content(
    step_input,
    "parallel_validation",
    "validate_vendor"
)
```

**Why this happens**: See [SIMPLIFICATION_V2.md](simplification/SIMPLIFICATION_V2.md#technical-deep-dive-why-this-matters) for the complete technical explanation.

## Testing

Run the test suite:
```bash
python test_simplifications.py
```

Test files:
- `tests/` - Main test suite
- `archive/simplification_tests/` - Proof-of-concept tests demonstrating serialization behavior

## Future Improvements

See **[NEXT_STEPS.md](NEXT_STEPS.md)** for:
- V2 optimization using `get_step_output()` (~70 minutes)
- Performance improvements
- No deserialization overhead

## Contributing

Ready to contribute? Check out **[CONTRIBUTING.md](../../CONTRIBUTING.md)** for:
- Development setup
- Coding standards
- Pull request process
- Testing requirements

## Need Help?

- **Architecture questions**: See [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md)
- **Code simplification**: See [simplification/SIMPLIFICATION_V2.md](simplification/SIMPLIFICATION_V2.md)
- **Agno framework**: See [examples/parallel-outputs/](examples/parallel-outputs/)
- **Setup issues**: See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## Project Context

This is an OctaveHQ clone - a sales intelligence platform that analyzes vendor and prospect companies to generate personalized sales playbooks.

**Workflow Phases:**
1. **Phase 1**: Intelligence Gathering (domain validation, scraping)
2. **Phase 2**: Vendor Element Extraction (8 GTM elements)
3. **Phase 3**: Prospect Intelligence (pain points, buyer personas)
4. **Phase 4**: Sales Playbook Generation (battle cards, email sequences)

See [artifacts/](../../artifacts/README.md) for phase outputs and [docs/phases/](../phases/) for completion summaries.
