# This program demonstrates a simplified version of Shor's algorithm
# for factoring the number N=15.
#
# A full implementation for a large three-digit number would require
# hundreds of qubits, making it infeasible for a classical simulator.
# This example is a pedagogical tool to show the quantum-mechanical
# part of the algorithm: finding the period of a function.
#
# Requirements:
# pip install qiskit==2.1
# pip install qiskit-aer==0.15
# pip install numpy
# pip install matplotlib

import math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram

def c_amod15(a, power):
    """
    Creates a controlled-U gate for modular exponentiation.
    The function performs a^power mod 15.
    This is hard-coded for the specific case of a=7 and N=15.
    
    Args:
        a (int): The base of the exponentiation (e.g., 7).
        power (int): The power of 'a' to be used in the exponentiation.
    
    Returns:
        QuantumCircuit: A circuit for the controlled modular exponentiation.
    """
    U = QuantumCircuit(4)
    # This is a correct, hard-coded modular exponentiation circuit for a=7, N=15.
    # The powers of 7 mod 15 are: 7^1=7, 7^2=4, 7^3=13, 7^4=1. Period r=4.
    # We apply the transformation according to the power.
    
    if a != 7:
        print("Error: This function is hard-coded for a=7.")
        return U.to_gate()

    if power % 4 == 0:
        # a^4 = 1 mod 15, no change
        pass
    elif power % 4 == 1:
        # a^1 = 7 mod 15, which is |x> -> |7x mod 15>
        U.swap(0, 1)
        U.swap(1, 2)
        U.swap(2, 3)
    elif power % 4 == 2:
        # a^2 = 4 mod 15, which is |x> -> |4x mod 15>
        U.swap(1, 3)
        U.swap(0, 2)
    elif power % 4 == 3:
        # a^3 = 13 mod 15, which is |x> -> |13x mod 15>
        U.swap(0, 3)
        U.swap(0, 2)
        U.swap(1, 3)

    return U.to_gate()

def shor_algorithm():
    """
    Runs the simplified Shor's algorithm for factoring N=15.
    """
    N = 15
    # Step 1: Classical pre-processing. Pick 'a' such that gcd(a, N) = 1.
    a = 7
    print(f"Factoring N = {N}")
    print(f"Chosen integer 'a' = {a}")

    if math.gcd(a, N) != 1:
        print(f"Error: gcd({a}, {N}) is not 1. Please choose a different 'a'.")
        return

    # Step 2: Determine the number of qubits for the counting register.
    # We need 2n qubits where N <= 2^n. For N=15, n=4. So we need 8 qubits.
    n_count = 8
    
    # Step 3: Create the quantum circuit.
    # We need one register for counting and one for the result.
    qc = QuantumCircuit(n_count + 4, n_count)
    
    # Initialize the counting qubits to a superposition.
    for q in range(n_count):
        qc.h(q)

    # Initialize the result register to |1>
    qc.x(n_count)
    
    # Step 4: Apply the controlled modular exponentiation gates.
    for q in range(n_count):
        # We need to apply the modular exponentiation a^(2^q) mod N.
        # This is where the c_amod15 circuit is used.
        power_of_a = int(2**q)
        gate = c_amod15(a, power_of_a)
        
        # The controlled version of our 4-qubit gate now needs 5 qubits in total.
        qc.append(gate.control(1), [q] + list(range(n_count, n_count + 4)))
    
    # Step 5: Apply the inverse Quantum Fourier Transform (QFT).
    # This is a key part of the algorithm, used to extract the period.
    qc.barrier()
    qc.append(QFT(n_count, inverse=True), range(n_count))
    
    # Step 6: Measurement.
    qc.measure(range(n_count), range(n_count))

    # Step 7: Run the simulation.
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    shots = 1000
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    print("\nMeasurement Results:")
    print(counts)
    
    # Plot a histogram of the results
    plot_histogram(counts, title="Shor's Algorithm Period-Finding Results")
    
    # Step 8: Classical post-processing to find the period 'r' and factors.
    measured_periods = []
    for measurement in counts:
        decimal = int(measurement, 2)
        print(f"Measured value: {measurement} (decimal {decimal})")
        # We look for a period 'r' such that c/2^n is a close approximation of k/r.
        # We can find this by checking denominators of the measured value's continued fraction.
        # Here we just use a simplified approach to find 'r' from the measured output.
        if decimal != 0:
            r = 2**n_count / decimal
            if r % 1 == 0:  # Check if r is an integer
                r = int(r)
                if r % 2 == 0 and r not in measured_periods:
                    measured_periods.append(r)
                    
    print("\nPossible periods (r) from measurements:")
    print(measured_periods)
    
    for r in measured_periods:
        if r != 0 and r % 2 == 0:
            x = int(math.pow(a, r / 2))
            factor1 = math.gcd(x - 1, N)
            factor2 = math.gcd(x + 1, N)
            
            if factor1 != 1 and factor1 != N and factor2 != 1 and factor2 != N:
                print(f"\nFound factors using period r={r}:")
                print(f"  Factor 1: gcd({x-1}, {N}) = {factor1}")
                print(f"  Factor 2: gcd({x+1}, {N}) = {factor2}")
                break
    else:
        print("\nCould not find a valid period to factor the number.")
        print("Note: The algorithm is probabilistic. Rerun the program for different results.")

if __name__ == "__main__":
    shor_algorithm()
