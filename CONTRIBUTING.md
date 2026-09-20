# Contributing to Inv1s1bl3 Bot

Thank you for your interest in contributing to **Inv1s1bl3 Bot**! This project is maintained as an open-source revival and legacy showcase.

---

## Code of Conduct
Please be respectful, constructive, and helpful when participating in discussions, reporting issues, or submitting pull requests.

---

## How to Contribute

### 1. Reporting Bugs
- Search existing GitHub Issues before submitting a new report.
- Use the **Bug Report** issue template.
- Include reproduction steps, environment details (Python version, OS), and error tracebacks.

### 2. Suggesting Features
- Open a discussion or issue using the **Feature Request** template.
- Note: Because this is a preserved legacy project, major redesigns that deviate from the bot's historical character may be declined, but bug fixes, performance improvements, and documentation enhancements are always welcome.

### 3. Pull Requests
1. Fork the repository and create a descriptive feature branch (`git checkout -b feature/my-enhancement`).
2. Follow PEP 8 guidelines and maintain typing annotations.
3. Run the automated test suite before committing:
   ```bash
   pytest -v
   ```
4. Verify code compiles cleanly:
   ```bash
   python -m compileall -q src tests scripts
   ```
5. Submit your pull request with a clear description of the problem solved.
