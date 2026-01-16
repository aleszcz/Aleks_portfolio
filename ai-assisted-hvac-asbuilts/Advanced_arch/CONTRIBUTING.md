# Contributing to RevitAssist

Thank you for considering contributing to RevitAssist! This document outlines how to contribute effectively.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other contributors

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Collect relevant information (OS, Revit version, error messages)

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Revit Version: [e.g., 2024]
- Plugin Version: [e.g., 1.0.0]
- Python Version: [e.g., 3.9]

**Additional context**
Any other relevant information.
```

### Suggesting Features

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other relevant information.
```

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## Development Setup

### Python Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code style
black AIBackend/
flake8 AIBackend/

# Type checking
mypy AIBackend/
```

### C# Development

```bash
# Build in debug mode
dotnet build --configuration Debug

# Run tests
dotnet test
```

## Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Maximum line length: 88 (Black default)

**Example:**
```python
def process_drawing(
    pdf_path: str,
    level: str = "Level 1"
) -> ProcessingResult:
    """
    Process HVAC drawing.
    
    Args:
        pdf_path: Path to PDF file
        level: Target Revit level
        
    Returns:
        Processing result with components
    """
    pass
```

### C#

- Follow Microsoft C# coding conventions
- Use meaningful variable names
- Add XML documentation comments

**Example:**
```csharp
/// <summary>
/// Processes the HVAC drawing
/// </summary>
/// <param name="filePath">Path to drawing file</param>
/// <returns>Processing result</returns>
public Result ProcessDrawing(string filePath)
{
    // Implementation
}
```

## Testing

### Python Tests

```python
# tests/test_processor.py

def test_component_detection():
    """Test that components are detected correctly"""
    processor = HVACProcessor("models/test.pt")
    result = processor.process_drawing("test.pdf")
    
    assert len(result.components) > 0
    assert result.avg_confidence > 0.5
```

### Integration Tests

Test the complete workflow:
1. Import drawing
2. Process with AI
3. Insert to Revit
4. Verify created elements

## Documentation

- Update README.md for new features
- Add docstrings to all functions
- Create examples for new functionality
- Update CHANGELOG.md

## Priority Areas for Contribution

### High Priority

- [ ] Support for additional HVAC component types
- [ ] Improved connection inference
- [ ] Performance optimization
- [ ] Better error handling

### Medium Priority

- [ ] Multi-floor support
- [ ] Batch processing
- [ ] Export to other CAD formats
- [ ] Web UI for configuration

### Low Priority (but welcome!)

- [ ] Additional language support
- [ ] Dark mode for UI
- [ ] Custom component libraries
- [ ] Integration with other tools

## Release Process

1. Update version in all relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Tag release: `git tag v1.0.0`
5. Build release artifacts
6. Create GitHub release
7. Update documentation

## Questions?

- Open a [Discussion](https://github.com/yourusername/RevitAssist/discussions)
- Email: your.email@example.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make RevitAssist better! 🎉
