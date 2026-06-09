# QNNX-Sentinel Post-Quantum Cryptography Engine
**Standard Operating Procedures & Cryptographic Workflows**

This document outlines the standard workflows for the QNNX-Sentinel engine. All cryptographic operations utilize Post-Quantum algorithms loaded dynamically from the local `libs/liboqs` installation.

---

## 1. Key Generation Workflow
Generates secure public-private keypairs for either KEM or Digital Signatures.

```mermaid
sequenceDiagram
    participant App as Client Application
    participant Core as app/crypto/__init__.py
    participant Engine as KEM/DSA Manager
    participant Lib as libs/liboqs

    App->>Core: Request Key Generation (Algorithm ID)
    Core->>Lib: Auto-resolve DLL Path
    Core->>Engine: Initialize Algorithm
    Engine->>Lib: Generate Keypair
    Lib-->>Engine: Raw Byte Data
    Engine-->>App: Return {public_key, private_key}
```
---

## 2. Key Encapsulation Mechanism (KEM)
Securely encapsulates a shared cryptographic secret meant for a specific receiver.
```mermaid
sequenceDiagram
    participant Sender as Sender (Client)
    participant Engine as KEM Manager
    participant Lib as libs/liboqs
    
    Sender->>Engine: encapsulate(public_key)
    Engine->>Lib: OQS_KEM_encaps()
    Lib-->>Engine: ciphertext, shared_secret
    Engine-->>Sender: Return {ciphertext, shared_secret}
    Note right of Sender: The ciphertext is transmitted over the network.<br/>The shared_secret is kept locally.
```
---
## 3. Digital Signature (DSA)
Creates a tamper-proof post-quantum signature for a given message or payload.

```mermaid
sequenceDiagram
    participant Signer as Signer (Client)
    participant Engine as DSA Manager
    participant Lib as libs/liboqs

    Signer->>Engine: sign_message(message, private_key)
    Engine->>Lib: OQS_SIG_sign()
    Lib-->>Engine: signature bytes
    Engine-->>Signer: Return signature
```
---
## 4. Signature Verification
Validates a digital signature against a message and a public key. Security Note: Enforces a strict rejection policy for any verification failure or malformed data. 

```mermaid
sequenceDiagram
    participant Verifier as Verifier (Client)
    participant Engine as DSA Manager
    participant Lib as libs/liboqs

    Verifier->>Engine: verify_signature(message, signature, public_key)
    Engine->>Lib: OQS_SIG_verify()
    alt Verification Success
        Lib-->>Engine: True
        Engine-->>Verifier: Return True (Accept)
    else Verification Failure
        Lib-->>Engine: False
        Engine-->>Verifier: Return False (Strict Reject)
    end
```