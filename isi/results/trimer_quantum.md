# Pulsed two-level emitter (QuTiP, pulsed_tls.run) coupled to the telecom gold-nanorod designs (n = 1.5)

Bright emitter q0 = 1, tau_0 = 1 ns; Gamma = Fp / tau_0. Resonant Gaussian pi pulse. Pure dephasing 1 ueV (4 K) or 10 meV (300 K).
Fp and eta at 1550 nm from tri2.md (mesh h = 5 nm).

| design | Fp | eta_a | 1/Gamma (fs) | pulse | g2(0) 4 K | I 4 K | g2(0) 300 K | I 300 K |
|---|---|---|---|---|---|---|---|---|
| dimer L = 270 | 272 | 87% | 3676 | 100 fs | 0.012 | 0.979 | 0.013 | 0.009 |
| dimer L = 270 | 272 | 87% | 3676 | 1 ps | 0.094 | 0.909 | 0.117 | 0.009 |
| dimer L = 280 | 288 | 87% | 3472 | 100 fs | 0.012 | 0.979 | 0.014 | 0.009 |
| trimer L3 = 300 (35 deg) | 215 | 77% | 4651 | 100 fs | 0.009 | 0.978 | 0.010 | 0.007 |
| trimer L3 = 300 (35 deg) | 215 | 77% | 4651 | 1 ps | 0.077 | 0.918 | 0.095 | 0.007 |
| trimer L3 = 340 (35 deg) | 315 | 73% | 3175 | 100 fs | 0.013 | 0.979 | 0.015 | 0.010 |

At 4 K all designs give g2 ~ 0.01 and I ~ 0.98 with 100 fs pulses; at room temperature I < 0.01 (hbar Gamma ~ 0.2 meV << 10 meV).
