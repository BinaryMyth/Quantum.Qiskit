from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Create quantum registers with 2 qubits
qr = QuantumRegister(2, 'q')
cr = ClassicalRegister(2, 'c')

circuit = QuantumCircuit(qr, cr)

circuit.x(qr[0])    # Apply X gate to the first qubit to set it to |1>
circuit.x(qr[1])    # Apply X gate to the second qubit to set it to |1>

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