import os
import json
import time
import logging
import psycopg_pool

logger = logging.getLogger(__name__)

_pool: psycopg_pool.AsyncConnectionPool | None = None
_prompt_cache: dict = {}
CACHE_TTL = 300  # 5 minutos

async def get_pool() -> psycopg_pool.AsyncConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg_pool.AsyncConnectionPool(
            os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
            open=False,
        )
        await _pool.open()
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

async def load_prompt(platform: str = "whatsapp") -> str:
    """Carga y construye el system prompt desde PostgreSQL con caché en memoria."""
    now = time.time()

    if platform in _prompt_cache and now - _prompt_cache[platform]["ts"] < CACHE_TTL:
        logger.debug(f"Prompt para '{platform}' servido desde caché.")
        return _prompt_cache[platform]["value"]

    try:
        pool = await get_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT role, system_prompt, workflow, behavioral_rules
                    FROM prompts
                    WHERE platform = %s AND active = TRUE
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (platform,),
                )
                row = await cur.fetchone()

        if not row:
            raise ValueError(f"No active prompt found for platform: {platform}")

        role, system_prompt, workflow, behavioral_rules = row

        full_prompt = f"""Rol: {role}

{system_prompt}

FLUJO DE TRABAJO:
{json.dumps(workflow, ensure_ascii=False, indent=2)}

REGLAS DE COMPORTAMIENTO:
{chr(10).join(f'- {rule}' for rule in behavioral_rules)}
"""
        _prompt_cache[platform] = {"value": full_prompt, "ts": now}
        logger.info(f"Prompt para '{platform}' cargado desde DB y cacheado.")
        return full_prompt

    except Exception as e:
        logger.error(f"Error loading prompt from DB: {e}")

        if platform in _prompt_cache:
            logger.warning(f"Usando caché expirado para '{platform}' por fallo en DB.")
            return _prompt_cache[platform]["value"]

        return "Eres el Agente Financiero, experto en el mercado colombiano. Responde de forma clara y concisa."