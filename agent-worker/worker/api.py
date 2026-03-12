from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from worker.agent.graph import build_graph, run_agent
from worker.agent.prompt_loader import close_pool

load_dotenv()

POSTGRES_URL = os.getenv("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(POSTGRES_URL) as checkpointer:
        await checkpointer.setup()
        app.state.graph = build_graph(checkpointer)
        yield
    await close_pool()  # cierra el pool del prompt_loader al apagar

app = FastAPI(title="Agent Worker API", lifespan=lifespan)

class AgentRequest(BaseModel):
    message: str
    phone_number: str

class AgentResponse(BaseModel):
    response: str

@app.post("/agent/run", response_model=AgentResponse)
async def run(req: AgentRequest):
    response = await run_agent(app.state.graph, req.message, req.phone_number)
    return AgentResponse(response=response)