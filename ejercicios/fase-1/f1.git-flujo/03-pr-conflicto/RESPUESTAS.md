# Respuestas — 03-pr-conflicto

## P1 (antes de fusionar el PR A)

¿Qué mostrará GitHub en la página del PR B tras fusionar el A, y por qué? ¿El botón de merge estará disponible?

dira que hay un conflicto, y la razon es que ambos cambios tocaron la misma linea. el boton de merge no estara disponible pero va a proponer resolver el conflicto manualmente

## P2 (antes de resolver el conflicto)

¿En qué archivo y entre qué marcadores verás el conflicto? ¿Qué dos versiones de la línea aparecerán y de dónde viene cada una?

en README.md se vera el conflicto, justamente en la linea donde tenemos temperature, estara la version que vamos a mergear y la version que acabamos de mergear
marcadores: 
- Head: los cambios que tenemos en B
- branch: los cambios que acabamos de mergear de A en main

## P3 (después del paso 8)

¿Cuántos commits tiene la historia completa? ¿Cuántos merge commits añadió este flujo y de dónde salió cada uno?

ya la historia tiene 14 commits, desde el merge a866366 se agregaron 5 commits. 
el branch A agrego 2 commits, uno es el commit de mejorar la descripcion de temperatura y otro es el merge 2
el branch B agrego 3 commits, uno es el commit de branch agregando el rango de 0 a 1, otro es resolviendo los conflictos que hubo al intentar mergear a main despues del merge 2 (que se hizo pull desde el main y se resolvieron) y finalmente el merge 3 correctamente efectuado
