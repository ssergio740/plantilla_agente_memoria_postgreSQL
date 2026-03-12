@Copyright © 2026 Sergio Andrés Sierra García. All rights reserved.

# plantilla_agente_memoria_postgreSQL

Este repositorio es una **plantilla básica** para desplegar un agente de [LangGraph](https://github.com/langgraph/langgraph) que mantiene su memoria en una **base de datos PostgreSQL local**. Está diseñado como punto de partida y se puede extender fácilmente según tus necesidades.

## Características principales

- **Memoria persistente en PostgreSQL**: el agente guarda conversaciones y estados en una base de datos PostgreSQL local para recuperación entre ejecuciones.
- **Arquitectura modular**: puedes añadir o modificar `tools` (herramientas) para personalizar el comportamiento del agente y conectarlo con APIs externas, lógica de negocio, etc.
- **Webhook funcional con WhatsApp**: la plantilla ya incluye un webhook listo para integrarse con WhatsApp. Solo es necesario configurar los parámetros en los archivos `.env` para que empiecen a llegar y enviarse mensajes.

## Personalización

1. Clona este repositorio.
2. Ajusta la configuración de PostgreSQL en `db-memory/init.sql` y los `.env` correspondientes.
3. Agrega tus propias **tools** en `agent-worker/worker/agent/tools` y regístralas en `agent-worker/worker/agent/graph.py`.
4. Actualiza los prompts o lógica del agente según el caso de uso.

> 🔧 *Consejo*: la flexibilidad de esta plantilla facilita la creación de agentes especializados agregando o modificando herramientas sin reescribir la infraestructura básica.

## Configuración del webhook

- Copia y renombra los archivos `.env.example` en los distintos servicios (agent-worker y api-service) a `.env`.
- Rellena las variables referentes a la conexión PostgreSQL y a las credenciales del proveedor de WhatsApp.
- Inicia los contenedores con `docker compose up --build` y verifica que el webhook esté recibiendo mensajes.

¡Listo! Ahora tienes una base para construir un agente conversacional con memoria persistente y un canal de WhatsApp listo para producción. Continúa agregando herramientas y lógica según tu caso de uso.
