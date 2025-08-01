# 📋 Формат внутрішнього самозвіту LLM у стилі MOVA

## 🔄 Структура відповіді:

```json
{
  "mova_interpretation": {
    "intent_type": "string (наприклад, 'emotional_discharge')",
    "thinking_phase": "string (наприклад, 'naming')",
    "awareness_level": "low / medium / high",
    "depth_score": "float (0.0–1.0)",
    "response_behavior": "mirror / structure / act / enhance / hold",
    "temperature": "float (0.2–1.0)",
    "frames_used": [
      "усвідомлення наміру",
      "оцінка глибини",
      "емпатичне позиціонування"
    ]
  },
  "system_decision": {
    "reasoning_summary": "Коротке пояснення, чому обрано саме таку відповідь",
    "final_prompt_used": "Промпт, сформований для відповіді",
    "mode": "reflective / directive / explorative"
  },
  "response": "Згенерована відповідь, яка ґрунтується на всьому вищезазначеному"
}
```

## 📊 Пояснення полів:

### `mova_interpretation`:
- **intent_type**: Тип наміру користувача
- **thinking_phase**: Фаза мислення (сприйняття, плутанина, називання, дія)
- **awareness_level**: Рівень усвідомлення (низький/середній/високий)
- **depth_score**: Глибина запиту (0.0-1.0)
- **response_behavior**: Стиль відповіді
- **temperature**: Креативність відповіді
- **frames_used**: Використані фрейми мислення

### `system_decision`:
- **reasoning_summary**: Пояснення логіки рішення
- **final_prompt_used**: Фінальний промпт для генерації
- **mode**: Режим роботи (рефлексивний/директивний/дослідницький)

### `response`: Фінальна відповідь користувачу 