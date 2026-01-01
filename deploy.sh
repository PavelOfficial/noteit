#!/bin/bash

# Скрипт деплоя для Markdown Notes App
# Собирает Docker образ и запускает новый контейнер

set -e  # Остановка при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
IMAGE_NAME="noteit-app"
CONTAINER_NAME="noteit-container"
PORT=5000

echo -e "${GREEN}=== Деплой Markdown Notes App ===${NC}"

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Ошибка: Docker не установлен или не доступен в PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}Шаг 1: Остановка и удаление существующего контейнера (если есть)...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo -e "${YELLOW}Шаг 2: Сборка Docker образа...${NC}"
docker build -t $IMAGE_NAME:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка: Не удалось собрать Docker образ${NC}"
    exit 1
fi

echo -e "${YELLOW}Шаг 3: Запуск нового контейнера...${NC}"

# Проверка наличия SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}Предупреждение: SECRET_KEY не установлен. Генерирую временный ключ...${NC}"
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-in-production")
fi

# Запуск контейнера
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:5000 \
    -e SECRET_KEY="$SECRET_KEY" \
    -e DATABASE_URL="${DATABASE_URL:-sqlite:///noteit.db}" \
    -v $(pwd)/instance:/app/instance \
    --restart unless-stopped \
    $IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка: Не удалось запустить контейнер${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Контейнер успешно запущен!${NC}"
echo -e "${GREEN}Приложение доступно по адресу: http://localhost:$PORT${NC}"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  Просмотр логов: docker logs -f $CONTAINER_NAME"
echo "  Остановка: docker stop $CONTAINER_NAME"
echo "  Перезапуск: docker restart $CONTAINER_NAME"
echo "  Удаление: docker rm -f $CONTAINER_NAME"

