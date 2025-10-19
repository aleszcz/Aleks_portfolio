# Contributing to GenoScope

Thank you for your interest in contributing to GenoScope! This document provides guidelines and instructions for contributing.

## 🎯 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages/logs if applicable

### Suggesting Features

We love feature suggestions! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (optional)

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/genoscope.git
   cd genoscope
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   python -m pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes clearly

## 📝 Code Style Guidelines

- Use Python 3.8+ features
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write descriptive variable names
- Add docstrings to functions and classes

Example:
```python
async def search_genomics_data(
    self, 
    query: str, 
    database: str = "nuccore",
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Search NCBI databases for genomics data.
    
    Args:
        query: Search terms (e.g., "BRCA1 human")
        database: NCBI database name
        max_results: Maximum number of results
        
    Returns:
        List of search results with metadata
    """
    # Implementation here
```

## 🧪 Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Test with different query types
- Check edge cases

## 📚 Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Include usage examples
- Update CHANGELOG.md

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Give constructive feedback
- Acknowledge contributions

## 📞 Questions?

- Create an issue for questions
- Join discussions in existing issues
- Check documentation first

## 🙏 Thank You!

Your contributions help make genomics research more accessible to everyone!
