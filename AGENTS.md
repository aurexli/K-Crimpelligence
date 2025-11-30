# AGENTS Guide for pydanticAI

## Project Overview
- A minimal example demonstrating **Pydantic AI** to build a bank support agent.
- Core file: `main.py` contains the agent definition, dependencies, and example runs.

## Key Concepts
- **Agent**: `support_agent = Agent('openai:gpt-5.1', deps_type=SupportDependencies, output_type=SupportOutput, instructions=... )`
- **Dependencies** (`SupportDependencies`): `customer_id` and a fake `DatabaseConn` providing async methods.
- **Output Model** (`SupportOutput`): fields `support_advice`, `block_card`, `risk`.
- **Tools**: `customer_balance` defined via `@support_agent.tool` for balance lookup.
- **Instructions**: Added via `@support_agent.instructions` to prepend customer name.

## Running the Example
```bash
# Install the library (if not already installed)
pip install pydantic-ai

# Run the example directly
python main.py
```
The script prints two example interactions:
1. Query balance – returns `support_advice`, `block_card=False`, `risk=1`.
2. Report lost card – returns `support_advice`, `block_card=True`, `risk=8`.

## Code Structure
- `main.py`
  - `DatabaseConn`: async mock methods `customer_name` and `customer_balance`.
  - `SupportDependencies`: dataclass for injecting dependencies.
  - `SupportOutput`: Pydantic model for agent response.
  - Agent definition and tooling.
  - `if __name__ == '__main__':` block demonstrating usage.

## Naming & Style Conventions
- **Classes**: `CamelCase` (e.g., `DatabaseConn`).
- **Functions/Methods**: `snake_case` (e.g., `customer_name`).
- **Dataclasses**: suffix `Dependencies` for injected services.
- **Pydantic Models**: suffix `Output`.
- **Agent variable**: lower_snake with `*_agent` suffix.
- Use type hints and async where appropriate.

## Gotchas & Tips
- The example relies on the `pydantic_ai` package; ensure compatible version.
- Async methods in `DatabaseConn` are simple stubs – replace with real DB calls in production.
- The `Agent` is instantiated with model identifier `'openai:gpt-5.1'`; adjust to your model provider if needed.
- No tests are included; add unit tests for custom tools and dependencies if extending.

## Extending the Project
1. **Add Real Database**: Implement `DatabaseConn` with actual async DB driver.
2. **Create More Tools**: Decorate additional async functions with `@support_agent.tool`.
3. **Write Tests**: Use `pytest` to test tool functions and agent outputs.
4. **CLI Wrapper**: Convert the `if __name__ == '__main__'` block into a Click/argparse CLI for flexible interaction.

## References
- `main.py` – core implementation.
- Pydantic AI documentation for `Agent`, `RunContext`, and tool creation.
