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
    # If the second classical bit is 1, apply an X gate.
    with circuit.if_test((cbit2, 1)):
        circuit.x(target_qubit)
    # If the first classical bit is 1, apply a Z gate.
    with circuit.if_test((cbit1, 1)):
        circuit.z(target_qubit)


# --- Main Execution ---

# We need a circuit with 3 qubits and 2 classical bits
# q0: The message qubit
# q1: Alice's half of the entangled pair
# q2: Bob's half of the entangled pair (the destination)
qc = QuantumCircuit(3, 2)

# Define the initial message state we want to teleport.
# An angle of pi/4 creates a state that is not |0>, |1>, or an equal superposition.
message_angle = np.pi / 4

# === Build the Circuit Step-by-Step ===

# 1. Alice creates a message state on q0
create_message_state(qc, 0, message_angle)

# 2. Alice creates an entangled pair between q1 and q2
create_entangled_pair(qc, 1, 2)

# 3. Alice applies the teleportation protocol
teleportation_protocol(qc, 0, 1, 2)

# 4. Alice measures her qubits and "sends" the classical results to Bob,
#    who then reconstructs the state on q2.
classical_communication_and_reconstruction(qc, 0, 1, 2, 0, 1)

# Let's see the final circuit
print("\nFinal Quantum Teleportation Circuit:")
print(qc)

# === Verification using a Statevector Simulator ===
# To prove teleportation worked, we check if the state of q2 matches the
# original state of q0. We can't just measure it, as that would destroy the state.
# Instead, we use a simulator that shows the final quantum state of all qubits.

print("\nVerifying the final state of the target qubit...")
sv_sim = AerSimulator(method='statevector')
# The transpile step is good practice, even for simulators, especially with conditional logic
transpiled_qc = transpile(qc, sv_sim)
final_statevector = sv_sim.run(transpiled_qc).result().get_statevector()

# Display the final state on a Bloch Sphere. q2 should match the initial state of q0.
print("Displaying Bloch sphere for the final state. Qubit 2 should have the message.")
plot_bloch_multivector(final_statevector).show()