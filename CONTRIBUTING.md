# CONTRIBUTORS

Thank you for your interest in contributing to **dataspiderai**! This document gathers all the information you need to get started and guides you through our contribution process.

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/jorvalalb/dataspiderai.git
   cd dataspiderai
   ```

2. **Create and activate a development environment**  
   We use `uv` to manage environments and dependencies:
   ```bash
   pip install --user uv
   uv venv create dataspiderai-dev
   dataspiderai-dev\Scripts\activate      # Windows
   ```

3. **Install dependencies**  
   ```bash
   uv sync --active
   ```

4. **Install the package in editable mode**  
   ```bash
   uv pip install -e .
   ```

5. **Create a feature branch**  
   ```bash
   git checkout -b feature/your-feature-name
   ```

6. **Make your changes**  
   - Follow existing style and patterns.  
   - Keep your scope narrow and focused.  
   - Add tests for new functionality or bug fixes.  
   - Update documentation (`README.md`, docstrings, CLI help, etc.) as needed.

7. **Commit and push**  
   ```bash
   git add .
   git commit -m "Brief description of your change"
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** on GitHub  
   - Link to any relevant issues.  
   - Describe what you’ve changed and why.  
   - Ensure CI passes and that you’ve updated docs/tests.

---

## Types of Contributions

### Report a Bug
- Include your OS, Python version, and reproduction steps.  
- Provide error messages or stack traces.

### Fix a Bug
- Look for issues labeled `bug` or `help wanted`.  
- Include or update tests to cover the bug scenario.

### Implement a Feature
- Review issues labeled `enhancement` or `help wanted`.  
- Propose your design first if it’s a large change.

### Improve Documentation
- Clarify existing docs or add new examples.  
- Update inline docstrings and CLI help messages.

### Submit Feedback
- Suggest improvements or use-case ideas.  
- Keep proposals focused and actionable.

---

## Pull Request Guidelines

1. Keep your PR up to date with `main`.  
2. Include tests for any new behavior.  
3. Update documentation where applicable.  
4. Keep commits atomic and descriptive.  
5. Reference the issue number in your PR title or description.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.

---

Thank you for helping make **dataspiderai** even better! 🚀
