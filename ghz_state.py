from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Create quantum registers with 3 qubits
qr = QuantumRegister(3, 'q')
cr = ClassicalRegister(3, 'c')

# Create a quantum circuit with 3 qubits and 3 classical bits
circuit = QuantumCircuit(qr, cr)

# Create GHZ state (|000⟩ + |111⟩)/√2
circuit.h(qr[0])    # Apply Hadamard gate to the first qubit
circuit.cx(qr[0], qr[1])  # CNOT between first and second qubit
circuit.cx(qr[1], qr[2])  # CNOT between second and third qubit

# Measure all qubits
circuit.measure(qr, cr)

# Print the circuit
print("Quantum Circuit:")
print(circuit)

# Create and run the simulator
simulator = AerSimulator()
result = simulator.run(circuit, shots=1000).result()

# Get the counts of measurement outcomes
counts = result.get_counts(circuit)

# Print the measurement results
print("\nMeasurement Results:")
for state, count in counts.items():
    print(f"|{state}>: {count}")

print("\nNote: In the GHZ state, you should only see measurements")
print("of |000> and |111> with roughly equal probability (~50% each).")
print("This demonstrates three-qubit entanglement where measuring")
print("any one qubit determines the state of all other qubits.")