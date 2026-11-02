import numpy as np
import csv
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def run_e91_qiskit_pair(theta_A, theta_B, noise_level=0.0, eavesdropping=False):
    """Simula una singola coppia di qubit nel protocollo E91."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)
    qc.z(0)
    state = Statevector.from_instruction(qc)
    
    # Simulazione del rumore quantistico ambientale sul canale
    if noise_level > 0.0 and np.random.rand() < noise_level:
        qc_noise = QuantumCircuit(2)
        if np.random.rand() < 0.5:
            qc_noise.x(np.random.choice([0, 1]))  # Bit flip
        else:
            qc_noise.z(np.random.choice([0, 1]))  # Phase flip
        state = state.evolve(qc_noise)

    # Attacco di Eve (Measure-and-Resend)
    if eavesdropping:
        theta_E = np.random.choice([0, np.pi/4, np.pi/2])
        qc_eve_rot = QuantumCircuit(2)
        qc_eve_rot.ry(-2 * theta_E, 1)
        state = state.evolve(qc_eve_rot)
        _, state = state.measure([1])
        qc_eve_prep = QuantumCircuit(2)
        qc_eve_prep.ry(2 * theta_E, 1)
        state = state.evolve(qc_eve_prep)

    # Misura di Alice e Bob
    qc_meas = QuantumCircuit(2)
    qc_meas.ry(-2 * theta_A, 0)
    qc_meas.ry(-2 * theta_B, 1)
    state = state.evolve(qc_meas)
    
    final_outcome, _ = state.measure([0, 1])
    alice_bit = 1 if final_outcome[1] == '0' else -1
    bob_bit = 1 if final_outcome[0] == '0' else -1
    return alice_bit, bob_bit

def generate_telemetry_point(num_pairs=400, noise=0.02, eavesdropping=False):
    """Esegue l'E91 su N coppie e restituisce [QBER, CHSH]."""
    alice_angles = [0, np.pi/8, np.pi/4]          # 0°, 22.5°, 45°
    bob_angles = [np.pi/8, np.pi/4, 3*np.pi/8]    # 22.5°, 45°, 67.5°

    alice_choices = np.random.randint(0, 3, num_pairs)
    bob_choices = np.random.randint(0, 3, num_pairs)

    alice_results = []
    bob_results = []

    for i in range(num_pairs):
        theta_A = alice_angles[alice_choices[i]]
        theta_B = bob_angles[bob_choices[i]]
        a_res, b_res = run_e91_qiskit_pair(theta_A, theta_B, noise_level=noise, eavesdropping=eavesdropping)
        alice_results.append(a_res)
        bob_results.append(b_res)

    alice_results = np.array(alice_results)
    bob_results = np.array(bob_results)

    def compute_correlation(a_base, b_base):
        idx = np.where((alice_choices == a_base) & (bob_choices == b_base))[0]
        if len(idx) == 0: return 0
        return np.mean(alice_results[idx] * bob_results[idx])

    E1 = compute_correlation(0, 0)
    E2 = compute_correlation(0, 2)
    E3 = compute_correlation(2, 0)
    E4 = compute_correlation(2, 2)
    S = E1 - E2 + E3 + E4

    key_indices = np.where(((alice_choices == 1) & (bob_choices == 0)) | 
                           ((alice_choices == 2) & (bob_choices == 1)))[0]
    
    if len(key_indices) > 0:
        alice_key = np.where(alice_results[key_indices] == 1, 1, 0)
        bob_key = np.where(bob_results[key_indices] == -1, 1, 0)
        qber = np.mean(alice_key != bob_key) * 100
    else:
        qber = 50.0

    return qber, abs(S)

if __name__ == "__main__":
    np.random.seed(42)
    filename = "dataset_quantistico.csv"
    num_samples_per_class = 25  # 25 Sicuri + 25 Sotto Attacco = 50 scenari totali
    
    print(f"[*] Avvio simulazione quantistica per la generazione del dataset...")
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['QBER', 'CHSH', 'Label']) # Intestazione
        
        # 1. Generazione Scenari BENIGNI (Solo rumore casuale sulla fibra)
        print("-> Generazione traffico sicuro (Solo Rumore)...")
        for _ in range(num_samples_per_class):
            random_noise = np.random.uniform(0.01, 0.06) # Rumore variabile tra 1% e 6%
            qber, chsh = generate_telemetry_point(num_pairs=400, noise=random_noise, eavesdropping=False)
            writer.writerow([qber, chsh, 0]) # Label 0 = Sicuro
            
        # 2. Generazione Scenari MALICIOUS (Eve presente + rumore casuale)
        print("-> Generazione traffico compromesso (Attacco Eve)...")
        for _ in range(num_samples_per_class):
            random_noise = np.random.uniform(0.01, 0.06)
            qber, chsh = generate_telemetry_point(num_pairs=400, noise=random_noise, eavesdropping=True)
            writer.writerow([qber, chsh, 1]) # Label 1 = Sotto Attacco

    print(f"[OK] Generazione completata! File '{filename}' salvato con successo.")
