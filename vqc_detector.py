import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# 1. CARICAMENTO E NORMALIZZAZIONE DEL DATASET REALE
try:
    data = np.genfromtxt('dataset_quantistico.csv', delimiter=',', skip_header=1)
    X_data = data[:, 0:2]  # Colonna 0 (QBER) e Colonna 1 (CHSH)
    y_data = data[:, 2]    # Colonna 2 (Label)
    num_samples = len(y_data)
    print(f"[OK] Dataset caricato correttamente. Trovati {num_samples} campioni quantistici.")
except OSError:
    print("[!!!] ERRORE: File 'dataset_quantistico.csv' non trovato. Esegui prima 'generatore_e91.py'!")
    exit()

# Normalizzazione matematica nell'intervallo [0, pi] per la Quantum Feature Map
X_min = X_data.min(axis=0)
X_max = X_data.max(axis=0)
X_norm = (X_data - X_min) / (X_max - X_min) * np.pi

# 2. PROGETTAZIONE DEL CIRCUITO QUANTISTICO MULTI-LAYER (VQC)
def build_vqc_circuit(x, theta, layers=2):
    """Mappa il QBER e il CHSH reali nel circuito quantistico e applica l'Ansatz."""
    qc = QuantumCircuit(2)
    
    # --- FASE 1: Feature Map Quantistica (Angle Encoding) ---
    qc.ry(x[0], 0)  # QBER mappato sul Qubit 0
    qc.ry(x[1], 1)  # CHSH mappato sul Qubit 1
    
    # --- FASE 2: Ansatz Parametrizzato (Istruttore del Modello) ---
    param_idx = 0
    for _ in range(layers):
        qc.rx(theta[param_idx], 0)
        qc.rx(theta[param_idx + 1], 1)
        qc.cx(0, 1)  # Entanglement Lineare
        qc.ry(theta[param_idx + 2], 0)
        qc.ry(theta[param_idx + 3], 1)
        param_idx += 4
        
    return qc

# 3. PREDIZIONE E FUNZIONE DI COSTO
def predict_probability(x, theta, layers=2):
    qc = build_vqc_circuit(x, theta, layers)
    state = Statevector.from_instruction(qc)
    probs = state.probabilities()
    # Misura dello stato del sistema per calcolare la probabilità della classe 1
    return probs[1] + probs[3]

def cost_function(theta, layers=2):
    loss = 0.0
    for i in range(num_samples):
        pred = predict_probability(X_norm[i], theta, layers)
        loss += (pred - y_data[i]) ** 2
    return loss / num_samples

# 4. ADDESTRAMENTO DEL MODELLO TRAMITE OTTIMIZZATORE CLASSICO COBYLA
print("\n=== AVVIO ADDESTRAMENTO QUANTUM INTRUSION DETECTION SYSTEM ===")
num_layers = 2
num_parameters = 4 * num_layers
np.random.seed(42)
initial_theta = np.random.uniform(0, 2 * np.pi, num_parameters)

print(f"[INFO] Ottimizzazione in corso su {num_parameters} parametri variazionali...")
result = minimize(lambda t: cost_function(t, num_layers), initial_theta, method='COBYLA', options={'maxiter': 100})
optimal_theta = result.x
print("[INFO] Addestramento quantistico completato con successo!")

# 5. CALCOLO ACCURATEZZA FINALE
predictions = []
for i in range(num_samples):
    prob = predict_probability(X_norm[i], optimal_theta, num_layers)
    predictions.append(1 if prob > 0.5 else 0)

accuracy = np.mean(np.array(predictions) == y_data) * 100
print(f"-> Accuratezza finale del Q-IDS: {accuracy:.2f}%")

# 6. VISUALIZZAZIONE DEL CONFINE DI DECISIONE REALE
plt.figure(figsize=(10, 6))

xx, yy = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, np.pi, 30))
grid_points = np.c_[xx.ravel(), yy.ravel()]
grid_preds = []

for pt in grid_points:
    grid_preds.append(predict_probability(pt, optimal_theta, num_layers))
grid_preds = np.array(grid_preds).reshape(xx.shape)

# Disegna le aree di probabilità calcolate dal VQC[span_15](start_span)[span_15](end_span)
plt.contourf(xx, yy, grid_preds, levels=20, cmap='coolwarm', alpha=0.6)
plt.colorbar(label='Probabilità Stato Compromesso (Presenza di Eve)')

# Plot dei veri dati fisici estratti dall'E91
plt.scatter(X_norm[y_data == 0, 0], X_norm[y_data == 0, 1], color='blue', edgecolors='k', s=70, label='Canale Sicuro (Solo Rumore)')
plt.scatter(X_norm[y_data == 1, 0], X_norm[y_data == 1, 1], color='red', edgecolors='k', s=70, label='Canale Compromesso (Eve Rilevata)')

plt.title(f"Quantum Intrusion Detection System (VQC su Dati E91) - Acc: {accuracy:.2f}%")
plt.xlabel("Feature 1: QBER Quantistico Normalizzato (da Basi Coincidenti)")
plt.ylabel("Feature 2: Indice CHSH |S| Normalizzato (Test di Bell)")
plt.legend(loc='lower left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()
