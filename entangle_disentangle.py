"""
Entangling and Un-entangling Qubits using Qiskit 2.1 with AerSimulator

This script demonstrates:
1. How to create entangled Bell states (entanglement)
2. How to un-entangle (disentangle) qubits using the inverse operations
3. Verification by measuring the quantum states

The key insight: To un-entangle qubits, apply the inverse operations
in reverse order of the entanglement process.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

def create_entangled_circuit():
    """Create a circuit that entangles 2 qubits into a Bell state."""
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qr, cr, name="Entanglement")
    
    # Step 1: Apply Hadamard to first qubit
    circuit.h(qr[0])
    
    # Step 2: Apply CNOT gate (control=q0, target=q1) to entangle
    circuit.cx(qr[0], qr[1])
    
    # Measure both qubits
    circuit.measure(qr, cr)
    
    return circuit

def create_disentangled_circuit():
    """Create a circuit that entangles and then un-entangles 2 qubits."""
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qr, cr, name="Entangle + Disentangle")
    
    # === ENTANGLEMENT PHASE ===
    # Step 1: Apply Hadamard to first qubit
    circuit.h(qr[0])
    
    # Step 2: Apply CNOT gate to entangle
    circuit.cx(qr[0], qr[1])
    
    # === UN-ENTANGLEMENT PHASE (Inverse operations in reverse order) ===
    # Step 3: Apply inverse CNOT (CNOT is self-inverse)
    circuit.cx(qr[0], qr[1])
    
    # Step 4: Apply inverse Hadamard (Hadamard is self-inverse)
    circuit.h(qr[0])
    
    # After these operations, the qubits should be in |00> state
    # Measure both qubits
    circuit.measure(qr, cr)
    
    return circuit

def run_simulation(circuit, shots=1000):
    """Run the circuit on AerSimulator and return measurement counts."""
    simulator = AerSimulator()
    result = simulator.run(circuit, shots=shots).result()
    counts = result.get_counts(circuit)
    return counts

def display_results(circuit_name, counts):
    """Display measurement results in a formatted way."""
    print(f"\n{circuit_name}")
    print("=" * 50)
    for state in sorted(counts.keys()):
        count = counts[state]
        percentage = (count / sum(counts.values())) * 100
        print(f"|{state}>: {count:4d} ({percentage:5.1f}%)")

def main():
    print("QUANTUM ENTANGLEMENT AND DISENTANGLEMENT DEMONSTRATION")
    print("=" * 70)
    
    # === Test 1: Entanglement Only ===
    print("\n[TEST 1] ENTANGLEMENT ONLY")
    print("-" * 70)
    entangled_circuit = create_entangled_circuit()
    print("\nCircuit:")
    print(entangled_circuit)
    
    entangled_counts = run_simulation(entangled_circuit)
    display_results("Measurement Results (Should see |00> and |11> only):", entangled_counts)
    
    print("\nInterpretation:")
    print("✓ Only |00> and |11> states appear (roughly 50% each)")
    print("✓ The qubits are ENTANGLED - measuring one determines the other")
    
    # === Test 2: Entanglement + Disentanglement ===
    print("\n" + "=" * 70)
    print("[TEST 2] ENTANGLEMENT + DISENTANGLEMENT")
    print("-" * 70)
    disentangled_circuit = create_disentangled_circuit()
    print("\nCircuit:")
    print(disentangled_circuit)
    
    disentangled_counts = run_simulation(disentangled_circuit)
    display_results("Measurement Results (Should see only |00>):", disentangled_counts)
    
    print("\nInterpretation:")
    print("✓ Only |00> state appears (100%)")
    print("✓ The qubits are UN-ENTANGLED - both are in known state |0>")
    
    # === Summary ===
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
HOW TO UN-ENTANGLE QUBITS:
-------------------------
1. Identify the entanglement gates used:
   - In Bell state creation: Hadamard (H) on q0, CNOT(q0, q1)

2. Apply inverse operations in REVERSE order:
   - CNOT†(q0, q1) = CNOT(q0, q1)  [CNOT is self-inverse]
   - H†(q0) = H(q0)                 [Hadamard is self-inverse]

3. Result: Qubits return to |00> (fully disentangled)

KEY CONCEPTS:
-------------
• Entanglement: Creates correlated qubits where measuring one 
  instantly determines the other's state
  
• Disentanglement: Applies inverse operations to restore qubits 
  to independent, separable states
  
• Self-Inverse Gates: Both H and CNOT are their own inverses
  (H† = H, CNOT† = CNOT)
  
• Order Matters: Must apply inverse operations in reverse order 
  of entanglement to properly disentangle
""")

if __name__ == "__main__":
    main()
