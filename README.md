# Quantum Intrusion Detection System (Q-IDS): Co-Design of E91 Protocol and VQC

## 📌 Overview
This project implements a Quantum Intrusion Detection System (Q-IDS) simulated in Qiskit to monitor and secure quantum key distribution (QKD) channels. By co-designing the **Ekert91 (E91) protocol** and a **Variational Quantum Classifier (VQC)**, the system dynamically distinguishes natural optical fiber perturbations from quantum state collapses caused by eavesdropping attacks.

---

## 🚨 Problem & Solution
* **The Problem:** Although the E91 protocol guarantees absolute key security via quantum entanglement, physical channel noise (e.g., bit flip and phase flip errors in optical fibers) mimics eavesdropping effects, leading to false alarms.
* **The Solution:** A smart telemetry system (Q-IDS) capable of separating natural environmental disturbances from state collapse caused by a Measure-and-Resend attack.

---

## 📐 Mathematical Foundation & Features
* **CHSH Inequality:** Evaluates quantum correlations using $S = E(A_1,B_1) - E(A_1,B_3) + E(A_3,B_1) + E(A_3,B_3).
* **Entanglement Threshold:** $S > 2$ indicates quantum correlations (safe channel), while $S \le 2$ signals entanglement collapse (attack detected).
* **Sifting & QBER:** Asymmetric measurement bases for Alice and Bob optimize the sifting rate (~22%). The Quantum Bit Error Rate (QBER) is calculated from key discrepancies on matching bases.
* **Feature Normalization:** Dataset features (QBER and CHSH) are scaled into $[0, \pi]$ for angular encoding in quantum gates.
* **Dataset Labels:** Label `0` indicates a safe channel, and Label `1` indicates an attacked channel.

---

## 🔬 Dataset Generation & Noise Modeling
* **Entanglement Generation:** EPR singlet states $|\psi^-\rangle = \frac{|01\rangle - |10\rangle}{\sqrt{2}}$ are generated using Qiskit.
* **Physical Noise Simulation:** Models optical fiber degradation via random Bit Flip and Phase Flip errors.
* **Eavesdropper Model:** Models Eve executing a Measure-and-Resend attack with random measurement angles, causing quantum state collapse.

---

## ⚙️ Quantum Machine Learning Architecture (VQC)
* **Quantum Feature Map:** Rotations $r_y(\theta)$ encode classical normalized data into quantum states across 2 qubits.
* **Variational Circuit:** Consists of 2 deep layers featuring parameterized $r_x$ and $r_y$ gates with $c_x$ entangling gates.
* **Hybrid Training Loop:**
  * Extracts measured probabilities from the final quantum state.
  * Optimizes classical parameters using the COBYLA optimizer by minimizing Mean Squared Error (MSE) over 100 iterations.
  * Eliminates shot noise by utilizing exact statevector probabilities during training.

---

## 📊 Results & Performance
* **Accuracy:** Achieves **100% classification accuracy** with a clear decision boundary dividing safe and compromised scenarios.
* **Safe Channel Profile:** Average QBER $\approx 3.02\%$ and average CHSH value $\approx 2.68$ (reaching $\approx 2.82$).
* **Attacked Channel Profile:** Average QBER $\approx 25.12\%$ and average CHSH value $\approx 1.38$.

---

## 🚀 Key Advantages & Future Outlook
* **Dynamic Security:** Learns adaptive channel degradation patterns without relying on rigid static thresholds.
* **Scalable Efficiency:** Requires only 2 qubits, making it lightweight and suitable for low-depth NISQ hardware deployment.
* **Commercial Application:** Serves as a foundational monitoring engine for real-time commercial QKD networks.
