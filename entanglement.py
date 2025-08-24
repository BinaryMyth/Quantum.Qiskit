from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Create quantum registers with 2 qubits
qr = QuantumRegister(2, 'q')
cr = ClassicalRegister(2, 'c')

# Create a quantum circuit with 2 qubits and 2 classical bits
circuit = QuantumCircuit(qr, cr)

# Create Bell state (entanglement)
circuit.h(qr[0])    # Apply Hadamard gate to the first qubit
# circuit.x(qr[1])    # Apply X gate to the second qubit to set it to |1>
circuit.cx(qr[0], qr[1])  # Apply CNOT gate with control qubit 0 and target qubit 1

# Measure both qubits
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

print("\nNote: If the qubits are truly entangled, you should only see measurements")
print("of |00> and |11> with roughly equal probability (~50% each).")
print("This demonstrates that measuring one qubit immediately determines")
print("the state of the other qubit, showing quantum entanglement.")
