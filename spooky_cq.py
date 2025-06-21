# 1. Import necessary classes from Qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# 2. Create a Quantum Circuit
# We need 2 qubits to entangle and 2 classical bits to store the measurement results.
circuit = QuantumCircuit(2, 2)

# 3. Apply Gates to create a Bell State (Φ+)
# Apply a Hadamard gate (H) to the first qubit (qubit 0).
# This puts it into a superposition of |0> and |1>.
print("Applying Hadamard gate to put one qubit in superposition...")
circuit.h(0)

# Apply a Controlled-NOT (CNOT) gate.
# The first qubit (qubit 0) is the control, and the second qubit (qubit 1) is the target.
# This entangles the two qubits. If qubit 0 is |1>, it flips qubit 1.
# If qubit 0 is |0>, it does nothing to qubit 1.
print("Applying CNOT gate to entangle the two qubits...")
circuit.cx(0, 1)

# 4. Measure the Qubits
# We can't know the state of the qubits until we measure them.
# This collapses the superposition and entanglement.
# We map the quantum measurement from our qubits to our classical bits.
circuit.measure([0, 1], [0, 1])

# Let's see the circuit we built
print("\nQuantum Circuit Diagram:")
print(circuit)

# 5. Simulate the Circuit
# We use the AerSimulator for a high-performance simulation on a classical computer.
simulator = AerSimulator()

# Transpile the circuit for the simulator for better performance.
compiled_circuit = transpile(circuit, simulator)

# Run the simulation. We run it 1024 times (called "shots") to see the probability distribution.
print("\nRunning simulation (1024 shots)...")
job = simulator.run(compiled_circuit, shots=1024)

# 6. Get and Print the Results
result = job.result()
counts = result.get_counts(compiled_circuit)
print("\nTotal counts for '00' and '11' are:", counts)

# 7. Visualize the Results
# The histogram shows the probability of measuring each state.
print("Displaying results histogram...")
plot_histogram(counts)
plt.show()

