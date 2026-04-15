#!/usr/bin/env bash
# =============================================================
#  deploy.sh — Craque do Jogo Store
#  Roda tudo de uma vez na VPS após o merge dos PRs.
#  Uso: bash deploy.sh
# =============================================================

set -euo pipefail

DEPLOY_DIR="/opt/craque-do-jogo"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"
UPLOADS_DIR="$DEPLOY_DIR/uploads"
LOG_FILE="/tmp/scraper-$(date +%Y%m%d-%H%M%S).log"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; exit 1; }
step() { echo -e "\n${YELLOW}==> $1${NC}"; }

echo ""
echo "=============================="
echo "  Craque do Jogo — Deploy"
echo "  $(date '+%d/%m/%Y %H:%M')"
echo "=============================="

# ------------------------------------------------------------------
step "1/7  Atualizando código (git pull)"
# ------------------------------------------------------------------
cd "$DEPLOY_DIR"
git pull origin main || fail "git pull falhou"
ok "Código atualizado"

# ------------------------------------------------------------------
step "2/7  Build do frontend"
# ------------------------------------------------------------------
cd "$FRONTEND_DIR"
npm install --silent || fail "npm install falhou"
npm run build 2>&1 | tail -5 || fail "npm run build falhou"
cp -r dist/* "$BACKEND_DIR/static/"
ok "Frontend buildado e copiado para backend/static/"

# ------------------------------------------------------------------
step "3/7  Limpando uploads antigos"
# ------------------------------------------------------------------
cd "$DEPLOY_DIR"
COUNT=$(find "$UPLOADS_DIR" -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" 2>/dev/null | wc -l)
warn "Removendo $COUNT imagens antigas + metadata.json..."
rm -f "$UPLOADS_DIR"/*.jpg "$UPLOADS_DIR"/*.jpeg "$UPLOADS_DIR"/*.png "$UPLOADS_DIR"/metadata.json 2>/dev/null || true
ok "Uploads limpos"

# ------------------------------------------------------------------
step "4/7  Rodando scraper (isso demora 30-60 min)"
# ------------------------------------------------------------------
cd "$BACKEND_DIR"
pip install requests -q 2>/dev/null || true
warn "Log em tempo real em: $LOG_FILE"
warn "Para acompanhar em outro terminal: tail -f $LOG_FILE"
echo ""
python scraper.py 2>&1 | tee "$LOG_FILE" || fail "Scraper falhou — veja $LOG_FILE"

PRODUCTS=$(python3 -c "
import json, os
path = '$UPLOADS_DIR/metadata.json'
if os.path.exists(path):
    data = json.load(open(path))
    print(len(data))
else:
    print(0)
")

if [ "$PRODUCTS" -eq 0 ]; then
    fail "metadata.json vazio ou não gerado — cheque $LOG_FILE"
fi
ok "Scraper concluído: $PRODUCTS produtos coletados"

# ------------------------------------------------------------------
step "5/7  Populando o banco"
# ------------------------------------------------------------------
cd "$BACKEND_DIR"
python populate_db.py || fail "populate_db.py falhou"
ok "Banco populado"

# ------------------------------------------------------------------
step "6/7  Reiniciando o backend"
# ------------------------------------------------------------------
if systemctl is-active --quiet craque-do-jogo 2>/dev/null; then
    systemctl restart craque-do-jogo
    ok "Serviço reiniciado via systemctl"
elif pgrep -f "uvicorn main" > /dev/null; then
    pkill -f "uvicorn main" || true
    sleep 2
    nohup uvicorn main:app --host 0.0.0.0 --port 5051 > /tmp/backend.log 2>&1 &
    ok "Backend reiniciado via uvicorn"
else
    warn "Não encontrei processo do backend — inicie manualmente se necessário"
    warn "Comando: cd $BACKEND_DIR && uvicorn main:app --host 0.0.0.0 --port 5051"
fi

# ------------------------------------------------------------------
step "7/7  Verificando API"
# ------------------------------------------------------------------
sleep 3
TOTAL=$(curl -s "http://localhost:5051/api/products?per_page=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total', d.get('count', '?')))" 2>/dev/null || echo "?")
BRASILEIRAO=$(curl -s "http://localhost:5051/api/products?category=brasileirao&per_page=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total', d.get('count', '?')))" 2>/dev/null || echo "?")
COPA=$(curl -s "http://localhost:5051/api/products?category=copa-do-mundo&per_page=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total', d.get('count', '?')))" 2>/dev/null || echo "?")

echo ""
echo "  Produtos totais    : $TOTAL"
echo "  Brasileirão        : $BRASILEIRAO"
echo "  Copa do Mundo 2026 : $COPA"

echo ""
echo "=============================="
ok "Deploy concluído com sucesso!"
echo "=============================="
echo ""
echo "Próximos passos:"
echo "  1. Acesse https://craquedojogostore.com.br e confira o catálogo"
echo "  2. Feche o PR #1 (obsoleto)"
echo "  3. Rode: git tag -a v0.2.0 -m 'minkang scraper + categorization' && git push origin main --tags"
echo ""
