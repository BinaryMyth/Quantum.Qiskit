from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def deutsch_algorithm(oracle):
    # Create a quantum circuit with 2 qubits and 1 classical bit
    qc = QuantumCircuit(2, 1)
    
    # Initialize qubits: |0> and |1>
    qc.x(1)
    qc.h([0, 1])
    
    # Apply the oracle
    qc.append(oracle, [0, 1])
    
    # Hadamard on the first qubit
    qc.h(0)
    
    # Measure the first qubit
    qc.measure(0, 0)
    
    # Initialize the AerSimulator
    simulator = AerSimulator()

    # Transpile the circuit for the simulator
    # This optimizes the circuit for the specific backend
    compiled_circuit = transpile(qc, simulator)

    # Execute the compiled circuit on the simulator
    # We'll run 1024 shots
    job = simulator.run(compiled_circuit, shots=1024)

    
    # Get the results from the job
    result = job.result()    
    
    # Get the measurement counts
    counts = result.get_counts(compiled_circuit)
    return counts

def create_oracle(type='constant'):
    """Returns a Deutsch oracle as a gate."""
    from qiskit.circuit import QuantumCircuit, Gate
    oracle = QuantumCircuit(2)
    if type == 'constant':
        # f(x) = 0, do nothing
        pass
    elif type == 'balanced':
        # f(x) = x, apply CNOT
        oracle.cx(0, 1)
    else:
        raise ValueError("type must be 'constant' or 'balanced'")
    return oracle.to_gate(label=f"{type.capitalize()} Oracle")

if __name__ == "__main__":
    for oracle_type in ['constant', 'balanced']:
        oracle = create_oracle(oracle_type)
        result = deutsch_algorithm(oracle)
        print(f"Oracle type: {oracle_type}, Result: {result}")