"""
FastAPI REST API Server for Nanopore Sequencing Basecaller.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Nanopore Sequencing Basecaller API",
    description="Rule-based QC demonstration. Not a raw nanopore signal basecaller or clinical decision-support system.",
    version="2.0.0",
)


@app.exception_handler(SecurityException)
async def sensitive_input_handler(request: Request, exc: SecurityException):
    # Do not echo user input or matching identifier back to the client.
    return JSONResponse(status_code=422, content={"detail": "Potential sensitive identifier detected. Remove identifying data and retry."})


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "nanopore-sequencing-basecaller", "domain": "QC demonstration", "standard": "Illustrative thresholds", "version": "2.0.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "RUNNING"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid supervisory query")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
