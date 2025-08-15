#!/usr/bin/env bash
set -euo pipefail

echo "[post-create] Ajustes iniciales..."

# Actualizar índices (rápido, ignora errores transitorios)
if command -v apt-get &>/dev/null; then
  sudo apt-get update -y || true
fi

# Asegurar directorio para historial bash/zsh montado
mkdir -p /home/vscode/commandhistory
chown vscode:vscode /home/vscode/commandhistory || true

# Configurar bash para usar historial persistente
if ! grep -q "HISTFILE=/home/vscode/commandhistory/.bash_history" /home/vscode/.bashrc; then
  echo 'export HISTFILE=/home/vscode/commandhistory/.bash_history' >> /home/vscode/.bashrc
  echo 'export HISTSIZE=50000' >> /home/vscode/.bashrc
  echo 'export SAVEHIST=50000' >> /home/vscode/.bashrc
fi

# Configurar zsh y Oh My Zsh si están disponibles
if command -v zsh &>/dev/null; then
  echo "[post-create] Configurando zsh y Oh My Zsh..."
  
  # Configurar historial persistente para zsh
  if [ -f "/home/vscode/.zshrc" ]; then
    if ! grep -q "HISTFILE=/home/vscode/commandhistory/.zsh_history" /home/vscode/.zshrc; then
      echo 'export HISTFILE=/home/vscode/commandhistory/.zsh_history' >> /home/vscode/.zshrc
      echo 'export HISTSIZE=50000' >> /home/vscode/.zshrc
      echo 'export SAVEHIST=50000' >> /home/vscode/.zshrc
    fi
  fi
  
  # Configurar Oh My Zsh si no está ya configurado
  if [ ! -d "/home/vscode/.oh-my-zsh" ] && command -v curl &>/dev/null; then
    echo "[post-create] Instalando Oh My Zsh..."
    su vscode -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended' || true
  fi
  
  # Cambiar shell por defecto a zsh para el usuario vscode
  if [ "$(getent passwd vscode | cut -d: -f7)" != "/bin/zsh" ]; then
    echo "[post-create] Cambiando shell por defecto a zsh..."
    sudo chsh -s /bin/zsh vscode || true
  fi
  
  # Configurar plugins y tema de Oh My Zsh
  if [ -f "/home/vscode/.zshrc" ] && [ -d "/home/vscode/.oh-my-zsh" ]; then
    echo "[post-create] Configurando plugins de Oh My Zsh..."
    # Agregar plugins útiles
    sed -i 's/plugins=(git)/plugins=(git docker terraform golang python node npm)/' /home/vscode/.zshrc || true
    
    # Configurar tema agnoster (opcional)
    sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' /home/vscode/.zshrc || true
  fi
fi

# Configurar vim
echo "[post-create] Configurando vim..."
if ! command -v vim &> /dev/null; then
    sudo apt-get install -y vim || true
fi

# Crear configuración básica de vim
if [ ! -f "/home/vscode/.vimrc" ]; then
    cat > /home/vscode/.vimrc << 'EOF'
" Configuración básica de vim
set number
set relativenumber
set autoindent
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab
syntax on
set hlsearch
set incsearch
set ignorecase
set smartcase
set showmatch
set ruler
set wildmenu
set encoding=utf-8
set background=dark
set backspace=indent,eol,start
EOF
    chown vscode:vscode /home/vscode/.vimrc || true
fi

# Instalar dependencias Python del proyecto si existen manifests
if [ -f "pyproject.toml" ]; then
  echo "[post-create] Instalando dependencias Python con uv (si disponible)";
  if command -v uv &>/dev/null; then
    uv sync || true
  else
    echo "uv no disponible; se omite sync"
  fi
fi

# Instalar dependencias Node si existe package.json
if [ -f "package.json" ]; then
  echo "[post-create] Instalando dependencias Node (pnpm preferido)";
  if command -v pnpm &>/dev/null; then
    pnpm install || true
  else
    npm install || true
  fi
fi

# Instalar Gemini CLI globalmente
echo "[post-create] Instalando Gemini CLI..."
if command -v npm &>/dev/null; then
  npm install -g @google/gemini-cli || true
else
  echo "npm no disponible; se omite instalación de Gemini CLI"
fi

# Inicializar gcloud auth configuración persistente (silencioso)
if command -v gcloud &>/dev/null; then
  echo "[post-create] Configurando gcloud..."
  # Crear directorios necesarios para gcloud
  mkdir -p /home/vscode/.config/gcloud/logs
  mkdir -p /home/vscode/.config/gcloud/configurations
  chown -R vscode:vscode /home/vscode/.config/gcloud || true
  
  # Configurar gcloud con configuración básica
  gcloud config set core/disable_usage_reporting true || true
fi

echo "[post-create] Completo."
