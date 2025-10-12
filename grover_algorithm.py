import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import GroverOperator

# --- 1. Problem Definition ---
NUM_QUBITS = 4 # n
N = 2**NUM_QUBITS # Total search space size
MARKED_STATE = "1101" # The target state (e.g., in binary string format)
NUM_SOLUTIONS = 1 # M (Number of marked solutions)

# --- 2. Calculate Optimal Iterations ---
def calculate_optimal_iterations(N, M):
    """Calculates the optimal number of Grover iterations (R)."""
    if M > N:
        return 0
    # The angle of rotation per iteration, theta, is defined by sin(theta) = sqrt(M/N).
    # The optimal number of iterations R is approximately floor(pi / (4 * theta)).
    theta = np.arcsin(np.sqrt(M / N))
    R_approx = np.pi / (4 * theta)
    # Use floor to maximize the success probability, as per the standard analysis.
    return math.floor(R_approx)

OPTIMAL_ITERATIONS = calculate_optimal_iterations(N, NUM_SOLUTIONS)
print(f"Search space size (N): {N}")
print(f"Marked state (w): |{MARKED_STATE}⟩")
print(f"Optimal iterations (R): {OPTIMAL_ITERATIONS}\n")


# --- 3. Custom Phase Oracle Construction ---
def create_oracle(marked_state: str) -> QuantumCircuit:
    """
    Creates a phase oracle that flips the phase of the marked_state.
    
    The marked_state is marked by applying X gates to flip the '0' bits
    to '1's, then applying a multi-controlled Z (MCZ) gate, and finally
    applying X gates to restore the unmarked qubits.
    """
    n = len(marked_state)
    oracle = QuantumCircuit(n, name="Oracle")
    
    # Apply X-gates where the target state has a '0'
    # Qiskit uses little-endian, so qubit 0 is the rightmost bit (least significant)
    for i, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            oracle.x(i)

    # Since Qiskit provides MultiControlGate classes, let's define the MCX
    # and sandwich it with H and X for the phase flip.
    
    # 1. Define control qubits (all of them)
    control_qubits = list(range(n))
    
    # 2. To implement MCZ on all qubits, we apply MCX,
    #    with the last qubit as target, sandwiched by H gates.
    oracle.h(n - 1)
    # Apply Multi-Controlled X (MCX) gate
    # Controls: 0 to n-2
    # Target: n-1
    oracle.mcx(control_qubits[:-1], n - 1)
    oracle.h(n - 1)

    # Apply X-gates where the target state had a '0' to uncompute
    for i, bit in enumerate(reversed(marked_state)):
        if bit == '0':
            oracle.x(i)
            
    oracle.barrier()
    return oracle

# Create the specific oracle for |1101⟩
oracle_qc = create_oracle(MARKED_STATE)

# --- 4. Build the Grover Circuit ---

# Initialize the main circuit
grover_circuit = QuantumCircuit(NUM_QUBITS, NUM_QUBITS)

# 1. Initialization (Uniform Superposition)
grover_circuit.h(range(NUM_QUBITS))
grover_circuit.barrier()

# 2. Apply the Grover Operator (R times)
# The Grover Operator (Q) is D * Sf (Diffusion * Oracle)
# We can use the built-in GroverOperator class for the diffusion part,
# feeding it our custom oracle.

grover_op = GroverOperator(oracle=oracle_qc, insert_barriers=True)

# Apply the Grover iteration R times
for _ in range(OPTIMAL_ITERATIONS):
    grover_circuit.compose(grover_op, inplace=True)
    grover_circuit.barrier()

# 3. Measurement
grover_circuit.measure(range(NUM_QUBITS), range(NUM_QUBITS))

# Draw the circuit (optional, but helpful for visualization)
# print(grover_circuit.draw(output='text', fold=-1))

# --- 5. Simulation and Results ---
def simulate_grover(circuit: QuantumCircuit, shots=1024):
    """Simulates the Grover circuit and returns the measurement counts."""
    # Use AerSimulator for simulating the circuit
    simulator = AerSimulator()
    
    # Execute the circuit and get the result
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    result = job.result()
    
    # Get the counts from the result
    counts = result.get_counts(circuit)    
    return counts

# Run the simulation
final_counts = simulate_grover(grover_circuit, shots=8192)

# --- 6. Analysis and Visualization ---

print("--- Simulation Results (8192 shots) ---")
# Get the top 5 results
top_results = list(final_counts.items())[:5]
for bitstring, count in top_results:
    is_solution = " (Solution)" if bitstring == MARKED_STATE else ""
    # Convert count back to percentage for clearer view
    percentage = (count / 8192) * 100
    print(f"Outcome |{bitstring}⟩: {int(count)} counts ({percentage:.2f}%) {is_solution}")

# The result is the raw counts from the sampling, which we format as a histogram plot.
print("\nSuccess probability focused on the marked state:")
marked_state_count = final_counts.get(MARKED_STATE, 0)
print(f"|{MARKED_STATE}⟩ probability: {(marked_state_count/8192) * 100:.2f}%")