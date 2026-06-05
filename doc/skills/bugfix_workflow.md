# Skill: bugfix workflow

Usar esta skill al corregir un bug Odoo, en la sesión VS Code + Claude. Source of
truth: `doc/skills/`.

## Pasos

### 1. Entender y reproducir

- Confirmar síntoma exacto, comportamiento incorrecto o mensaje de error.
- Capturar pasos mínimos de reproducción cuando sea posible.
- Identificar área afectada: modelo / vista / action / workflow / datos / seguridad.

### 2. Localizar la causa raíz

- Inspeccionar solo los archivos relevantes.
- Comparar comportamiento esperado contra task/spec y `doc/project/<modulo>/*`
  cuando aplique.

### 3. Planificar el fix

Para fixes no triviales, proponer un plan antes de editar:

- causa raíz;
- fix mínimo;
- archivos afectados;
- tests / regresiones;
- impacto en documentación.

### 4. Implementar el fix mínimo

- Arreglar la causa raíz, no solo el síntoma.
- Evitar refactors amplios fuera del alcance.
- Preservar el comportamiento existente fuera del bug.

### 5. Validar

- Re-ejecutar o describir pasos de reproducción y comportamiento corregido.
- Agregar / actualizar tests de regresión cuando sea factible.
- Marcar tests como `PENDIENTE USER-RUN` salvo que haya evidencia.

## Output contract

Salida en español rioplatense, formato:

```md
1. Referencia
2. Síntoma y reproducción
3. Causa raíz
4. Plan de fix
5. Estado de ejecución
6. Cómo probar
7. Tests: OK / PENDIENTE USER-RUN / N/A + motivo
8. Impacto en documentación
9. Riesgos / pendientes
10. Sugerencia de close gate: Ready / Blocked
```
