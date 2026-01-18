#!/usr/bin/env python3
"""
Test suite for PRISM_OF_COHERENCE protocol implementation.
"""

import pytest
from klipper_sdk.bridge import PrismProtocol, PrismResult, Signal


def test_prism_protocol_initialization():
    """Test that PrismProtocol can be initialized."""
    prism = PrismProtocol()
    assert prism is not None


def test_ingest_normal_signal():
    """Test ingestion of normal coherent signals."""
    prism = PrismProtocol()
    
    # Test with string
    result = prism.ingest("Hello World")
    assert isinstance(result, PrismResult)
    assert result.core_truth == "Hello World"
    assert result.is_coherent == True
    assert result.entropy_wrapper is None
    
    # Test with integer
    result = prism.ingest(42)
    assert result.core_truth == 42
    assert result.is_coherent == True
    
    # Test with dict
    test_dict = {"key": "value"}
    result = prism.ingest(test_dict)
    assert result.core_truth == test_dict
    assert result.is_coherent == True


def test_ingest_exception_signal():
    """Test ingestion of exception signals (entropy)."""
    prism = PrismProtocol()
    
    try:
        raise ValueError("Test error message")
    except Exception as e:
        result = prism.ingest(e)
        
        assert isinstance(result, PrismResult)
        assert result.is_coherent == False
        assert result.entropy_wrapper is not None
        assert "ValueError" in result.entropy_wrapper["type"]
        assert "Test error message" in result.entropy_wrapper["payload"]
        assert result.entropy_wrapper["context"] == "EntropyDetected"
        
        # Check core truth extraction
        assert result.core_truth is not None
        assert "ValueError" in result.core_truth["error_type"]
        assert "Test error message" in result.core_truth["error_message"]


def test_ingest_string_error():
    """Test ingestion of error-like strings."""
    prism = PrismProtocol()
    
    result = prism.ingest("This is an error message")
    assert result.is_coherent == False
    assert result.entropy_wrapper is not None
    assert "StringError" in result.entropy_wrapper["type"]


def test_ingest_empty_signal():
    """Test ingestion of empty/None signals."""
    prism = PrismProtocol()
    
    # Test None
    result = prism.ingest(None)
    assert result.is_coherent == False
    assert result.entropy_wrapper is not None
    assert "EmptySignal" in result.entropy_wrapper["type"]
    
    # Test empty string
    result = prism.ingest("")
    assert result.is_coherent == False
    assert result.entropy_wrapper is not None
    
    # Test empty list
    result = prism.ingest([])
    assert result.is_coherent == False
    assert result.entropy_wrapper is not None


def test_signal_class():
    """Test Signal dataclass."""
    signal = Signal(raw_payload="test", source="test_source", timestamp=123.45)
    
    assert signal.raw_payload == "test"
    assert signal.source == "test_source"
    assert signal.timestamp == 123.45
    
    # Test default values
    signal2 = Signal(raw_payload="test2")
    assert signal2.source is None
    assert signal2.timestamp is None


def test_prism_result_class():
    """Test PrismResult dataclass."""
    result = PrismResult(
        core_truth="test_truth",
        entropy_wrapper={"type": "test"},
        is_coherent=False
    )
    
    assert result.core_truth == "test_truth"
    assert result.entropy_wrapper == {"type": "test"}
    assert result.is_coherent == False
    
    # Test default values
    result2 = PrismResult(core_truth="truth2")
    assert result2.entropy_wrapper is None
    assert result2.is_coherent == True


def test_integrate_method():
    """Test the integrate method."""
    prism = PrismProtocol()
    
    # Test integration of coherent result
    coherent_result = PrismResult(core_truth="good data")
    assert prism.integrate(coherent_result) == True
    
    # Test integration of entropy result
    entropy_result = PrismResult(
        core_truth=None,
        entropy_wrapper={"type": "test_entropy"},
        is_coherent=False
    )
    assert prism.integrate(entropy_result) == False
    
    # Test integration of result with both truth and entropy
    mixed_result = PrismResult(
        core_truth="extracted truth",
        entropy_wrapper={"type": "mixed_entropy"},
        is_coherent=False
    )
    assert prism.integrate(mixed_result) == True


def test_prism_with_signal_object():
    """Test prism with explicit Signal objects."""
    prism = PrismProtocol()
    
    # Test with Signal object
    signal = Signal(raw_payload="explicit signal", source="test")
    result = prism.ingest(signal)
    
    assert result.core_truth == "explicit signal"
    assert result.is_coherent == True


def test_prism_internal_error():
    """Test prism handling of internal errors."""
    prism = PrismProtocol()
    
    # Create a signal that might cause issues during processing
    # The prism should handle this gracefully
    result = prism.ingest({"problematic": object()})
    
    # Should still return a PrismResult, even if it's not coherent
    assert isinstance(result, PrismResult)


def test_core_truth_extraction():
    """Test the core truth extraction logic."""
    prism = PrismProtocol()
    
    # Test with different types of exceptions
    exceptions_to_test = [
        ValueError("Value error"),
        RuntimeError("Runtime error"),
        KeyError("Key error"),
        Exception("Generic exception")
    ]
    
    for exc in exceptions_to_test:
        result = prism.ingest(exc)
        assert result.core_truth is not None
        assert "error_type" in result.core_truth
        assert "error_message" in result.core_truth
        assert "diagnostic" in result.core_truth


def test_entropy_types():
    """Test different entropy type detection."""
    prism = PrismProtocol()
    
    # Test Exception entropy
    try:
        raise TypeError("Type error")
    except Exception as e:
        result = prism.ingest(e)
        assert "Exception" in result.entropy_wrapper["type"]
    
    # Test StringError entropy
    result = prism.ingest("This contains error")
    assert "StringError" in result.entropy_wrapper["type"]
    
    # Test EmptySignal entropy
    result = prism.ingest(None)
    assert "EmptySignal" in result.entropy_wrapper["type"]


if __name__ == "__main__":
    # Run tests
    test_prism_protocol_initialization()
    test_ingest_normal_signal()
    test_ingest_exception_signal()
    test_ingest_string_error()
    test_ingest_empty_signal()
    test_signal_class()
    test_prism_result_class()
    test_integrate_method()
    test_prism_with_signal_object()
    test_prism_internal_error()
    test_core_truth_extraction()
    test_entropy_types()
    
    print("All tests passed!")