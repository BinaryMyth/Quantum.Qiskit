from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# --- Parameters ---
N = 3  # Number of qubits for input and output (total 2N qubits)
SECRET_STRING = "101" # The hidden period 's' (e.g., "101")
if len(SECRET_STRING) != N:
    raise ValueError(f"Secret string length must be {N}")


def make_simon_oracle(n, s):
    
    qc = QuantumCircuit(2 * n)
    s_list = [int(bit) for bit in s[::-1]] # LSB is at index 0

    # The oracle must implement two conditions:
    # 1. f is one-to-one on the set of inputs with a '0' in the LSB position (a simplification).
    # 2. f(x) = f(x XOR s)

    # Simplified Oracle for s="101" (N=3)
    # The oracle's output register (qubits n to 2n-1) is used for f(x).
    # We choose f(x) = x_0 for x_0=0 and f(x) = x_1 XOR x_2 for x_0=1
    # which satisfies the s="101" periodicity constraint.

    # 1. Start by copying the input register to the output register (CNOTs)
    # This ensures f(x) has a dependence on x.
    for i in range(n):
        qc.cx(i, i + n)

    # 2. Enforce the s-periodicity: f(x) = f(x XOR s)
    # This is done by adding CNOTs from input bits where s_i = 1 to ALL output bits.
    # For s="101": s_0=1 (qubit 0), s_1=0 (qubit 1), s_2=1 (qubit 2)
    # The CNOTs ensure that if x and x XOR s are input, they produce the same f(x).

    for i in range(n):
        if s_list[i] == 1:
            for j in range(n):
                qc.cx(i, j + n)

    return qc


def make_simon_circuit(n, oracle):
    """
    Creates the main Simon's algorithm circuit.
    """
    # 2n qubits total: n input (0 to n-1) and n output (n to 2n-1)
    qc = QuantumCircuit(2 * n, n)

    # 1. Apply Hadamard gates to the input register (0 to n-1)
    qc.h(range(n))
    qc.barrier()

    # 2. Apply the oracle O_f
    qc.append(oracle, range(2 * n))
    qc.barrier()

    # 3. Apply Hadamard gates to the input register again
    qc.h(range(n))
    qc.barrier()

    # 4. Measure the input register (0 to n-1)
    qc.measure(range(n), range(n))

    return qc

# --- Execution ---

# 1. Create the Oracle
oracle_instruction = make_simon_oracle(N, SECRET_STRING)

# 2. Create the Simon Circuit
simon_circuit = make_simon_circuit(N, oracle_instruction)

print("--- Simon's Circuit for s='101' ---")
print(simon_circuit.draw(fold=-1))

# 3. Execute the circuit on a simulator
print("\n--- Executing on Qiskit Sampler (Simulator) ---")
# Use AerSimulator for simulating the circuit
simulator = AerSimulator()

# Execute the circuit and get the result
compiled_circuit = transpile(simon_circuit, simulator)
job = simulator.run(compiled_circuit, shots=1024)
result = job.result()

# Get the counts from the result
counts = result.get_counts(simon_circuit)    

print("\n--- Measurement Results (y) ---")
print(counts)

# 4. Analysis
# The measured strings 'y' must satisfy the equation: y * s = 0 (mod 2)
# TODO: Implement classical post-processing to solve for 's' using the measured 'y' values.