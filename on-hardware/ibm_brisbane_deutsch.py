# This script demonstrates the Deutsch algorithm using Qiskit 2.1 and
# qiskit-ibm-runtime 0.41.1.
# It checks if a single-qubit boolean function is constant or balanced.

import numpy as np

# Import necessary components from Qiskit and Qiskit IBM Runtime
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
from qiskit.quantum_info import SparsePauliOp

def build_oracle(qc, oracle_qubit, helper_qubit, secret_bit):
    """
    Constructs the oracle for the Deutsch algorithm.

    Args:
        qc (QuantumCircuit): The quantum circuit to build the oracle on.
        oracle_qubit (QuantumRegister): The input qubit.
        helper_qubit (QuantumRegister): The helper qubit.
        secret_bit (int): The hidden bit (0 or 1) that defines the function.
                          If 0, the function is f(x) = 0.
                          If 1, the function is f(x) = x.
    """
    if secret_bit == 1:
        # f(x) = x, which is a balanced function.
        # This is implemented with a CNOT gate.
        qc.cx(oracle_qubit, helper_qubit)
    else:
        # f(x) = 0, which is a constant function.
        # This is implemented with an identity gate, as we do nothing.
        qc.id(oracle_qubit)


def deutsch_algorithm(secret_bit):
    """
    Runs the Deutsch algorithm for a given secret bit.
    
    Args:
        secret_bit (int): The bit (0 or 1) that defines the function f(x).
                          This function can be constant (f(0)=0, f(1)=0) or
                          balanced (f(0)=0, f(1)=1).
    Returns:
        QuantumCircuit: The complete Deutsch circuit.
    """
    # Create quantum and classical registers
    qr = QuantumRegister(2)
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qr, cr)

    # State preparation: put the helper qubit in the |-> state
    # and the oracle qubit in the |+> state.
    qc.x(qr[1])
    qc.h(qr)

    # Apply the oracle to the qubits
    build_oracle(qc, qr[0], qr[1], secret_bit)

    # Apply Hadamard gate to the oracle qubit
    qc.h(qr[0])

    # Measure the oracle qubit
    qc.measure(qr[0], cr[0])
    
    # We un-compute the helper qubit's transformation for cleaner visualization
    qc.h(qr[1])
    qc.z(qr[1])
    
    return qc

# Create a quantum circuit for a constant function (secret_bit=0)
constant_circuit = deutsch_algorithm(secret_bit=0)

# Create a quantum circuit for a balanced function (secret_bit=1)
balanced_circuit = deutsch_algorithm(secret_bit=1)

# You can print the circuits to see their structure
print("Constant Function Circuit:")
print(constant_circuit)
print("\nBalanced Function Circuit:")
print(balanced_circuit)

# --- Qiskit IBM Runtime integration starts here ---
# Note: You need an IBM Quantum account and a saved API token/instance
# in order for this to work.

# Initialize the QiskitRuntimeService
# This loads your saved credentials from disk.
# service = QiskitRuntimeService(channel="ibm_cloud", token="MY_API_KEY", region="us-east")
service = QiskitRuntimeService()

# Select a backend. Here, we use a simulator. You can replace this
# with a real quantum device if you have access to it.
backend = service.least_busy(simulator=False, operational=True)

# Define the circuits to be run.
circuits_to_run = [constant_circuit, balanced_circuit]

# Transpile the circuits for the specific backend. This step is crucial.
transpiled_circuits = transpile(circuits_to_run, backend=backend, optimization_level=3)
    
# Using EstimatorV2 to get the expectation value of the measurement result.
# The backend must now be passed as the `mode` argument.
print(f"\nRunning job on the backend: {backend.name}...")
try:
    # Instantiate the EstimatorV2 primitive with the backend specified as the mode.
    estimator = EstimatorV2(mode=backend)
    
    # The observable must have the same number of qubits as the circuit.
    # We create a SparsePauliOp that explicitly acts on the first qubit (qubit 0).
    obs_z = SparsePauliOp("ZI")
    
    # Transpiled circuits can change the qubit layout.
    # We must apply the transpiled circuit's layout to the observable to align them.
    transpiled_obs_z = obs_z.apply_layout(layout=transpiled_circuits[0].layout)
    
    # Run the transpiled circuits on the backend using the primitive
    # The EstimatorV2 primitive requires `pubs`, which is a list of tuples
    # where each tuple is `(circuit, observables)`.
    pubs = [(transpiled_circuits[0], transpiled_obs_z), (transpiled_circuits[1], transpiled_obs_z)]
    job = estimator.run(pubs=pubs)
    
    # Get the job result
    result = job.result()
    
    # The result object contains the expectation values for each pub.
    print("\n--- Results ---")
    
    # The result is now an object with a .data attribute.
    # The .data.evs attribute contains the expectation values.
    constant_ev = result[0].data.evs
    balanced_ev = result[1].data.evs
    
    print(f"Constant function expectation value: {constant_ev}")
    print(f"Balanced function expectation value: {balanced_ev}")
    
    print("\n--- Analysis ---")
    # For a constant function, the expectation value should be close to 1.
    if np.isclose(constant_ev, 1.0):
        print("Analysis for Constant Function: The expectation value is close to 1, which correctly indicates a constant function.")
    else:
        print("Analysis for Constant Function: The expectation value is close to -1, which is unexpected for a constant function.")
    
    # For a balanced function, the expectation value should be close to -1.
    if np.isclose(balanced_ev, -1.0):
        print("Analysis for Balanced Function: The expectation value is close to -1, which correctly indicates a balanced function.")
    else:
        print("Analysis for Balanced Function: The expectation value is close to 1, which is unexpected for a balanced function.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure you have configured your IBM Quantum account using `QiskitRuntimeService.save_account()`.")
    



# --- Example Output ---
# Running job on the backend: ibm_brisbane...

# --- Results ---
# Constant function expectation value: -0.9954604813133512
# Balanced function expectation value: 0.9984453703127915

# --- Analysis ---
# Analysis for Constant Function: The expectation value is close to -1, which is unexpected for a constant function.
# Analysis for Balanced Function: The expectation value is close to 1, which is unexpected for a balanced function.
