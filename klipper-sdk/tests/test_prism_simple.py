#!/usr/bin/env python3
"""
Simple test for PRISM_OF_COHERENCE protocol implementation.
Tests the core protocol without importing the full klipper_sdk module.
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import just the bridge module directly
from klipper_sdk.bridge import PrismProtocol, PrismResult, Signal


def test_prism_protocol_basic():
    """Test basic prism protocol functionality."""
    print("Testing PRISM_OF_COHERENCE protocol implementation...")
    
    prism = PrismProtocol()
    assert prism is not None
    print("✓ PrismProtocol initialized")
    
    # Test 1: Normal signal
    result = prism.ingest("Hello World")
    assert isinstance(result, PrismResult)
    assert result.core_truth == "Hello World"
    assert result.is_coherent == True
    assert result.entropy_wrapper is None
    print("✓ Normal signal processing works")
    
    # Test 2: Exception signal
    try:
        raise ValueError("Test error message")
    except Exception as e:
        result = prism.ingest(e)
        assert isinstance(result, PrismResult)
        assert result.is_coherent == False
        assert result.entropy_wrapper is not None
        assert "ValueError" in result.entropy_wrapper["type"]
        assert "Test error message" in result.entropy_wrapper["payload"]
        print("✓ Exception signal processing works")
        
        # Test core truth extraction
        assert result.core_truth is not None
        assert "ValueError" in result.core_truth["error_type"]
        print("✓ Core truth extraction works")
    
    # Test 3: Empty signal
    result = prism.ingest(None)
    assert result.is_coherent == False
    assert result.entropy_wrapper is not None
    assert "EmptySignal" in result.entropy_wrapper["type"]
    print("✓ Empty signal processing works")
    
    # Test 4: Integration
    coherent_result = PrismResult(core_truth="good data")
    assert prism.integrate(coherent_result) == True
    print("✓ Integration of coherent result works")
    
    entropy_result = PrismResult(
        core_truth=None,
        entropy_wrapper={"type": "test_entropy"},
        is_coherent=False
    )
    assert prism.integrate(entropy_result) == False
    print("✓ Integration of entropy result works")
    
    print("\n🎉 All PRISM_OF_COHERENCE tests passed!")
    return True


def test_signal_class():
    """Test Signal dataclass."""
    signal = Signal(raw_payload="test", source="test_source", timestamp=123.45)
    assert signal.raw_payload == "test"
    assert signal.source == "test_source"
    assert signal.timestamp == 123.45
    print("✓ Signal class works correctly")


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
    print("✓ PrismResult class works correctly")


if __name__ == "__main__":
    try:
        test_signal_class()
        test_prism_result_class()
        test_prism_protocol_basic()
        print("\n🚀 PRISM_OF_COHERENCE implementation is working correctly!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)