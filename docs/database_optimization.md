# Optimización de Base de Datos

## Cambios Realizados en la Gestión de Base de Datos

La optimización de la base de datos se centró en consolidar las múltiples tablas específicas en la tabla unificada `consultas_ia`. Los cambios principales son:

### 1. Implementación del Modelo Unificado `ConsultaIA`

Hemos consolidado toda la persistencia de datos en un único modelo `ConsultaIA` que almacena todos los tipos de consultas:

```python
class ConsultaIA(Base):
    __tablename__ = "consultas_ia"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    tipo_tarea = Column(String(50), nullable=False, index=True)  # 'resumir', 'clasificar', etc.
    texto_original = Column(Text, nullable=False)
    resultado = Column(Text)
    idioma = Column(String(20), nullable=True)  # Solo para traducciones
    fecha = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

Este modelo unificado permite:
- Una estructura de datos coherente y predecible
- Facilidad para añadir nuevos tipos de tareas sin crear nuevas tablas
- Consultas más eficientes al tener todo el historial en una sola tabla
- Mayor simplicidad en el código de acceso a datos

### 2. Nueva Función Unificada `guardar_consulta`

Se ha implementado una función unificada para guardar consultas, que reemplaza a todas las funciones específicas anteriores:

```python
async def guardar_consulta(
    chat_id: int,
    tipo_tarea: str,
    texto_original: str,
    resultado: str,
    idioma: Optional[str] = None
) -> None:
    """
    Función unificada para guardar cualquier tipo de consulta en la base de datos.
    
    Args:
        chat_id: ID del chat/usuario
        tipo_tarea: Tipo de tarea ('resumir', 'traducir', 'clasificar')
        texto_original: Texto original enviado
        resultado: Resultado del procesamiento
        idioma: Idioma para traducciones (opcional)
    """
    async with async_session() as session:
        async with session.begin():
            nueva_consulta = ConsultaIA(
                chat_id=chat_id,
                tipo_tarea=tipo_tarea,
                texto_original=texto_original,
                resultado=resultado,
                idioma=idioma
            )
            session.add(nueva_consulta)
```

Esta función:
- Utiliza una única interfaz para todos los tipos de consultas
- Implementa mejor manejo de transacciones con `async with session.begin()`
- Reduce la duplicación de código en la capa de persistencia

### 3. Eliminación de Modelos y Funciones Legacy

Se han eliminado completamente:
- Los modelos antiguos `Resumen`, `Traduccion` y `Clasificacion`
- Las funciones específicas `guardar_resumen`, `guardar_traduccion` y `guardar_clasificacion`
- Los scripts de migración obsoletos

Esta limpieza reduce la complejidad del código y evita confusiones para futuros desarrolladores.

### 4. Mejora de Manejo de Transacciones

Se han actualizado todas las funciones de base de datos para usar el patrón `async with session.begin()`, que garantiza:
- Commits automáticos si la transacción se completa con éxito
- Rollbacks automáticos en caso de excepciones
- Mejor rendimiento al consolidar operaciones

### 5. Índices y Restricciones para Integridad de Datos

Se han añadido índices estratégicos para optimizar las consultas más frecuentes:

```sql
-- Índices básicos
CREATE INDEX idx_consultas_chat_id ON consultas_ia(chat_id);
CREATE INDEX idx_consultas_tipo_tarea ON consultas_ia(tipo_tarea);
CREATE INDEX idx_consultas_fecha ON consultas_ia(fecha);

-- Índice combinado para búsquedas comunes
CREATE INDEX idx_consultas_chat_tipo ON consultas_ia(chat_id, tipo_tarea);

-- Índice para evitar duplicados exactos (opcional)
CREATE INDEX idx_consultas_ia_unique
ON consultas_ia (chat_id, tipo_tarea, texto_original, resultado)
WHERE texto_original IS NOT NULL AND resultado IS NOT NULL;
```

## Beneficios de la Unificación

1. **Código más simple**: La lógica de persistencia está centralizada, reduciendo la duplicación.

2. **Consultas más eficientes**: Las consultas de historial ahora son más rápidas y flexibles.

3. **Mantenimiento simplificado**: Menos objetos que mantener y actualizar.

4. **Evolución facilitada**: Añadir nuevos tipos de tareas no requiere crear nuevas entidades.

5. **Mejor rendimiento**: Índices optimizados para los patrones de acceso más comunes.

## Recomendaciones Futuras

1. **Monitoreo de Rendimiento**: Implementar métricas para monitorear el rendimiento de las consultas a la base de datos.

2. **Particionamiento**: Si el volumen de datos crece significativamente, considerar el particionamiento de la tabla `consultas_ia` por fecha.

3. **Limpieza periódica**: Implementar una política de retención de datos para evitar el crecimiento excesivo de la tabla.

4. **Optimización de consultas**: Revisar periódicamente las consultas más frecuentes y añadir índices adicionales si es necesario.

5. **Backup automatizado**: Configurar backups regulares de la base de datos siguiendo las recomendaciones de la documentación.