import logging
import httpx
from fastapi import APIRouter, Request, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import JSONResponse
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode and hub_verify_token:
        if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return int(hub_challenge)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing verification parameters")

async def process_message(from_number: str, msg_body: str):
    """Se ejecuta en background — Meta ya recibió su 200 OK."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.AGENT_WORKER_URL}/agent/run",
                json={"message": msg_body, "phone_number": from_number},
            )
            resp.raise_for_status()
            agent_response = resp.json()["response"]
            logger.info(f"Agent response: {agent_response}")

        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
                headers={
                    "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": from_number,
                    "text": {"body": agent_response},
                },
            )
    except Exception as e:
        logger.error(f"Error processing message in background: {str(e)}")

@router.post("")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()

        if body.get("object"):
            entry = body.get("entry", [])
            if (
                entry and
                entry[0].get("changes") and
                entry[0]["changes"][0].get("value") and
                entry[0]["changes"][0]["value"].get("messages")
            ):
                value = entry[0]["changes"][0]["value"]
                from_number = value["messages"][0]["from"]
                msg_body = value["messages"][0]["text"]["body"]

                logger.info(f"Message from {from_number}: {msg_body}")

                # Retorna 200 a Meta de inmediato y procesa en background
                background_tasks.add_task(process_message, from_number, msg_body)

            return JSONResponse(content={"status": "ok"}, status_code=200)

        return JSONResponse(content={"status": "not a whatsapp payload"}, status_code=404)

    except Exception as e:
        logger.error(f"Error parsing webhook: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)