# 🎯 Быстрая демонстрация ВФС в Open Web UI

## 🚀 Команды для копирования и вставки

### 1. Проверка статуса системы
```
/vfs status
```

### 2. Создание проекта Instagram Parser
```
/project create InstagramParser instagram_parser
```

### 3. Просмотр созданных файлов
```
/file list InstagramParser
```

### 4. Чтение основного файла парсера
```
/file read InstagramParser instagram_parser.py
```

### 5. Создание дополнительного файла
```
/file create InstagramParser bot_runner.py "
from instagram_parser import InstagramParser
import json
import time

def main():
    parser = InstagramParser()
    
    # Тестовые пользователи для парсинга
    test_users = ['test_user1', 'test_user2']
    
    results = []
    for username in test_users:
        print(f'🔍 Парсинг пользователя: {username}')
        
        # Получаем информацию о пользователе
        user_info = parser.get_user_info(username)
        results.append(user_info)
        
        # Получаем посты
        posts = parser.parse_posts(username, limit=5)
        user_info['posts'] = posts
        
        # Задержка между запросами
        time.sleep(2)
    
    # Сохраняем результаты
    output_file = f'results_{int(time.time())}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'✅ Результаты сохранены в {output_file}')
    print(f'📊 Обработано пользователей: {len(results)}')
    
    return results

if __name__ == '__main__':
    main()
"
```

### 6. Обновление конфигурации
```
/file update InstagramParser config.json "{
    \"instagram\": {
        \"delay_between_requests\": 3,
        \"max_retries\": 5,
        \"timeout\": 45,
        \"save_images\": false,
        \"output_format\": \"json\"
    },
    \"bot\": {
        \"max_users_per_session\": 10,
        \"auto_save_results\": true,
        \"log_level\": \"INFO\"
    },
    \"proxy\": {
        \"enabled\": false,
        \"http_proxy\": null,
        \"https_proxy\": null
    }
}"
```

### 7. Создание второго проекта - API клиент
```
/project create APIClient api_client
```

### 8. Настройка API клиента для реального сервиса
```
/file update APIClient api_client.py "
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class FacebookAPIClient:
    '''Клиент для работы с Facebook Graph API'''
    
    def __init__(self, access_token: str):
        self.base_url = 'https://graph.facebook.com/v18.0'
        self.access_token = access_token
        self.session = requests.Session()
        
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
    
    def get_user_info(self, user_id: str = 'me') -> Dict:
        '''Получить информацию о пользователе'''
        url = f'{self.base_url}/{user_id}'
        params = {
            'fields': 'id,name,email,picture',
            'access_token': self.access_token
        }
        
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def get_user_posts(self, user_id: str = 'me', limit: int = 10) -> List[Dict]:
        '''Получить посты пользователя'''
        url = f'{self.base_url}/{user_id}/posts'
        params = {
            'limit': limit,
            'fields': 'id,message,created_time,likes.summary(true)',
            'access_token': self.access_token
        }
        
        response = self.session.get(url, params=params)
        data = self._handle_response(response)
        return data.get('data', [])
    
    def _handle_response(self, response) -> Dict:
        '''Обработка ответа API'''
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }

# Пример использования
if __name__ == '__main__':
    # Замените на ваш токен доступа
    api = FacebookAPIClient('YOUR_ACCESS_TOKEN_HERE')
    
    # Получаем информацию о текущем пользователе
    user_info = api.get_user_info()
    print('👤 Информация о пользователе:')
    print(json.dumps(user_info, indent=2, ensure_ascii=False))
    
    # Получаем последние посты
    posts = api.get_user_posts(limit=5)
    print(f'📄 Найдено постов: {len(posts)}')
    for post in posts:
        print(f'  📝 {post.get(\"id\")}: {post.get(\"message\", \"Без текста\")[:50]}...')
"
```

### 9. Создание универсального проекта
```
/project create DataProcessor default
```

### 10. Добавление обработчика данных
```
/file create DataProcessor data_processor.py "
import json
import csv
from typing import List, Dict, Any
from datetime import datetime
import os

class UniversalDataProcessor:
    '''Универсальный обработчик данных для различных форматов'''
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        '''Создать директорию для вывода если не существует'''
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def process_instagram_data(self, data_file: str) -> Dict[str, Any]:
        '''Обработка данных Instagram'''
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed = {
            'summary': {
                'total_users': len(data),
                'total_posts': sum(len(user.get('posts', [])) for user in data),
                'processed_at': datetime.now().isoformat()
            },
            'users': []
        }
        
        for user in data:
            user_summary = {
                'username': user.get('username'),
                'posts_count': len(user.get('posts', [])),
                'total_likes': sum(post.get('likes', 0) for post in user.get('posts', [])),
                'status': user.get('status', 'unknown')
            }
            processed['users'].append(user_summary)
        
        # Сохраняем обработанные данные
        output_file = os.path.join(self.output_dir, f'instagram_processed_{int(datetime.now().timestamp())}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        
        print(f'✅ Instagram данные обработаны: {output_file}')
        return processed
    
    def export_to_csv(self, data: List[Dict], filename: str):
        '''Экспорт данных в CSV'''
        if not data:
            print('❌ Нет данных для экспорта')
            return
        
        output_file = os.path.join(self.output_dir, filename)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        print(f'💾 Данные экспортированы в CSV: {output_file}')
        return output_file
    
    def generate_report(self, processed_data: Dict) -> str:
        '''Генерация отчета'''
        report = f'''
# 📊 Отчет по обработке данных

**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Сводка
- **Пользователей:** {processed_data['summary']['total_users']}
- **Постов:** {processed_data['summary']['total_posts']}
- **Средний лайков на пост:** {processed_data['summary']['total_posts'] / max(len(processed_data['users']), 1):.2f}

## Детали по пользователям
'''
        
        for user in processed_data['users']:
            report += f'''
### {user['username']}
- Постов: {user['posts_count']}
- Лайков: {user['total_likes']}
- Статус: {user['status']}
'''
        
        report_file = os.path.join(self.output_dir, f'report_{int(datetime.now().timestamp())}.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f'📋 Отчет сгенерирован: {report_file}')
        return report

if __name__ == '__main__':
    processor = UniversalDataProcessor()
    print('🔄 Процессор данных инициализирован')
    print('📁 Поместите файлы данных в input/ директорию для обработки')
"
```

### 11. Просмотр всех проектов
```
/project list
```

### 12. Переключение между проектами
```
/project switch InstagramParser
```
```
/project info InstagramParser
```

### 13. Статистика всей системы
```
/vfs stats
```

### 14. Экспорт проекта
```
/export InstagramParser json
```

### 15. Сохранение состояния системы
```
/vfs save
```

## 🎯 Результат демонстрации

После выполнения всех команд у вас будет:

1. **3 рабочих проекта:**
   - `InstagramParser` - полнофункциональный парсер Instagram
   - `APIClient` - клиент для Facebook API
   - `DataProcessor` - универсальный обработчик данных

2. **Структурированные файлы:**
   - Python скрипты с рабочим кодом
   - Конфигурационные файлы
   - Файлы зависимостей

3. **Интегрированная система:**
   - Все данные сохранены в Storage API Open Web UI
   - Возможность экспорта/импорта проектов
   - Командный интерфейс для управления

## 🚀 Следующие шаги

1. **Запустите код локально:**
   ```bash
   # Экспортируйте проект и сохраните файлы
   # Установите зависимости: pip install requests beautifulsoup4
   # Запустите: python instagram_parser.py
   ```

2. **Расширьте функциональность:**
   ```
   /file create InstagramParser advanced_features.py "# Ваши дополнения"
   ```

3. **Создайте собственные шаблоны:**
   - Изучите существующие шаблоны
   - Создайте новые под ваши задачи

**🎉 Поздравляем! ВФС готова к продуктивной работе!** 