#!/bin/bash
# Автоматическая установка ВФС плагина в Open Web UI
# Поддерживает Docker и локальные установки

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Переменные
VFS_VERSION="1.0.0"
INSTALL_TYPE=""
CONTAINER_ID=""
OPENWEBUI_PATH=""

# Функция определения типа установки Open Web UI
detect_installation() {
    log_info "Определение типа установки Open Web UI..."
    
    # Проверка Docker
    if command -v docker &> /dev/null; then
        CONTAINER_ID=$(docker ps --format "table {{.Names}}\t{{.Image}}" | grep -E "(open-web-ui|openwebui)" | head -1 | awk '{print $1}')
        if [ ! -z "$CONTAINER_ID" ]; then
            INSTALL_TYPE="docker"
            log_success "Найдена Docker установка: контейнер $CONTAINER_ID"
            return
        fi
    fi
    
    # Проверка systemd сервиса
    if systemctl is-active --quiet open-web-ui 2>/dev/null; then
        INSTALL_TYPE="systemd"
        # Попытка найти путь через systemd
        SERVICE_PATH=$(systemctl show -p ExecStart open-web-ui | cut -d'=' -f2- | awk '{print $1}')
        OPENWEBUI_PATH=$(dirname "$(dirname "$SERVICE_PATH")")
        log_success "Найдена systemd установка: $OPENWEBUI_PATH"
        return
    fi
    
    # Проверка процессов
    if pgrep -f "open-web-ui\|openwebui" > /dev/null; then
        PROCESS_PATH=$(ps aux | grep -E "(open-web-ui|openwebui)" | grep -v grep | head -1 | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        if [[ "$PROCESS_PATH" == *"python"* ]]; then
            INSTALL_TYPE="local"
            # Попытка определить путь
            read -p "Введите путь к директории Open Web UI: " OPENWEBUI_PATH
            if [ -d "$OPENWEBUI_PATH" ]; then
                log_success "Найдена локальная установка: $OPENWEBUI_PATH"
                return
            fi
        fi
    fi
    
    log_error "Open Web UI не найден или не запущен"
    echo "Убедитесь, что Open Web UI запущен и попробуйте снова"
    exit 1
}

# Проверка необходимых файлов
check_files() {
    log_info "Проверка файлов ВФС..."
    
    required_files=(
        "openwebui_integrated_vfs.js"
        "openwebui_vfs_plugin.js" 
        "vfs_config.json"
    )
    
    missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        log_error "Отсутствуют необходимые файлы:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
    
    log_success "Все файлы найдены"
}

# Установка для Docker
install_docker() {
    log_info "Установка ВФС в Docker контейнер $CONTAINER_ID..."
    
    # Создание директорий
    log_info "Создание директорий..."
    docker exec "$CONTAINER_ID" mkdir -p /app/plugins/vfs /app/backend/data/vfs/{projects,templates,cache} /app/backend/data/config
    
    # Копирование файлов
    log_info "Копирование файлов ВФС..."
    docker cp openwebui_integrated_vfs.js "$CONTAINER_ID":/app/static/js/ || {
        log_warning "Не удалось скопировать в /app/static/js/, пробуем /app/frontend/static/js/"
        docker cp openwebui_integrated_vfs.js "$CONTAINER_ID":/app/frontend/static/js/
    }
    
    docker cp openwebui_vfs_plugin.js "$CONTAINER_ID":/app/plugins/vfs/
    docker cp vfs_config.json "$CONTAINER_ID":/app/backend/data/config/
    
    # Установка прав
    log_info "Настройка прав доступа..."
    docker exec "$CONTAINER_ID" chown -R user:user /app/backend/data/vfs /app/plugins/vfs 2>/dev/null || {
        log_warning "Не удалось изменить владельца, используется другой пользователь"
    }
    
    # Перезапуск контейнера
    log_info "Перезапуск контейнера..."
    docker restart "$CONTAINER_ID"
    
    # Ожидание запуска
    log_info "Ожидание запуска контейнера..."
    sleep 10
    
    # Проверка работоспособности
    if docker exec "$CONTAINER_ID" ls /app/plugins/vfs/openwebui_vfs_plugin.js &>/dev/null; then
        log_success "ВФС плагин установлен в Docker контейнер"
    else
        log_error "Не удалось установить плагин"
        exit 1
    fi
}

# Установка для systemd
install_systemd() {
    log_info "Установка ВФС в systemd сервис..."
    
    if [ -z "$OPENWEBUI_PATH" ] || [ ! -d "$OPENWEBUI_PATH" ]; then
        log_error "Путь к Open Web UI не найден или недоступен: $OPENWEBUI_PATH"
        exit 1
    fi
    
    # Создание директорий
    log_info "Создание директорий..."
    sudo mkdir -p "$OPENWEBUI_PATH"/{plugins/vfs,static/js,backend/data/vfs/{projects,templates,cache},backend/data/config}
    
    # Копирование файлов
    log_info "Копирование файлов ВФС..."
    sudo cp openwebui_integrated_vfs.js "$OPENWEBUI_PATH"/static/js/
    sudo cp openwebui_vfs_plugin.js "$OPENWEBUI_PATH"/plugins/vfs/
    sudo cp vfs_config.json "$OPENWEBUI_PATH"/backend/data/config/
    
    # Установка прав
    log_info "Настройка прав доступа..."
    WEBUI_USER=$(ps aux | grep open-web-ui | grep -v grep | head -1 | awk '{print $1}')
    if [ ! -z "$WEBUI_USER" ]; then
        sudo chown -R "$WEBUI_USER":"$WEBUI_USER" "$OPENWEBUI_PATH"/backend/data/vfs "$OPENWEBUI_PATH"/plugins/vfs
    fi
    
    # Перезапуск сервиса
    log_info "Перезапуск сервиса Open Web UI..."
    sudo systemctl restart open-web-ui
    
    # Ожидание запуска
    log_info "Ожидание запуска сервиса..."
    sleep 5
    
    if systemctl is-active --quiet open-web-ui; then
        log_success "ВФС плагин установлен в systemd сервис"
    else
        log_error "Сервис не запустился после установки"
        sudo systemctl status open-web-ui
        exit 1
    fi
}

# Установка для локальной установки
install_local() {
    log_info "Установка ВФС в локальную установку..."
    
    if [ -z "$OPENWEBUI_PATH" ] || [ ! -d "$OPENWEBUI_PATH" ]; then
        log_error "Путь к Open Web UI не найден или недоступен: $OPENWEBUI_PATH"
        exit 1
    fi
    
    # Создание директорий
    log_info "Создание директорий..."
    mkdir -p "$OPENWEBUI_PATH"/{plugins/vfs,static/js,backend/data/vfs/{projects,templates,cache},backend/data/config}
    
    # Копирование файлов
    log_info "Копирование файлов ВФС..."
    cp openwebui_integrated_vfs.js "$OPENWEBUI_PATH"/static/js/
    cp openwebui_vfs_plugin.js "$OPENWEBUI_PATH"/plugins/vfs/
    cp vfs_config.json "$OPENWEBUI_PATH"/backend/data/config/
    
    log_success "ВФС плагин установлен локально"
    log_warning "Перезапустите Open Web UI сервер вручную для применения изменений"
}

# Проверка установки
verify_installation() {
    log_info "Проверка установки..."
    
    case $INSTALL_TYPE in
        "docker")
            # Проверка файлов в контейнере
            if docker exec "$CONTAINER_ID" ls /app/plugins/vfs/openwebui_vfs_plugin.js &>/dev/null; then
                log_success "✅ Файлы плагина найдены"
            else
                log_error "❌ Файлы плагина не найдены"
                return 1
            fi
            
            # Проверка директорий
            if docker exec "$CONTAINER_ID" ls -d /app/backend/data/vfs &>/dev/null; then
                log_success "✅ Директории ВФС созданы"
            else
                log_error "❌ Директории ВФС не созданы"
                return 1
            fi
            ;;
        "systemd"|"local")
            # Проверка файлов
            if [ -f "$OPENWEBUI_PATH/plugins/vfs/openwebui_vfs_plugin.js" ]; then
                log_success "✅ Файлы плагина найдены"
            else
                log_error "❌ Файлы плагина не найдены"
                return 1
            fi
            
            # Проверка директорий
            if [ -d "$OPENWEBUI_PATH/backend/data/vfs" ]; then
                log_success "✅ Директории ВФС созданы"
            else
                log_error "❌ Директории ВФС не созданы"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Показать инструкции по использованию
show_usage_instructions() {
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 ВФС плагин успешно установлен!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "🌐 Откройте Open Web UI в браузере"
    echo "🔍 Проверьте работу командой: /vfs help"
    echo
    echo "📋 Основные команды:"
    echo "  /vfs status                    - статус системы"
    echo "  /project create MyProject      - создать проект"
    echo "  /project list                  - список проектов"
    echo "  /file create MyProject test.py - создать файл"
    echo "  /file read MyProject test.py   - прочитать файл"
    echo "  /vfs stats                     - статистика"
    echo
    echo "🎯 Доступные шаблоны:"
    echo "  - default          (базовый Python проект)"
    echo "  - instagram_parser (парсер Instagram)"
    echo "  - api_client       (REST API клиент)"
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Функция удаления (для отката)
uninstall_vfs() {
    log_info "Удаление ВФС плагина..."
    
    case $INSTALL_TYPE in
        "docker")
            docker exec "$CONTAINER_ID" rm -rf /app/plugins/vfs /app/backend/data/vfs
            docker exec "$CONTAINER_ID" rm -f /app/static/js/openwebui_integrated_vfs.js /app/frontend/static/js/openwebui_integrated_vfs.js
            docker exec "$CONTAINER_ID" rm -f /app/backend/data/config/vfs_config.json
            docker restart "$CONTAINER_ID"
            ;;
        "systemd"|"local")
            sudo rm -rf "$OPENWEBUI_PATH"/plugins/vfs "$OPENWEBUI_PATH"/backend/data/vfs
            sudo rm -f "$OPENWEBUI_PATH"/static/js/openwebui_integrated_vfs.js
            sudo rm -f "$OPENWEBUI_PATH"/backend/data/config/vfs_config.json
            if [ "$INSTALL_TYPE" = "systemd" ]; then
                sudo systemctl restart open-web-ui
            fi
            ;;
    esac
    
    log_success "ВФС плагин удален"
}

# Справка
show_help() {
    echo "Установка ВФС плагина для Open Web UI"
    echo
    echo "Использование: $0 [КОМАНДА]"
    echo
    echo "Команды:"
    echo "  install   - установить ВФС плагин (по умолчанию)"
    echo "  uninstall - удалить ВФС плагин"
    echo "  check     - проверить установку"
    echo "  help      - показать эту справку"
    echo
    echo "Примеры:"
    echo "  $0                 # автоматическая установка"
    echo "  $0 install         # явная установка"
    echo "  $0 uninstall       # удаление плагина"
    echo "  $0 check           # проверка установки"
    echo
}

# Главная функция
main() {
    local command=${1:-install}
    
    echo "🚀 Установщик ВФС плагина v$VFS_VERSION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case $command in
        "install")
            detect_installation
            check_files
            
            case $INSTALL_TYPE in
                "docker")
                    install_docker
                    ;;
                "systemd")
                    install_systemd
                    ;;
                "local")
                    install_local
                    ;;
                *)
                    log_error "Неизвестный тип установки: $INSTALL_TYPE"
                    exit 1
                    ;;
            esac
            
            if verify_installation; then
                show_usage_instructions
            else
                log_error "Установка завершилась с ошибками"
                exit 1
            fi
            ;;
        "uninstall")
            detect_installation
            uninstall_vfs
            ;;
        "check")
            detect_installation
            if verify_installation; then
                log_success "ВФС плагин установлен и работает"
            else
                log_error "ВФС плагин не установлен или работает некорректно"
                exit 1
            fi
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Неизвестная команда: $command"
            show_help
            exit 1
            ;;
    esac
}

# Обработка прерывания
trap 'log_warning "Установка прервана пользователем"; exit 130' INT

# Запуск
main "$@" 