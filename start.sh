#!/bin/bash

# Define el nombre del entorno virtual
VENV_DIR="venv"

# Detecta el sistema operativo para el comando de activación adecuado
if [[ "$OSTYPE" == "msys" ]]; then
    ACTIVATE_CMD="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_CMD="$VENV_DIR/bin/activate"
fi

echo "🔍 Verificando entorno virtual..."

# Verifica si el directorio del entorno virtual existe
if [ ! -d "$VENV_DIR" ]; then
    echo "📁 No se encontró un entorno virtual. Creando uno nuevo..."
    python3 -m venv $VENV_DIR
    echo "✅ Entorno virtual creado."
else
    echo "✅ Se encontró el entorno virtual existente."
fi

# Activa el entorno virtual
echo "⚙️ Activando el entorno virtual..."
source $ACTIVATE_CMD
echo "✅ Entorno virtual activado."

# Instala las dependencias
echo "📦 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt
echo "✅ Dependencias instaladas."

# Pregunta al usuario sobre el modo de inicio
echo "🛠️ ¿Desea iniciar en modo desarrollo o producción? (dev/prod)"
read MODE

# Ejecuta npm run build dentro del directorio /client
if [ "$MODE" == "prod" ]; then
    echo "🔨 Ejecutando build de producción para el cliente..."
    pushd client
    npm install
    npm run build
    popd
    echo "✅ Build de producción completado."
else
    echo "📦 Instalando dependencias del cliente en modo desarrollo..."
    pushd client
    npm install
    echo "🚀 Iniciando cliente en modo desarrollo..."
    npm run dev &
    popd
fi

# Ejecuta la aplicación FastAPI
echo "🚀 Iniciando la aplicación FastAPI..."
python main.py
