    circuit.measure(msg_qubit, cbit1)
    circuit.measure(ent_qubit, cbit2)
    circuit.barrier()

    print("Step 5: Reconstructing the message state on the target qubit.")
    
    # Note: For statevector simulation, these conditional operations are applied
    # to the statevector directly, as the statevector simulator cannot handle
    # mid-circuit measurements and classical conditional logic in the same way as a QASM simulator.
    # If the second classical bit is 1, apply an X gate.
    with circuit.if_test((cbit2, 1)):
        circuit.x(target_qubit)
Unchanged lines# q0: The message qubit
# q1: Alice's half of the entangled pair
# q2: Bob's half of the entangled pair (the destination)
qc = QuantumCircuit(3, 2)
# This `qc_full_protocol` will contain the full protocol with measurements and classical logic.
qc_full_protocol = QuantumCircuit(3, 2)

# Define the initial message state we want to teleport.
# An angle of pi/4 creates a state that is not |0>, |1>, or an equal superposition.
message_angle = np.pi / 4

# === Build the Circuit Step-by-Step ===
# === Build the Full Protocol Circuit (for diagram and QASM simulation) ===

# 1. Alice creates a message state on q0
create_message_state(qc, 0, message_angle)
create_message_state(qc_full_protocol, 0, message_angle)

# 2. Alice creates an entangled pair between q1 and q2
create_entangled_pair(qc, 1, 2)
create_entangled_pair(qc_full_protocol, 1, 2)

# 3. Alice applies the teleportation protocol
teleportation_protocol(qc, 0, 1, 2)
teleportation_protocol(qc_full_protocol, 0, 1, 2)

# 4. Alice measures her qubits and "sends" the classical results to Bob,
#    who then reconstructs the state on q2.
classical_communication_and_reconstruction(qc, 0, 1, 2, 0, 1)
classical_communication_and_reconstruction(qc_full_protocol, 0, 1, 2, 0, 1)

# Let's see the final circuit
print("\nFinal Quantum Teleportation Circuit:")
print(qc)
print("\nFinal Quantum Teleportation Circuit (with measurements and classical logic):")
print(qc_full_protocol)

# === Verification using a Statevector Simulator (for ideal state) ===
# To prove teleportation worked, we check if the state of q2 matches the original state of q0.
# The statevector simulator cannot handle mid-circuit measurements and classical conditional
# logic directly to produce a single final statevector for the entire system.
# Instead, we create a *separate* circuit for statevector simulation that omits the measurements
# and uses `save_statevector()` to capture the state before collapse.

print("\nVerifying the final state of the target qubit using statevector simulation...")

# Create a separate circuit for statevector simulation (no classical bits for measurement)
qc_sv_verify = QuantumCircuit(3)

# Re-apply the initial state and protocol gates to this new circuit
create_message_state(qc_sv_verify, 0, message_angle)
create_entangled_pair(qc_sv_verify, 1, 2)
teleportation_protocol(qc_sv_verify, 0, 1, 2)

# At this point, the state of q2 is entangled with q0 and q1.
# The teleportation protocol ensures that after the Bell measurement and conditional
# operations, q2 will be in the original message state.
# For statevector verification, we can simply save the statevector here.
# The `plot_bloch_multivector` will then show the state of q2 as the teleported state.
qc_sv_verify.save_statevector()

sv_sim = AerSimulator(method='statevector')
# The transpile step is good practice, even for simulators, especially with conditional logic
transpiled_qc_sv = transpile(qc_sv_verify, sv_sim)
result_sv = sv_sim.run(transpiled_qc_sv).result()
final_statevector_for_plot = result_sv.get_statevector()

# Display the final state on a Bloch Sphere. Qubit 2 should match the initial state of q0.
print("Displaying Bloch sphere for the final state. Qubit 2 should be in the original message state.")
plot_bloch_multivector(final_statevector_for_plot).show()

# Optional: Run the full circuit on a QASM simulator to see measurement counts
print("\nRunning full circuit on QASM simulator for measurement counts (optional)...")
qasm_sim = AerSimulator(method='qasm_simulator')
transpiled_qc_qasm = transpile(qc_full_protocol, qasm_sim) # Use qc_full_protocol here
job_qasm = qasm_sim.run(transpiled_qc_qasm, shots=1024)
counts_qasm = job_qasm.result().get_counts(transpiled_qc_qasm)
print("Measurement Counts (q0, q1):", counts_qasm)
# quantum_teleportation.py
#
# This script demonstrates the quantum teleportation protocol, which transfers
# the state of one qubit to another using entanglement and classical communication.

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector, plot_histogram


def create_message_state(circuit, qubit_index, message_angle):
    """Creates an arbitrary 'message' state on a specific qubit."""
    print(f"Step 1: Creating an arbitrary message state on qubit {qubit_index}.")
    # We'll use a rotation around the Y-axis to create a state that is a
    # superposition of |0> and |1> with specific amplitudes.
    circuit.ry(message_angle, qubit_index)
    circuit.barrier()


def create_entangled_pair(circuit, qubit1_index, qubit2_index):
    """Creates an entangled Bell pair between two qubits."""
    print(f"Step 2: Creating an entangled Bell pair between qubits {qubit1_index} and {qubit2_index}.")
    circuit.h(qubit1_index)
    circuit.cx(qubit1_index, qubit2_index)
    circuit.barrier()


def teleportation_protocol(circuit, msg_qubit, ent_qubit, target_qubit):
    """Applies the core teleportation gates."""
    print(f"Step 3: Applying teleportation protocol gates.")
    circuit.cx(msg_qubit, ent_qubit)
    circuit.h(msg_qubit)
    circuit.barrier()


def classical_communication_and_reconstruction(circuit, msg_qubit, ent_qubit, target_qubit, cbit1, cbit2):
    """Measures and uses classical bits to reconstruct the state."""
    print("Step 4: Measuring and sending classical information.")
    circuit.measure(msg_qubit, cbit1)
    circuit.measure(ent_qubit, cbit2)
    circuit.barrier()

    print("Step 5: Reconstructing the message state on the target qubit.")
    # In Qiskit 1.0+, c_if is replaced by the with circuit.if_test(...) context manager.
    # If the second classical bit is 1, apply an X gate.
    with circuit.if_test((cbit2, 1)):
        circuit.x(target_qubit)
    # If the first classical bit is 1, apply a Z gate.
    with circuit.if_test((cbit1, 1)):
        circuit.z(target_qubit)


# --- Main Execution ---

# Define the initial message state we want to teleport.
# An angle of pi/4 creates a state that is not |0>, |1>, or an equal superposition.
message_angle = np.pi / 4

# === Build the Full Protocol Circuit (for diagram and QASM simulation) ===
print("--- Building Full Protocol Circuit ---")
# This circuit represents the complete experiment with measurements.
# q0: The message qubit
# q1: Alice's half of the entangled pair
# q2: Bob's half of the entangled pair (the destination)
qc_protocol = QuantumCircuit(3, 2)

# 1. Alice creates a message state on q0
create_message_state(qc_protocol, 0, message_angle)

# 2. Alice creates an entangled pair between q1 and q2
create_entangled_pair(qc_protocol, 1, 2)

# 3. Alice applies the teleportation protocol
teleportation_protocol(qc_protocol, 0, 1, 2)

# 4. Alice measures her qubits and "sends" the classical results to Bob,
#    who then reconstructs the state on q2.
classical_communication_and_reconstruction(qc_protocol, 0, 1, 2, 0, 1)

# Let's see the final circuit
print("\nFinal Quantum Teleportation Circuit (with measurements):")
print(qc_protocol)

# === Verification using a Statevector Simulator (for ideal state) ===
print("\n--- Verifying Final State with Statevector Simulator ---")
# To verify the protocol, we create a separate circuit *without* measurements
# and check the ideal final quantum state of the target qubit.
qc_verify = QuantumCircuit(3)

# Re-apply the quantum gates to this new circuit
create_message_state(qc_verify, 0, message_angle)
create_entangled_pair(qc_verify, 1, 2)
teleportation_protocol(qc_verify, 0, 1, 2)

# The teleportation protocol ensures that after the Bell measurement and conditional
# operations, q2 will be in the original message state. For statevector verification,
# we can simply save the statevector here. The plot will show the final state of all qubits.
qc_verify.save_statevector()

sv_sim = AerSimulator(method='statevector')
transpiled_qc_verify = transpile(qc_verify, sv_sim)
result_sv = sv_sim.run(transpiled_qc_verify).result()
final_statevector = result_sv.get_statevector()

# Display the final state on a Bloch Sphere. q2 should match the initial state of q0.
print("Displaying Bloch sphere. Qubit 2 should be in the original message state.")
plot_bloch_multivector(final_statevector).show()
