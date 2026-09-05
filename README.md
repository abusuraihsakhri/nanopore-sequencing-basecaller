# Nanopore Sequencing Basecaller

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Nanopore Sequencing Basecaller is an enterprise-grade distributed component platform that orchestrates multiple specialized workers (QC, Safety, Protocol Conformance) to evaluate task payloads, classify urgency levels, and maintain a tamper-evident HMAC-SHA256 audit trail.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED, CRITICAL_STAT) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Agent Orchestration**: InvariantQCWorker, SafetyEscalationWorker, and ProtocolConformanceWorker.
- **Enrichment Suite**: Basecalling Quality Metrics, Context-Aware Basecalling, Modified Base Detection, Real-Time Basecalling, Structural Variant Detection, Metagenomic Classification, RNA Direct Sequencing, Workflow Integration.

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install fastapi uvicorn pydantic pytest
```

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 6. Run Simulation
```bash
python simulator.py --tasks 1000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task identifier | TASK-2026-001 |
| `--target` | Target/specimen identifier | KEY-TARGET-01 |
| `--primary` | Primary metric (float) | 28.5 |
| `--secondary` | Secondary metric (float) | 14.2 |
| `--critical` | Critical flag (boolean) | False |
| `--status` | Status descriptor | DISCORDANT |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or target key | Required |
| `primary_metric` | Primary measurement (finite float) | Required |
| `secondary_metric` | Secondary kinetic score | Optional (default 0.0) |
| `is_critical_flag` | Emergency escalation flag | Optional (default False) |
| `status_descriptor` | Status code or phenotype | Optional (default "NOMINAL") |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Deterministic mock integration (extensible to Ollama, Claude, GPT-4).
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration
Set the audit secret key via environment variable:
```bash
export AUDIT_SECRET_KEY="your-secure-random-key"
```

---

## 🧪 Testing & Verification

Run the automated test suite:
```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:
```bash
python simulator.py --tasks 1000
```

---

## 🐳 Container Deployment

```bash
# Build and run
docker build -t nanopore-sequencing-basecaller .
docker run -e AUDIT_SECRET_KEY=$(openssl rand -hex 32) -p 8000:8000 nanopore-sequencing-basecaller

# Or use docker-compose
echo "AUDIT_SECRET_KEY=$(openssl rand -hex 32)" > .env
docker-compose up -d
```

---

## 📁 Project Structure

```
nanopore-sequencing-basecaller/
├── agents/                    # Core agent orchestration
│   ├── api.py                 # FastAPI REST endpoints
│   ├── base.py                # Security, PHI guard, audit trail
│   ├── llm_factory.py         # LLM provider factory
│   ├── models.py              # Pydantic schemas
│   ├── supervisor.py          # Multi-agent supervisor
│   ├── workers.py             # Specialized worker agents
│   ├── learning.py            # Bayesian calibration engine
│   ├── metrics.py             # Prometheus metrics
│   └── streamer.py            # WebSocket telemetry
├── nanopore_basecaller/       # Alternative CLI entrypoint
│   ├── agents.py              # Sub-agent coordinators
│   ├── engine.py              # Domain evaluation engine
│   ├── models.py              # Data models
│   ├── server.py              # FastAPI server factory
│   └── cli.py                 # CLI interface
├── tests/                     # Pytest test suite
├── web/                       # Operations console (HTML)
├── cli.py                     # Main CLI entrypoint
├── simulator.py               # Stress testing simulator
├── enrichment.py              # Domain enrichment suite
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Compose configuration
└── .github/workflows/ci.yml   # CI/CD pipeline
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
