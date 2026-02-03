# Lint and Format Skill
Description: Ensure Python code adheres to Ruff standards.
Actions:
  - Run `ruff check --fix .`
  - Run `ruff format .`
Rule: "Never submit code that has T201 (print) or F401 (unused import) violations."