
# Інструкції для налаштування Open WebUI з ISKALA

## 1. Доступ до Open WebUI
Відкрийте браузер і перейдіть до: http://localhost:3000

## 2. Налаштування моделей
1. Увійдіть в Open WebUI
2. Перейдіть до Settings -> Models
3. Додайте нові моделі:

### ISKALA MOVA v2
- Provider: Custom
- Base URL: http://localhost:8001
- Model Name: iskala-mova-v2
- API Key: (залиште порожнім)

### ISKALA RAG
- Provider: Custom  
- Base URL: http://localhost:8001
- Model Name: iskala-rag
- API Key: (залиште порожнім)

### ISKALA Translation
- Provider: Custom
- Base URL: http://localhost:8001
- Model Name: iskala-translation
- API Key: (залиште порожнім)

## 3. Налаштування API Endpoints
Додайте наступні endpoints:

### Chat Endpoint
- URL: http://localhost:8001/api/openwebui/chat
- Method: POST
- Headers: Content-Type: application/json

### Models Endpoint
- URL: http://localhost:8001/api/openwebui/models
- Method: GET

### Status Endpoint
- URL: http://localhost:8001/api/openwebui/status
- Method: GET

## 4. Тестування
1. Виберіть модель "ISKALA MOVA v2"
2. Надішліть повідомлення: "Привіт, як справи?"
3. Перевірте відповідь

## 5. Додаткові можливості
- RAG система: http://localhost:8001/api/memory/search
- Інструменти: http://localhost:8001/api/tools
- WebSocket: ws://localhost:8001/ws

## 6. Інтеграційний інтерфейс
Відкрийте: openwebui_integration/iskala_openwebui_integration.html

---
Згенеровано автоматично: 2025-07-31 19:14:57
