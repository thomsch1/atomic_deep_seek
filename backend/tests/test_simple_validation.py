"""
Simple validation tests to verify the testing framework works.
"""

import pytest
import asyncio


def test_basic_functionality():
    """Test that pytest is working correctly."""
    assert 1 + 1 == 2
    assert "hello" in "hello world"


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert 3 in test_list
    assert max(test_list) == 5


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality works."""
    async def async_add(a, b):
        await asyncio.sleep(0.01)  # Simulate async operation
        return a + b
    
    result = await async_add(2, 3)
    assert result == 5


class TestClassExample:
    """Test class example."""
    
    def test_string_methods(self):
        """Test string methods."""
        s = "hello world"
        assert s.upper() == "HELLO WORLD"
        assert s.split() == ["hello", "world"]
    
    def test_dictionary_operations(self):
        """Test dictionary operations."""
        d = {"a": 1, "b": 2}
        assert d["a"] == 1
        assert "b" in d
        assert len(d) == 2


def test_exception_handling():
    """Test exception handling."""
    with pytest.raises(ValueError):
        int("not_a_number")
    
    with pytest.raises(KeyError):
        d = {"key1": "value1"}
        _ = d["missing_key"]


@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4), 
    (3, 6),
    (0, 0)
])
def test_parametrized(input, expected):
    """Test parametrized testing."""
    assert input * 2 == expected


def test_mock_usage():
    """Test mock functionality."""
    from unittest.mock import Mock
    
    mock_func = Mock(return_value=42)
    result = mock_func()
    
    assert result == 42
    mock_func.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])