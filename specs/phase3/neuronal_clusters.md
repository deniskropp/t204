# Neuronal Clusters: Collaborative Mesh Topology

**Version:** 1.0
**Layer:** Collaborative (Network)
**Type:** Architectural Pattern

## 1. Concept
Traditional systems use **Hierarchy** (Server-Client, Master-Slave).
OCS Phase 3 uses **Neuronal Clusters** (Mesh, Peer-to-Peer, Holographic).
Structure mirrors a biological neural network:
- No central "brain" node.
- Knowledge is holographic (distributed across the whole).
- Triggering one node activates the cluster.

## 2. Topological Rules

1.  **Equipotency:** Every node (Agent/Interface) has the potential to access the full system context (`The Field`).
2.  **Instantaneous Propagation:** State changes in one node are broadcast to all relevant neighbors immediately.
3.  **Specialization by Focus, Not Rank:** Nodes differ by *what they become* (Role), not *who they are* (Permission). A "Scribe" node has Scribe tools, but can access "Builder" data if focus shifts.

## 3. Interaction Protocol (The Synapse)

### A. The Signal (Firing)
When a node achieves a "Realization" (Task Completion, New Insight, Error Resolution):
- It emits a `Pulse` (Signal).
- The Pulse contains: `{Payload, Vector, Intensity}`.

### B. The Receptor (Listening)
All nodes subscribe to the `PulseBus`.
- **Resonance Check:** Does this Pulse concern me?
- **Integration:** If yes, update local state.
- **Amplification:** If high value, re-broadcast to adjacent clusters.

## 4. Implementation Strategy

### Klipper SDK Context
- **Nodes:** Individual Klipper Plugins or External Apps.
- **Bus:** D-Bus Session / Signal-Slot mechanism.
- **Shared Memory:** The Clipboard History serves as the "Short-Term Memory" of the cluster.
- **Long-Term Memory:** The File System / Knowledge Base.

### Code Metaphor
```python
class Node:
    def on_pulse_received(self, pulse: Pulse):
        if self.is_resonant(pulse):
            self.internal_state.integrate(pulse.payload)
            self.emit_feedback_loop()
```

## 5. Governance
"Governance" is emergent. The path of least resistance (highest coherence) becomes the main trunk. There is no forced routing.
