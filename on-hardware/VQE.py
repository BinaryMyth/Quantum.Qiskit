from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.circuit.library import EfficientSU2
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
from scipy.optimize import minimize
import numpy as np

# 1. Define the Hamiltonian (The Map) 🗺️
# Let's imagine a 100-qubit chain where each qubit interacts with its neighbor
num_qubits = 100
interactions = [("ZZ", [i, i+1], 1.0) for i in range(num_qubits - 1)]
hamiltonian = SparsePauliOp.from_sparse_list(interactions, num_qubits=num_qubits)

# 2. Define the Ansatz (The Knobs) 🎡
# EfficientSU2 creates a hardware-efficient pattern of rotations and entanglers
ansatz = EfficientSU2(num_qubits, entanglement='linear', reps=1)

# 3. Define the Cost Function (The Altitude Measurement) 📏
def cost_func(params, transpiled_ansatz, transpiled_hamiltonian, estimator):
    # This function is what the classical optimizer "calls"
    # Now use these in your PUB
    pub = (transpiled_ansatz, transpiled_hamiltonian, params)
    job = estimator.run([pub])
    pub_result = job.result()[0]
    return pub_result.data.evs

# 4. The Optimization Loop (The Driver) 🏎️
# In a real run, you would initialize an IBM Runtime Estimator here

service = QiskitRuntimeService()
 
backend = service.least_busy(simulator=False, operational=True)

# 1. Create a Pass Manager for the specific backend
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

# 2. Transpile the Ansatz (the circuit)
transpiled_ansatz = pm.run(ansatz)

# 3. Transform the Hamiltonian (the observable) 
# It must match the layout of the transpiled circuit
transpiled_hamiltonian = hamiltonian.apply_layout(transpiled_ansatz.layout)

estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 1000

initial_params = np.random.rand(ansatz.num_parameters)

# We use a classical optimizer (COBYLA) to find the minimum energy
result = minimize(cost_func, initial_params, args=(transpiled_ansatz, transpiled_hamiltonian, estimator), method='COBYLA')

print(f"Final Estimated Ground State Energy: {result.fun}")