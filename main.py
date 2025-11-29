import os
import uvicorn
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from masumi.config import Config
from masumi.payment import Payment, Amount
from crew_definition import AuditSenseCrew  # ← updated import
from logging_config import setup_logging

# Configure logging
logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK")

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")

# Initialize FastAPI
app = FastAPI(
    title="AuditSense API (Masumi Compatible)",
    description="API for running AuditSense compliance agent pipeline with Masumi payment integration",
    version="1.0.0"
)

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
config = Config(
    payment_service_url=PAYMENT_SERVICE_URL,
    payment_api_key=PAYMENT_API_KEY
)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "example_purchaser_123",
                "input_data": {
                    "standard_url": "https://example.com/iso.txt",
                    "source_url": "https://example.com/policy.txt",
                    "doc_id": "policy_doc",
                    "scope": "IT Security"
                }
            }
        }


class ProvideInputRequest(BaseModel):
    job_id: str


# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_crew_task(input_data: dict) -> str:
    """ Execute the AuditSense CrewAI pipeline """
    logger.info(f"Starting AuditSense CrewAI task with input: {input_data}")

    crew = AuditSenseCrew(logger=logger)  # ← class-based usage

    # IMPORTANT: AuditSenseCrew stores Crew instance as crew.crew
    result = crew.crew.kickoff(inputs=input_data)

    logger.info("AuditSense pipeline completed successfully")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request """
    print(f"Received data: {data}")
    print(f"Received data.input_data: {data.input_data}")
    try:
        job_id = str(uuid.uuid4())
        agent_identifier = os.getenv("AGENT_IDENTIFIER")

        source_url = data.input_data.get("source_url")
        standard_url = data.input_data.get("standard_url")
        logger.info(f"Received job request for Standard URL: {standard_url}")
        logger.info(f"Evidence document URL: {source_url}")
        logger.info(f"Starting job {job_id} with agent {agent_identifier}")

        payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")
        payment_unit = os.getenv("PAYMENT_UNIT", "lovelace")

        amounts = [Amount(amount=payment_amount, unit=payment_unit)]
        logger.info(f"Using payment amount: {payment_amount} {payment_unit}")

        payment = Payment(
            agent_identifier=agent_identifier,
            config=config,
            identifier_from_purchaser=data.identifier_from_purchaser,
            input_data=data.input_data,
            network=NETWORK
        )

        logger.info("Creating payment request...")
        payment_request = await payment.create_payment_request()
        blockchain_identifier = payment_request["data"]["blockchainIdentifier"]
        payment.payment_ids.add(blockchain_identifier)
        logger.info(f"Created payment request with blockchain identifier: {blockchain_identifier}")

        jobs[job_id] = {
            "status": "awaiting_payment",
            "payment_status": "pending",
            "blockchain_identifier": blockchain_identifier,
            "input_data": data.input_data,
            "result": None,
            "identifier_from_purchaser": data.identifier_from_purchaser
        }

        async def payment_callback(blockchain_identifier: str):
            await handle_payment_status(job_id, blockchain_identifier)

        payment_instances[job_id] = payment
        logger.info(f"Starting payment status monitoring for job {job_id}")
        await payment.start_status_monitoring(payment_callback)

        return {
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": blockchain_identifier,
            "submitResultTime": payment_request["data"]["submitResultTime"],
            "unlockTime": payment_request["data"]["unlockTime"],
            "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
            "agentIdentifier": agent_identifier,
            "sellerVKey": os.getenv("SELLER_VKEY"),
            "identifierFromPurchaser": data.identifier_from_purchaser,
            "amounts": amounts,
            "input_hash": payment.input_hash,
            "payByTime": payment_request["data"]["payByTime"],
        }
    except Exception as e:
        logger.error(f"Error in start_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Input_data or identifier_from_purchaser is missing or invalid."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2) Payment Callback → Execute CrewAI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes AuditSense CrewAI after payment confirmation """
    try:
        logger.info(f"Payment {payment_id} completed for job {job_id}, executing AuditSense pipeline...")

        jobs[job_id]["status"] = "running"
        logger.info(f"Input data: {jobs[job_id]['input_data']}")

        result = await execute_crew_task(jobs[job_id]["input_data"])
        logger.info(f"Crew task completed for job {job_id}")

        result_string = result.raw if hasattr(result, "raw") else str(result)

        await payment_instances[job_id].complete_payment(payment_id, result_string)
        logger.info(f"Payment completed for job {job_id}")

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result

        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]

    except Exception as e:
        print(f"Error processing payment {payment_id} for job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]


# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job Status
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    logger.info(f"Checking status for job {job_id}")
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job_id in payment_instances:
        try:
            status = await payment_instances[job_id].check_payment_status()
            job["payment_status"] = status.get("data", {}).get("status")
        except:
            job["payment_status"] = "unknown"

    result_data = job.get("result")
    result = result_data.raw if result_data and hasattr(result_data, "raw") else None

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": result
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4) Availability
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    return {"status": "available", "type": "audit-sense", "message": "Server operational."}


# ─────────────────────────────────────────────────────────────────────────────
# 5) Input Schema
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """ AuditSense-specific input schema """
    return {
        "input_data": [
            {
                "id": "standard_url",
                "type": "string",
                "name": "Compliance Standard URL",
                "data": {
                    "description": "URL containing a compliance standard (ISO, SOC2, PCI, GDPR, RBI...)",
                    "placeholder": "https://example.com/iso27001.txt"
                }
            },
            {
                "id": "source_url",
                "type": "string",
                "name": "Evidence Document URL",
                "data": {
                    "description": "URL of the policy/procedure document to evaluate",
                    "placeholder": "https://example.com/policy.txt"
                }
            },
            {
                "id": "doc_id",
                "type": "string",
                "name": "Evidence Document ID",
                "data": {
                    "description": "Logical name for the evidence document",
                    "placeholder": "policy_doc"
                }
            },
            {
                "id": "scope",
                "type": "string",
                "name": "Audit Scope",
                "data": {
                    "description": "Scope of the audit (e.g., IT Security, HR Controls, Finance)",
                    "placeholder": "IT Security"
                }
            }
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy"}


# ─────────────────────────────────────────────────────────────────────────────
# Main Logic (standalone mode)
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Run AuditSense pipeline without API"""
    import os
    os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'

    print("\n" + "=" * 70)
    print("🚀 Running AuditSense agents locally (standalone mode)...")
    print("=" * 70 + "\n")

    input_data = {
        "standard_name": "Local Test Standard",  # ← REQUIRED
        "standard_url": None,  # ← optional, but needed as key
        "standard_text": "A.5 Security Policies\nA.6 Roles and Responsibilities",

        "source_url": "https://raw.githubusercontent.com/github/gitignore/main/LICENSE",
        "doc_id": "policy_doc",

        "controls": None,  # mapper needs presence
        "documents": None,  # mapper needs presence
        "evaluations": None,  # report needs presence

        "scope": "Local Test Run"
    }

    print(f"Standard Text Provided")
    print(f"Evidence URL: {input_data['source_url']}")

    print("\nProcessing with AuditSense CrewAI agents...\n")

    crew = AuditSenseCrew(verbose=True)
    result = crew.crew.kickoff(inputs=input_data)

    print("\n" + "=" * 70)
    print("✅ AuditSense Crew Output:")
    print("=" * 70 + "\n")
    print(result)
    print("\n" + "=" * 70 + "\n")

    sys.stdout.flush()
    sys.stderr.flush()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        port = int(os.environ.get("API_PORT", 8000))
        host = os.environ.get("API_HOST", "127.0.0.1")

        print("\n" + "=" * 70)
        print("🚀 Starting AuditSense FastAPI server with Masumi integration...")
        print("=" * 70)
        print(f"API Documentation:        http://{host}:{port}/docs")
        print(f"Availability Check:       http://{host}:{port}/availability")
        print(f"Status Check:             http://{host}:{port}/status")
        print(f"Input Schema:             http://{host}:{port}/input_schema\n")
        print("=" * 70 + "\n")

        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        main()
