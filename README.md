# Nanopore Sequencing Basecaller

A Python rule-based QC/audit demonstrator with a standalone browser **CTC greedy-decoding example**. The browser decodes nucleotide probability vectors that have **already** been produced by a model; it does not infer bases from raw nanopore current. The Python workers evaluate arbitrary numeric thresholds and status keywords, not experimentally derived Oxford Nanopore quality metrics.

**Research and teaching demonstration only.** No trained neural network, raw-signal processing, calibrated Phred quality scores, modified-base calling, specimen validation, or clinical decision support is provided.

## Components

| Component | What it actually does |
| --- | --- |
| **web/** | Offline-capable, static browser CTC greedy decoder plus local threshold-audit demo |
| **agents/** | Pydantic/FastAPI rule-based supervisor with an in-process, HMAC-chained audit log |
| **cli.py** | CLI for a single audit, CSV batch, mock status query, and API server |
| **nanopore_basecaller/** | Older, independent rule-based audit engine and CLI |
| **enrichment.py** | Illustrative threshold checks named after sequencing tasks; **does not implement** those analyses |
| **simulator.py** | Synthetic traffic exerciser for the rule-based supervisor |

## Browser decoder

Open **web/index.html** locally in a browser, or use a verified GitHub Pages deployment when available. No server, Pyodide, GPU, or external JavaScript dependencies are required.

1. Paste a JSON 2D array or CSV with columns blank,A,C,G,T and one probability row per timestep (values between 0 and 1; each row sums to 1 within 0.01).
2. Run **Decode CTC**. Greedy decoding selects the largest posterior per timestep, collapses consecutive repeated labels, then removes the blank label. A blank between repeated bases preserves the repeat.
3. Export the output as FASTA. The reported mean argmax probability is **not** calibrated base quality or an accuracy estimate.

Input is limited to 1 MB and 20,000 timesteps. Import and computation remain on the user's device. The separate local QC panel applies the existing arbitrary rules (primary >25, secondary >12, critical flag, anomaly keywords) and does not create signed audit logs.

## Python installation

Requires Python 3.10+.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[server,test]"
python -m pytest -q
node --test tests/test_basecaller.cjs  # optional: Node.js 18+
~~~

For a smaller CLI-only installation, use **python -m pip install .** (requires Pydantic but not FastAPI/Uvicorn).

## CLI

~~~bash
nanopore-sequencing-basecaller audit --task-id T-001 --target SPECIMEN-001 --primary 29 --secondary 13 --status DISCORDANT
nanopore-sequencing-basecaller batch -i sample.csv -o results.csv
nanopore-sequencing-basecaller chat "What is the system status?"
nanopore-sequencing-basecaller verify-audit
nanopore-sequencing-basecaller serve --host 127.0.0.1 --port 8000
squigglecaller-audit audit --primary 29 --secondary 13  # older audit workflow
python simulator.py --tasks 100
~~~

The batch CSV requires a primary_metric column; other recognized fields include task_id, target_identifier, secondary_metric, status_descriptor, and is_critical_flag. Flag values are case-insensitive true/false, yes/no, and 1/0. Invalid records are skipped with a warning by the primary CLI.

## API

Start the server with the CLI above. Useful endpoints:

- **GET /health**: health response
- **POST /api/audit**: validate input and return a rule-based audit dossier
- **POST /api/chat**: deterministic mock response (not model inference)
- **GET /metrics**: JSON counters, **not** Prometheus text
- **GET /api/audit/logs**: in-memory audit hash-chain records and verification result
- **GET /docs**: FastAPI-generated OpenAPI UI

The API uses illustrative thresholds and returns no prediction of sequencing accuracy. The HMAC log is **process-local and nonpersistent**: it is not an immutable ledger, not a full audit of all input data, and not a substitute for regulated logging. Provide AUDIT_SECRET_KEY for stable signing within a process; without it, the service generates an ephemeral key. Do not send patient-identifying data. Regex-based screening catches certain identifier formats but does **not** guarantee removal of protected health information. Do not expose this unauthenticated demo server or its logs to untrusted networks.

## Docker

~~~bash
docker build -t nanopore-sequencing-basecaller .
docker run --rm -p 127.0.0.1:8000:8000 -e AUDIT_SECRET_KEY="$(openssl rand -hex 32)" nanopore-sequencing-basecaller
~~~

For Compose, set AUDIT_SECRET_KEY in a local .env file and run **docker compose up --build**. The file is ignored by Git.

## CI, deployment, compatibility

GitHub Actions runs Python tests on 3.10–3.12 and JavaScript syntax/decoder tests using Node. A separate Pages workflow publishes the static **web/** folder on pushes to **master**, provided GitHub Pages is enabled with GitHub Actions as the source. No Python server or trained model runs on GitHub Pages.

The browser demo uses modern JavaScript supported by current Chrome, Firefox, Safari and Edge. All input stays within the local page unless the user separately uses the Python API. It does not persist input in browser storage.

## License

MIT. See [LICENSE](LICENSE).
