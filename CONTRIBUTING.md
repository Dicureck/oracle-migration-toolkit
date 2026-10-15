# Contributing

Thanks for considering improvements to Oracle Migration Toolkit.

1. File an issue describing a reproducible *fictional* example; never attach commercial SQL or client data.
2. Add a test for each bug fix or new static detection rule.
3. Run `python -m unittest discover -s tests -v` before opening a pull request.
4. Prefer semantic documentation and compatibility notes over naive SQL string substitutions.
5. Explain validation scope precisely. Offline fixture parity is not cross-engine parity.
6. Do not add SQL that mutates production-style schemas, copied customer procedures, credentials or private endpoints.

Use Python 3.11+ and standard-library modules for core features unless there is a clear technical reason to add a dependency.
