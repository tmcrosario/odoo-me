# Narrativa funcional del sistema Mesa de Entradas

**Versión:** 1.0
**Fecha:** 2026-03-31
**Audiencia:** Usuarios, Product Owner, equipo funcional

---

## 1. Actores del sistema

El sistema reconoce tres perfiles de usuario:

- **Operador de Mesa de Entradas:** puede registrar y gestionar expedientes.
- **Usuario de consulta:** puede visualizar expedientes sin modificarlos.
- **Administrador (Manager):** tiene acceso completo, incluyendo configuración.

No existe actualmente un flujo de aprobación diferenciado por rol. Todos los operadores tienen capacidad de crear, editar y agregar movimientos.

---

## 2. El expediente: qué es y para qué sirve

Un **expediente** es un documento administrativo que ingresa al Tribunal Municipal de Cuentas (TMC) desde una dependencia externa o interna. Representa la unidad mínima de trazabilidad del sistema: todo documento que entra al TMC debe registrarse como expediente antes de poder circular por las distintas áreas.

Cada expediente tiene:

- Una **dependencia de origen** (quién lo genera): restringida a DEM, TMC o CM.
- Una **jurisdicción** (área funcional a la que pertenece).
- Un **número** de expediente.
- Un **período** (año).
- Un **tipo de documento**, que el sistema asigna automáticamente como "Expediente" (EXP).

El sistema genera automáticamente un **nombre único** para cada expediente con el formato `EXP-XXXXXX-ORIGEN/AÑO` (por ejemplo, `EXP-000042-DEM/2025`). Este nombre es calculado en tiempo real y queda visible desde el momento en que se completan los campos básicos.

---

## 3. Registro de un expediente

### 3.1 Campos mínimos requeridos

Para registrar un expediente, el operador debe completar:

1. Dependencia de origen
2. Jurisdicción
3. Número
4. Período

El tipo de documento (EXP) se asigna automáticamente al elegir la dependencia de origen. El operador no necesita seleccionarlo.

### 3.2 Validación de duplicados

Si ya existe un expediente con la misma combinación de dependencia + número + período, el sistema muestra un aviso al operador. El aviso es informativo: no impide guardar el expediente. La responsabilidad de verificar la información recae en el operador.

### 3.3 Campos extendidos (disponibles tras completar los básicos)

Una vez completados los cuatro campos mínimos, el formulario habilita campos adicionales:

- Temas principales del expediente
- Objeto/referencia del documento
- Fecha del documento
- Clave externa (identificador usado por la Municipalidad)
- Número de fojas

Estos campos son opcionales al momento del registro inicial.

### 3.4 Lo que ocurre al guardar

Cuando el operador guarda el expediente por primera vez, el sistema realiza automáticamente tres acciones:

1. **Registra el expediente en el sistema documental base del TMC**, vinculándolo al repositorio central de documentos.

2. **Registra el expediente en el sistema RAA** (Registro de Actos Administrativos), asociándolo al acto correspondiente.

3. **Genera movimientos iniciales** que documentan el ingreso físico del expediente. El número y recorrido depende de la dependencia de origen:
   - **DEM (y otras jurisdicciones):** dos movimientos — jurisdicción de origen → TMC, luego TMC → Mesa de Entradas.
   - **TMC:** un único movimiento — TMC → Mesa de Entradas (se omite el movimiento TMC→TMC, que no tiene sentido funcional).
   - **CM:** dos movimientos — CM → TMC, luego TMC → Mesa de Entradas. La jurisdicción se asigna automáticamente como CM sin intervención del operador.

Estas tres acciones son automáticas, atómicas (ocurren todas juntas o ninguna) y transparentes para el operador. No requieren intervención adicional.

---

## 4. Flujo de ingreso del documento

El flujo estándar de un expediente al ingresar al sistema es el siguiente:

```
Dependencia jurisdiccional de origen
        ↓
      TMC
        ↓
  Mesa de Entradas
```

Este recorrido queda registrado automáticamente como los primeros dos movimientos del expediente, con fecha y hora de creación.

A partir de ese momento, el expediente queda disponible en el sistema con su historial iniciado y puede continuar circulando entre dependencias mediante movimientos manuales.

---

## 5. Movimientos del expediente

### 5.1 Movimientos automáticos

Los dos primeros movimientos son generados por el sistema al momento de crear el expediente (ver sección 3.4). El operador no interviene en su creación.

### 5.2 Movimientos manuales

Una vez guardado el expediente, el operador puede registrar movimientos adicionales desde la pestaña **Movimientos**. Cada movimiento registra:

- Fecha y hora del movimiento
- Dependencia de origen (obligatorio)
- Dependencia de destino (obligatorio)
- Usuario que registra el movimiento

El sistema valida que la fecha del movimiento no sea futura y no sea anterior a la fecha de ingreso del expediente. No existen restricciones predefinidas sobre qué combinaciones de origen y destino son válidas: el operador puede registrar cualquier par de dependencias.

---

## 6. Trazabilidad

El sistema mantiene un historial completo de movimientos de cada expediente. Este historial es visible en la pestaña **Movimientos** del formulario del expediente.

Cada entrada del historial incluye: fecha, origen, destino y usuario responsable.

El sistema está diseñado para que el historial crezca por adición. Sin embargo, actualmente no existe una restricción técnica que impida editar o eliminar movimientos existentes.

No existe un campo de **estado actual** del expediente. El sistema no infiere automáticamente en qué dependencia se encuentra el expediente a partir de los movimientos registrados.

---

## 7. Reglas de negocio activas

| Regla | Descripción |
|---|---|
| Tipo de documento automático | Al seleccionar la dependencia de origen, el tipo "EXP" se asigna sin intervención del usuario. |
| Dependencias permitidas | Solo se pueden registrar expedientes de las dependencias DEM, TMC o CM. |
| Nombre generado automáticamente | El nombre del expediente se calcula en tiempo real con formato EXP-XXXXXX-ORIGEN/AÑO. |
| Movimientos iniciales automáticos | Al crear un expediente, se generan los movimientos iniciales según el origen: DEM → 2 movimientos (jurisdicción→TMC, TMC→ME); TMC → 1 movimiento (TMC→ME); CM → 2 movimientos (CM→TMC, TMC→ME). |
| Fojas — bloqueo después de creación | El número de fojas no puede modificarse una vez guardado el expediente, excepto por un Responsable de Mesa de Entradas. Las variaciones posteriores se registran a través de movimientos. |
| Registro automático en RAA | Todo expediente queda registrado en el sistema RAA al momento de su creación. |
| Aviso de duplicado | Si ya existe un expediente con igual origen, número y período, el sistema avisa pero no bloquea el guardado. |
| Fecha del documento | La fecha puede ser distinta a la fecha de registro en el sistema (incluye fechas pasadas). |
| Integridad de movimientos | Origen y destino son obligatorios en todo movimiento. La fecha no puede ser futura ni anterior a la fecha de ingreso. No se permiten movimientos duplicados (mismo expediente + origen + destino + fecha exacta). |

---

## 8. Limitaciones actuales del sistema

Las siguientes funcionalidades **no están implementadas** en la versión actual:

### 8.1 Sin estados de expediente

No existe un ciclo de vida formal del expediente (abierto, en proceso, cerrado, archivado). El sistema no tiene noción de en qué estado se encuentra cada expediente ni qué acciones son válidas en cada estado.

### 8.2 Sin seguimiento de ubicación actual

El sistema registra todos los movimientos del expediente, pero no calcula automáticamente en qué dependencia se encuentra actualmente. Para saberlo, el operador debe revisar el último movimiento del historial manualmente.

### 8.3 Sin validación de continuidad entre movimientos

Origen y destino son obligatorios en cada movimiento y las fechas tienen restricciones básicas (no futuras, no anteriores al ingreso). Sin embargo, no se verifica que el destino de un movimiento coincida con el origen del siguiente. El orden cronológico entre movimientos tampoco está validado: el operador puede registrar movimientos retroactivamente en cualquier orden.

### 8.4 Sin restricción técnica de append-only en movimientos

El diseño conceptual establece que los movimientos deben ser solo de adición (no modificables ni eliminables). Esta regla existe como principio pero no está enforceada técnicamente en el sistema actual.

### 8.5 Sin documentos relacionados

El tab "Documentos Relacionados" existe en el sistema pero está deshabilitado. No es posible vincular expedientes entre sí desde la interfaz actual.

### 8.6 Búsqueda de Mesa de Entradas por nombre

El movimiento automático hacia "Mesa de Entradas" depende de que exista una dependencia con ese nombre exacto en la base de datos. Si la dependencia no existe o su nombre difiere, el movimiento no se crea sin ningún aviso al operador.

### 8.7 Reglas de acceso por rol

El módulo ME define tres grupos: **Usuario**, **Responsable** y **Solo Lectura**. Las reglas de acceso a nivel de modelo (ir.model.access) están definidas para `me.document_exp` y `me.document_movement`. El bloqueo de fojas después de la creación solo puede ser levantado por un Responsable. Las restricciones de acceso a modelos de otros módulos (TMC, RAA) dependen de la configuración de esos módulos.
