# Contributing to Logistics Twin

First off, thank you for considering contributing to Logistics Twin! 🎉

This project is an **AI-powered logistics optimization platform** using Reinforcement Learning to solve the Traveling Salesman Problem for dynamic supply chain management.

## 🌟 Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? Open an issue!
- ✨ **Feature Requests**: Have an idea? We'd love to hear it!
- 📝 **Documentation**: Improve our docs
- 💻 **Code**: Submit pull requests
- 🧪 **Testing**: Help us test new features
- 🎨 **Design**: UI/UX improvements

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git
- Basic understanding of Flask and Reinforcement Learning (helpful)

### Development Setup

1. **Fork & Clone**
```bash
git clone https://github.com/YOUR-USERNAME/logistics-twin.git
cd logistics-twin
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Tests**
```bash
pytest -v
```

5. **Start Development Server**
```bash
python app.py
```

Visit http://localhost:5000

## 📋 Development Workflow

### 1. Create a Branch

Follow our branching strategy (see `BRANCHING_STRATEGY.md`):

```bash
# For features
git checkout -b feature/your-feature-name

# For bugs
git checkout -b bugfix/issue-description

# For hotfixes
git checkout -b hotfix/critical-fix
```

### 2. Make Changes

- Follow the existing code style
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

### 3. Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add city export to CSV
fix: resolve map editor validation bug
docs: update API documentation
test: add tests for disaster system
refactor: extract component CSS
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### 4. Run Tests

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_app.py -v

# With coverage
pytest --cov=. --cov-report=term-missing
```

### 5. Submit Pull Request

1. Push to your fork
2. Open a Pull Request against `main`
3. Fill out the PR template
4. Wait for review

## 🎨 Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Keep functions small and focused
- Document complex logic

Example:
```python
def calculate_route_cost(distance: float, vehicle_type: str) -> float:
    """
    Calculate total cost for a route.
    
    Args:
        distance: Route distance in kilometers
        vehicle_type: Type of vehicle (diesel, ev, hybrid)
        
    Returns:
        Total cost in Rupiah
    """
    # Implementation
```

### JavaScript
- Use `const` and `let`, avoid `var`
- Meaningful variable names
- Comment complex logic

### CSS
- Use design tokens from `@design-rules.md`
- Avoid inline styles
- Follow BEM naming: `.block__element--modifier`

## 🧪 Testing Guidelines

### What to Test
- New features (100% coverage)
- Bug fixes (regression test)
- Edge cases
- Error handling

### Test Structure
```python
def test_feature_description():
    # Arrange: Set up test data
    agent = QLearningAgent(cities_data)
    
    # Act: Execute the function
    result = agent.train_episode()
    
    # Assert: Verify the outcome
    assert result is not None
    assert len(result) > 0
```

## 📝 Documentation

Update these files when relevant:
- `README.md` - Overview and setup
- `CHANGELOG.md` - Version history
- `@design-rules.md` - Design system
- `roadmap.md` - Feature planning

## 🐛 Bug Reports

Use the bug report template and include:
- **Description**: What's wrong?
- **Steps to Reproduce**: How to trigger the bug?
- **Expected Behavior**: What should happen?
- **Actual Behavior**: What actually happens?
- **Environment**: OS, Python version, browser
- **Screenshots**: If applicable

## ✨ Feature Requests

Use the feature request template and include:
- **Problem**: What problem does this solve?
- **Solution**: Your proposed solution
- **Alternatives**: Other approaches considered
- **Use Case**: Real-world scenario

## 🔍 Review Process

1. **Automated Checks**: CI/CD runs tests
2. **Code Review**: Maintainer reviews code
3. **Changes Requested**: Address feedback
4. **Approval**: PR gets merged!

### Review Criteria
- ✅ Tests passing
- ✅ Code style consistent
- ✅ Documentation updated
- ✅ No breaking changes (or documented)
- ✅ Follows design patterns

## 🎯 Priority Areas

**V5.x (Current):**
- Map editor enhancements
- Mobile responsiveness
- Input validation

**V6.0 (Planned):**
- Atomic design system
- Component extraction
- Performance optimization

See `roadmap.md` for details.

## 🤝 Community

- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Email**: (if available)

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Appreciated forever! ❤️

## ❓ Questions?

- Check existing issues
- Read the documentation
- Ask in GitHub Discussions
- Open a new issue

---

**Thank you for contributing to Logistics Twin!** 🚀

Every contribution, no matter how small, makes a difference!
