from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import os
from services.db import (
    establecer_modo_usuario,
    obtener_modo_usuario,
    limpiar_modo_usuario,
    guardar_consulta,
)
from core.logging import setup_logger
from core.errors import handle_exception
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from services.db import get_db
from services.models import ConsultaIA
from core.auth.api_key import verify_api_key
from api.schemas import (
    EstadoUsuarioRequest,
    EstadoUsuarioResponse,
    ProcesarRequest,
    ProcesarResponse,
    ConsultaHistorialRequest,
    ConsultaHistorialResponse,
    ConsultaItem,
    InterpretarConsultaRequest,
    InterpretarConsultaResponse,
    ConsultaInteligenteRequest,
)
from openai import AsyncOpenAI
from openai import APIError as OpenAIError
from openai import RateLimitError as OpenAIRateLimitError
from openai import APITimeoutError as OpenAITimeoutError

# Importar los servicios de tasks
from services.tasks import translate, summarize, classify

# Configurar logging
logger = setup_logger("api.workflow_endpoints")

# Initialize AsyncOpenAI client for consultarInteligente solamente
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
    max_retries=3,
)

# Definir el router con dependencia global de API Key
router = APIRouter(tags=["workflow"], dependencies=[Depends(verify_api_key)])


# Endpoints
@router.post("/estado", response_model=EstadoUsuarioResponse)
async def gestionar_estado_usuario(request: EstadoUsuarioRequest):
    """
    Establece o consulta el estado/modo actual de un usuario.
    Utilizado para guardar qué acción ha elegido el usuario (resumir, traducir, etc.)
    """
    try:
        # Si el modo es vacío o null, solo consultamos
        if not request.modo or request.modo == "null":
            modo_actual = await obtener_modo_usuario(request.chat_id)
            mensaje = f"Estado actual: {modo_actual if modo_actual else 'Ninguno'}"
            return EstadoUsuarioResponse(
                chat_id=request.chat_id, modo_actual=modo_actual, mensaje=mensaje
            )

        # Si el modo es 'limpiar', eliminamos el estado
        if request.modo == "limpiar":
            await limpiar_modo_usuario(request.chat_id)
            return EstadoUsuarioResponse(
                chat_id=request.chat_id,
                modo_actual=None,
                mensaje="Estado limpiado correctamente",
            )

        # Establecemos el nuevo modo
        await establecer_modo_usuario(request.chat_id, request.modo)

        # Preparamos el mensaje según el modo
        mensajes = {
            "/resumir": "¿Qué texto quieres resumir?",
            "/traducir": "¿Qué texto quieres traducir?",
            "/clasificar": "¿Qué texto quieres clasificar?",
            "/consultar": "¿Qué quieres consultar del historial?",
        }

        mensaje = mensajes.get(request.modo, f"Modo cambiado a {request.modo}")

        return EstadoUsuarioResponse(
            chat_id=request.chat_id, modo_actual=request.modo, mensaje=mensaje
        )

    except Exception as e:
        logger.error(f"Error gestionando estado: {str(e)}")
        return EstadoUsuarioResponse(
            chat_id=request.chat_id, success=False, mensaje=f"Error: {str(e)}"
        )


@router.post("/procesar", response_model=ProcesarResponse)
async def procesar_texto(request: ProcesarRequest):
    """
    Procesa texto según el tipo de tarea especificado o el estado del usuario.
    Endpoint unificado para resumir, traducir, clasificar, etc.
    """
    try:
        # Si no se especifica tipo_tarea, intentamos obtenerlo del estado del usuario
        tipo_tarea = request.tipo_tarea
        if not tipo_tarea:
            modo_actual = await obtener_modo_usuario(request.chat_id)
            if not modo_actual:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "E202",
                        "message": "No se ha especificado tipo de tarea y no hay modo activo",
                        "details": {"chat_id": request.chat_id},
                    },
                )
            tipo_tarea = modo_actual.replace(
                "/", ""
            )  # Convertir '/resumir' a 'resumir'

        # Validar texto
        if not request.texto.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "E202",
                    "message": "El texto no puede estar vacío",
                    "details": {"tipo_tarea": tipo_tarea},
                },
            )

        # Preparar contexto y entrada para los servicios
        context = {"user_id": str(request.chat_id)}

        # Ejecutar la tarea según el tipo utilizando los servicios tasks
        if tipo_tarea == "resumir":
            input_data = {"text": request.texto}
            result = await summarize.run(input_data, context)
            resultado = result.get("summary", "")
        elif tipo_tarea == "traducir":
            input_data = {"text": request.texto, "lang": "en"}
            result = await translate.run(input_data, context)
            resultado = result.get("translation", "")
            idioma = "en"
        elif tipo_tarea == "clasificar":
            input_data = {"text": request.texto}
            result = await classify.run(input_data, context)
            # Convierte el dict a string (puedes usar json.dumps para formato legible)
            import json

            resultado = json.dumps(result.get("classification", ""), ensure_ascii=False)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "E202",
                    "message": f"Tipo de tarea desconocido: {tipo_tarea}",
                    "details": {"tipo_tarea": tipo_tarea},
                },
            )

        # Limpiar el estado del usuario solo si no se guardó en la función de tarea
        try:
            await limpiar_modo_usuario(request.chat_id)
        except Exception as e:
            logger.error(f"Error limpiando modo usuario: {str(e)}")
            # Continuamos aunque falle la limpieza

        return ProcesarResponse(
            chat_id=request.chat_id,
            resultado=resultado,
            tipo_tarea=tipo_tarea,
            mensaje="Procesamiento completado con éxito",
        )
    # Manejo de errores de OpenAI
    except OpenAITimeoutError as e:
        logger.error(f"Timeout de OpenAI: {e.message}")
        raise HTTPException(
            status_code=504,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except OpenAIRateLimitError as e:
        logger.error(f"Rate limit de OpenAI: {e.message}")
        raise HTTPException(
            status_code=429,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except OpenAIError as e:
        logger.error(f"Error de OpenAI: {e.message}")
        raise HTTPException(
            status_code=502,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
    except HTTPException as e:
        # Reenviar HTTPExceptions lanzadas explícitamente
        raise e
    except Exception as e:
        logger.error(f"Error procesando texto: {str(e)}")
        # Para otros errores, usar el manejador general
        error = handle_exception(e)
        raise HTTPException(
            status_code=error.status_code,
            detail={
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
        )


@router.post("/consultar", response_model=ConsultaHistorialResponse)
async def consultar_historial(
    request: ConsultaHistorialRequest, db: AsyncSession = Depends(get_db)
):
    """
    Consulta el historial de interacciones del usuario.
    Permite filtrar por tipo de tarea y limitar el número de resultados.
    """
    try:
        query = select(ConsultaIA).where(ConsultaIA.chat_id == request.chat_id)

        # Filtrar por tipo de tarea si se proporciona
        if request.tipo_tarea:
            query = query.where(ConsultaIA.tipo_tarea == request.tipo_tarea)

        # Ordenar por fecha descendente (más recientes primero)
        query = query.order_by(desc(ConsultaIA.fecha))

        # Limitar número de resultados
        query = query.limit(request.limit)

        # Ejecutar consulta
        result = await db.execute(query)
        consultas = result.scalars().all()

        # Convertir a modelo de respuesta
        items = [
            ConsultaItem(
                id=c.id,
                tipo_tarea=c.tipo_tarea,
                texto_original=c.texto_original,
                resultado=c.resultado,
                fecha=c.fecha,
            )
            for c in consultas
        ]

        return ConsultaHistorialResponse(
            consultas=items,
            total=len(items),
            mensaje=f"Se encontraron {len(items)} registros.",
        )

    except Exception as e:
        logger.error(f"Error consultando historial: {str(e)}")
        return ConsultaHistorialResponse(
            consultas=[],
            total=0,
            success=False,
            mensaje=f"Error consultando historial: {str(e)}",
        )


@router.post("/consultar-inteligente")
async def consultar_inteligente(
    request: ConsultaInteligenteRequest, db: AsyncSession = Depends(get_db)
):
    """
    Endpoint inteligente para consultar el historial de interacciones.
    Permite al usuario hacer preguntas en lenguaje natural como:
    - "Dame los 3 últimos registros clasificados"
    - "¿Cuántos registros se han traducido?"
    - "Quiero la fecha del primer registro traducido"
    - "Dame toda la tabla"

    El endpoint interpreta la intención usando IA, consulta la base de datos y devuelve la respuesta adecuada.
    Ejemplo de entrada:
        {"chat_id": 12345, "texto": "dame los 3 últimos registros clasificados"}
    Ejemplo de salida:
        {"success": true, "consultas": [...], "total": 3, "mensaje": "Se encontraron 3 registros."}
    """
    prompt = f"""
Eres un asistente que ayuda a estructurar consultas de historial para un bot de Telegram.
Dado el siguiente mensaje del usuario, responde SOLO con un JSON que indique:
- accion: "listar", "contar", "campo_especifico"
- tipo_tarea: "resumir", "traducir", "clasificar" o null
- limit: número de resultados (por defecto 5)
- orden: "desc" o "asc"
- campo: si el usuario pide un campo específico (por ejemplo, "fecha"), si no, null
- respuesta_esperada: "lista", "numero", "valor"
- Si el usuario pide el primer, segundo, tercer, cuarto, etc. registro, incluye un campo "posicion" (base 1, es decir, 1=primero, 2=segundo, etc.)
- Si el usuario pide el "antepenúltimo" registro, pon "posicion": -2; si pide el "penúltimo", pon "posicion": -1; si pide el "último", pon "posicion": -1.
- Si el usuario pide el "registro número N", pon "posicion": N.

Ejemplo: "cuántos registros se han clasificado"
Respuesta: {{"accion": "contar", "tipo_tarea": "clasificar", "respuesta_esperada": "numero"}}

Ejemplo: "quiero la fecha del primer registro traducido"
Respuesta: {{"accion": "campo_especifico", "tipo_tarea": "traducir", "limit": 1, "orden": "asc", "campo": "fecha", "posicion": 1, "respuesta_esperada": "valor"}}

Ejemplo: "dame la fecha del cuarto registro"
Respuesta: {{"accion": "campo_especifico", "tipo_tarea": null, "limit": 4, "orden": "asc", "campo": "fecha", "posicion": 4, "respuesta_esperada": "valor"}}

Ejemplo: "dame el tercer registro"
Respuesta: {{"accion": "listar", "tipo_tarea": null, "limit": 3, "orden": "asc", "posicion": 3, "respuesta_esperada": "valor"}}

Ejemplo: "dame el antepenúltimo registro"
Respuesta: {{"accion": "listar", "tipo_tarea": null, "limit": 2, "orden": "desc", "posicion": -2, "respuesta_esperada": "valor"}}

Ejemplo: "dame el registro número 15"
Respuesta: {{"accion": "listar", "tipo_tarea": null, "limit": 15, "orden": "asc", "posicion": 15, "respuesta_esperada": "valor"}}

Ejemplo: "dame los 3 últimos registros clasificados"
Respuesta: {{"accion": "listar", "tipo_tarea": "clasificar", "limit": 3, "orden": "desc", "respuesta_esperada": "lista"}}

Ejemplo: "dame toda la tabla"
Respuesta: {{"accion": "listar", "tipo_tarea": null, "limit": 100, "orden": "desc", "respuesta_esperada": "lista"}}

Mensaje del usuario: "{request.texto}"
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en estructurar consultas para un historial de IA.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        import json

        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        accion = data.get("accion", "listar")
        tipo_tarea = data.get("tipo_tarea")
        limit = data.get("limit", 5)
        orden = data.get("orden", "desc")
        campo = data.get("campo")
        respuesta_esperada = data.get("respuesta_esperada", "lista")
    except Exception as e:
        logger.error(f"Error interpretando consulta: {str(e)}")
        return {"success": False, "mensaje": f"Error interpretando consulta: {str(e)}"}

    try:
        query = select(ConsultaIA).where(ConsultaIA.chat_id == request.chat_id)
        if tipo_tarea:
            query = query.where(ConsultaIA.tipo_tarea == tipo_tarea)
        if orden == "asc":
            query = query.order_by(ConsultaIA.fecha.asc())
        else:
            query = query.order_by(desc(ConsultaIA.fecha))

        # Si se pide un registro específico por posición y no es una lista
        if (accion in ["listar", "campo_especifico"]) and data.get("posicion") and respuesta_esperada != "lista":
            idx = data.get("posicion", 1)
            if idx < 0:
                # Para negativos, necesitamos saber el total
                count_query = select(ConsultaIA).where(ConsultaIA.chat_id == request.chat_id)
                if tipo_tarea:
                    count_query = count_query.where(ConsultaIA.tipo_tarea == tipo_tarea)
                total = (await db.execute(count_query)).scalars().all()
                total_count = len(total)
                idx = total_count + idx
            else:
                idx = idx - 1
            if idx < 0:
                return {"success": False, "mensaje": f"No hay un registro en la posición solicitada (índice negativo)"}
            query = query.offset(idx).limit(1)
        elif accion in ["listar", "campo_especifico"]:
            query = query.limit(limit)

        result = await db.execute(query)
        consultas = result.scalars().all()

        # Acción: contar
        if accion == "contar":
            total = len(consultas)
            return {
                "success": True,
                "chat_id": request.chat_id,
                "total": total,
                "mensaje": f"Se han encontrado {total} registros{f' de tipo {tipo_tarea}' if tipo_tarea else ''}.",
            }

        # Acción: campo_especifico
        if accion == "campo_especifico" and campo and consultas:
            valor = getattr(consultas[0], campo, None)
            return {
                "success": True,
                "chat_id": request.chat_id,
                campo: valor,
                "mensaje": f"El campo '{campo}' del registro solicitado {'de tipo ' + tipo_tarea if tipo_tarea else ''} es: {valor}",
            }
        # Acción: listar con posición específica
        if accion == "listar" and data.get("posicion") and consultas and respuesta_esperada != "lista":
            item = consultas[0]
            # Construir descripción de la posición
            pos = data.get("posicion")
            if pos == -1:
                pos_desc = "penúltimo" if len(consultas) > 1 else "último"
            elif pos == -2:
                pos_desc = "antepenúltimo"
            elif isinstance(pos, int) and pos > 0:
                pos_desc = f"número {pos}"
            else:
                pos_desc = str(pos)
            return {
                "success": True,
                "chat_id": request.chat_id,
                "registro": ConsultaItem(
                    id=item.id,
                    tipo_tarea=item.tipo_tarea,
                    texto_original=item.texto_original,
                    resultado=item.resultado,
                    fecha=item.fecha,
                ),
                "mensaje": f"Registro {pos_desc} {'de tipo ' + tipo_tarea if tipo_tarea else ''} devuelto.",
            }

        # Acción: listar (por defecto)
        items = [
            ConsultaItem(
                id=c.id,
                tipo_tarea=c.tipo_tarea,
                texto_original=c.texto_original,
                resultado=c.resultado,
                fecha=c.fecha,
            )
            for c in consultas
        ]
        return {
            "success": True,
            "chat_id": request.chat_id,
            "consultas": items,
            "total": len(items),
            "mensaje": f"Se encontraron {len(items)} registros.",
        }
    except Exception as e:
        logger.error(f"Error consultando historial: {str(e)}")
        return {"success": False, "mensaje": f"Error consultando historial: {str(e)}"}


@router.get("/health")
async def health_check():
    """
    Endpoint de health check para verificar que el servicio está funcionando.
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
