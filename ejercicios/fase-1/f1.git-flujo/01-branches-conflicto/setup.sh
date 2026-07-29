#!/usr/bin/env bash
# Crea (o recrea desde cero) el repo de práctica para el ejercicio 01.
# Ejecutar desde cualquier lugar: ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

rm -rf repo-practica
git init -q -b main repo-practica
cd repo-practica

cat > config.py <<'EOF'
MODELO = "claude-sonnet-5"
TEMPERATURA = 0.7
MAX_TOKENS = 1024
EOF
git add config.py
git commit -qm "config inicial del asistente"

# Branch 1: baja la temperatura
git switch -qc ajuste-temperatura
cat > config.py <<'EOF'
MODELO = "claude-sonnet-5"
TEMPERATURA = 0.2
MAX_TOKENS = 1024
EOF
git add config.py
git commit -qm "baja temperatura a 0.2 para respuestas deterministas"

# Branch 2: cambia de modelo (parte del MISMO punto que la branch 1)
git switch -q main
git switch -qc cambio-modelo
cat > config.py <<'EOF'
MODELO = "claude-opus-5"
TEMPERATURA = 1.0
MAX_TOKENS = 2048
EOF
git add config.py
git commit -qm "sube a opus con temperatura creativa y mas tokens"

git switch -q main
echo "repo-practica listo. Entra con: cd repo-practica"
