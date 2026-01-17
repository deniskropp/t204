import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple

# Logger
logger = logging.getLogger(__name__)

# --- PRISM OF COHERENCE ---

@dataclass
class PrismResult:
    """Outcome of a Prism refraction."""
    core_truth: Any
    entropy_wrapper: Optional[Dict[str, Any]] = None
    is_coherent: bool = True

@dataclass
class Signal:
    """Represents a raw input signal to the PRISM_OF_COHERENCE protocol."""
    raw_payload: Any
    source: Optional[str] = None
    timestamp: Optional[float] = None

class PrismProtocol:
    """
    Implements the PRISM_OF_COHERENCE protocol (v1.0).
    
    A cognitive sorting and transmutation algorithm designed to handle "Shadow Data"
    (entropic inputs, fear, control mechanisms, high-friction systemic feedback)
    within the OCS framework.
    
    Operates at Integrity Layer 5D (Cognitive/Orchestrative).
    
    Principle: "The Shadow is not the enemy. It is the Diagnose-Mechanism for missing integrity."
    """
    
    def ingest(self, signal: Any) -> PrismResult:
        """
        Stage 1: Ingestion (The Open Port)
        
        Accepts the input signal fully without blocking.
        Metaphor: "Opening the door to the phantom."
        
        Args:
            signal: Raw input signal (can be Exception, data, or any object)
            
        Returns:
            PrismResult containing the processed signal
        """
        try:
            # Convert to Signal object if not already
            if not isinstance(signal, Signal):
                signal = Signal(raw_payload=signal)
            
            logger.debug(f"Prism Ingestion: {type(signal.raw_payload).__name__}")
            return self._refract(signal)
        except Exception as e:
            # Even the failure of the Prism is data
            return PrismResult(
                core_truth=None,
                entropy_wrapper={
                    "error": str(e),
                    "origin": "PrismInternal",
                    "stage": "ingestion"
                },
                is_coherent=False
            )

    def _refract(self, signal: Signal) -> PrismResult:
        """
        Stage 2: Refraction (The Prism)
        
        Decomposes the signal into its components: Information vs. Intent.
        Question: "What is the core data, and what is the fear packaging?"
        
        Args:
            signal: Signal object containing raw payload
            
        Returns:
            PrismResult with separated core truth and entropy wrapper
        """
        payload = signal.raw_payload
        
        # Handle Exception signals (high entropy)
        if isinstance(payload, Exception):
            return self._process_entropy(payload, "Exception")
        
        # Handle error-like signals
        if isinstance(payload, str) and ("error" in payload.lower() or "exception" in payload.lower()):
            return self._process_entropy(payload, "StringError")
        
        # Handle None or empty signals
        if payload is None or (isinstance(payload, (str, list, dict)) and not payload):
            return self._process_entropy(payload, "EmptySignal")
        
        # Default: Treat as coherent signal
        return PrismResult(core_truth=payload)
    
    def _process_entropy(self, entropy_payload: Any, entropy_type: str) -> PrismResult:
        """
        Processes entropic signals and extracts diagnostic information.
        
        Args:
            entropy_payload: The entropic content
            entropy_type: Type of entropy detected
            
        Returns:
            PrismResult with entropy wrapper and potential core truth
        """
        entropy_wrapper = {
            "type": entropy_type,
            "payload": str(entropy_payload) if not isinstance(entropy_payload, dict) else entropy_payload,
            "context": "EntropyDetected",
            "diagnostic": "Shadow data requiring integration"
        }
        
        # Attempt to extract core truth from entropy
        core_truth = self._extract_factual_basis(entropy_payload)
        
        return PrismResult(
            core_truth=core_truth,
            entropy_wrapper=entropy_wrapper,
            is_coherent=False
        )
    
    def _extract_factual_basis(self, data: Any) -> Optional[Any]:
        """
        Attempts to extract factual basis from entropic data.
        
        Args:
            data: The entropic data to analyze
            
        Returns:
            Extracted core truth if possible, None otherwise
        """
        try:
            if isinstance(data, Exception):
                # Extract meaningful information from exceptions
                return {
                    "error_type": type(data).__name__,
                    "error_message": str(data),
                    "diagnostic": "System integrity check required"
                }
            elif isinstance(data, str):
                # Extract keywords or meaningful content from error strings
                return {
                    "message": data,
                    "diagnostic": "Textual entropy detected"
                }
            elif isinstance(data, dict):
                # Return the dict as potential structured information
                return data
            else:
                # For other types, return type information
                return {
                    "type": type(data).__name__,
                    "diagnostic": "Non-textual entropy"
                }
        except Exception:
            return None

    def integrate(self, prism_result: PrismResult) -> bool:
        """
        Stage 3: Transmutation (The Alchemy)
        
        Discards the EntropyWrapper (acknowledges it, then nullifies its weight).
        Integrates the CoreTruth into the system model.
        
        Args:
            prism_result: Result from the refraction process
            
        Returns:
            True if integration successful, False otherwise
        """
        # Acknowledge entropy (diagnostic logging)
        if prism_result.entropy_wrapper:
            logger.info(f"Prism Integration: Acknowledging entropy - {prism_result.entropy_wrapper['type']}")
            # Entropy dissipates upon acknowledgment
        
        # Integrate core truth
        if prism_result.core_truth is not None:
            logger.debug(f"Prism Integration: Integrating core truth - {type(prism_result.core_truth).__name__}")
            # In a real system, this would update the system model
            # For now, we just log and return success
            return True
        
        return False


# --- NEURONAL CLUSTERS ---

@dataclass
class Pulse:
    """A signal emitted by a node in the cluster."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payload: Any = None
    vector: str = "broadcast"  # targeted or broadcast
    intensity: float = 1.0     # Importance (0.0 - 1.0)
    source_node: str = "local"

class PulseListener(Protocol):
    def on_pulse(self, pulse: Pulse):
        ...

class NeuronalCluster:
    """
    Manages the P2P mesh topology.
    Currently implements a local Observer pattern as V1 of the Cluster.
    Future V2: D-Bus Signal bridging.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.listeners: List[PulseListener] = []

    def subscribe(self, listener: PulseListener):
        """Adds a listener to the synaptic gap."""
        self.listeners.append(listener)

    def emit(self, payload: Any, vector: str = "broadcast", intensity: float = 1.0):
        """Fires a Pulse into the cluster."""
        pulse = Pulse(
            payload=payload,
            vector=vector,
            intensity=intensity,
            source_node=self.node_id
        )
        self._propagate(pulse)

    def _propagate(self, pulse: Pulse):
        """Internal propagation loop."""
        for listener in self.listeners:
            try:
                listener.on_pulse(pulse)
            except Exception as e:
                logger.error(f"Synapse failure in listener {listener}: {e}")
