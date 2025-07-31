#!/usr/bin/env python3
"""
Інтерактивний CLI інтерфейс для агента продуктивності
Реалізує всі 9 компонентів системи Алі Абдаала
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from productivity_assistant import ProductivityAssistant
from datetime import datetime, timedelta
import json

class ProductivityCLI:
    def __init__(self):
        self.assistant = ProductivityAssistant()
        self.current_user = "default"
    
    def display_menu(self):
        print("\n" + "="*60)
        print("🎯 АГЕНТ ПРОДУКТИВНОСТІ - СИСТЕМА АЛІ АБДААЛА")
        print("="*60)
        print("1. 🎯 Встановити ціль (3 горизонти)")
        print("2. 📅 Щоденний намір")
        print("3. ⚡ Відстежити енергію")
        print("4. 📝 Вечірня рефлексія")
        print("5. 📊 Звіт про прогрес")
        print("6. 🎮 Створити челлендж")
        print("7. 📋 Переглянути цілі")
        print("8. 🔍 Переглянути енергетичний леджер")
        print("9. 📈 Експорт у Todoist")
        print("0. ❌ Вихід")
        print("="*60)
    
    def set_goal(self):
        print("\n🎯 ВСТАНОВЛЕННЯ ЦІЛІ")
        print("Оберіть горизонт:")
        print("1. Довгострокова (10+ років)")
        print("2. Середньострокова (3-5 років)")
        print("3. Короткострокова (12 місяців)")
        
        choice = input("Ваш вибір (1-3): ").strip()
        goal_types = {"1": "long_term", "2": "mid_term", "3": "short_term"}
        
        if choice not in goal_types:
            print("❌ Невірний вибір")
            return
        
        description = input("Опишіть вашу ціль: ").strip()
        timeframe = input("Конкретний термін: ").strip()
        why_important = input("Чому це важливо для вас: ").strip()
        
        result = self.assistant.set_goal(goal_types[choice], description, timeframe, why_important)
        print(f"\n{result}")
    
    def set_daily_intention(self):
        print("\n📅 ЩОДЕННИЙ НАМІР")
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Дата: {today}")
        
        main_priority = input("Головний пріоритет сьогодні: ").strip()
        energy_level = input("Оцініть свій енергетичний рівень (1-10): ").strip()
        focus_blocks = input("Скільки блоків глибокої роботи плануєте: ").strip()
        
        result = self.assistant.set_daily_intention(today, main_priority, energy_level, focus_blocks)
        print(f"\n{result}")
    
    def track_energy(self):
        print("\n⚡ ВІДСТЕЖЕННЯ ЕНЕРГІЇ")
        activity = input("Яку активність виконували: ").strip()
        
        print("Оцініть вплив на енергію:")
        print("+3 - дуже заряджає")
        print("+2 - заряджає")
        print("+1 - трохи заряджає")
        print("0 - нейтрально")
        print("-1 - трохи виснажує")
        print("-2 - виснажує")
        print("-3 - дуже виснажує")
        
        try:
            energy_change = int(input("Ваш вибір (-3 до +3): ").strip())
            notes = input("Примітки (необов'язково): ").strip()
            
            result = self.assistant.track_energy(activity, energy_change, notes)
            print(f"\n{result}")
        except ValueError:
            print("❌ Будь ласка, введіть число від -3 до +3")
    
    def daily_reflection(self):
        print("\n📝 ВЕЧІРНЯ РЕФЛЕКСІЯ")
        today = datetime.now().strftime("%Y-%m-%d")
        
        wins = input("Що сьогодні вийшло найкраще? ").strip()
        challenges = input("Які були виклики? ").strip()
        
        try:
            energy_level = int(input("Оцініть енергетичний рівень за день (1-10): ").strip())
            tomorrow_focus = input("Головний фокус на завтра: ").strip()
            
            result = self.assistant.daily_reflection(today, wins, challenges, energy_level, tomorrow_focus)
            print(f"\n{result}")
        except ValueError:
            print("❌ Будь ласка, введіть число для енергетичного рівня")
    
    def show_progress(self):
        print("\n📊 ЗВІТ ПРО ПРОГРЕС")
        
        period = input("За який період? (week/month): ").strip().lower()
        if period not in ["week", "month"]:
            period = "week"
        
        report = self.assistant.get_progress_report(period)
        
        print(f"\n📊 Звіт за {period}:")
        print(f"📈 Виконання намірів: {report['completion_rate']}%")
        print(f"⚡ Енергетичний баланс: {report['energy_balance']:+d}")
        print(f"📋 Всього намірів: {report['total_intentions']}")
        print(f"🎯 Активні цілі: {report['active_goals']}")
    
    def view_goals(self):
        print("\n🎯 ВАШІ ЦІЛІ")
        
        for goal_type, goals in self.assistant.goals.items():
            type_names = {
                "long_term": "🌅 Довгострокові (10+ років)",
                "mid_term": "🏔️ Середньострокові (3-5 років)",
                "short_term": "🎯 Короткострокові (12 місяців)"
            }
            
            print(f"\n{type_names[goal_type]}:")
            if not goals:
                print("   (ще немає цілей)")
            else:
                for goal in goals:
                    print(f"   • {goal['description']}")
                    print(f"     Термін: {goal['timeframe']}")
                    print(f"     Причина: {goal['why_important']}")
                    print()
    
    def view_energy_ledger(self):
        print("\n⚡ ЕНЕРГЕТИЧНИЙ ЛЕДЖЕР")
        
        recent_activities = self.assistant.energy_ledger["activities"][-10:]
        if not recent_activities:
            print("   (ще немає записів)")
            return
        
        for activity in reversed(recent_activities):
            timestamp = datetime.fromisoformat(activity["timestamp"]).strftime("%H:%M")
            change = activity["energy_change"]
            symbol = "🔋" if change > 0 else "🔴" if change < 0 else "⚪"
            print(f"   {symbol} {timestamp} - {activity['activity']} ({change:+d})")
            if activity["notes"]:
                print(f"     💭 {activity['notes']}")
    
    def create_challenge(self):
        print("\n🎮 СТВОРЕННЯ ЧЕЛЛЕНДЖУ")
        
        name = input("Назва челленджу: ").strip()
        description = input("Опис: ").strip()
        reward = input("Нагорода за виконання: ").strip()
        
        try:
            duration = int(input("Тривалість (днів): ").strip())
            challenge = self.assistant.create_challenge(name, description, reward, duration)
            
            print(f"\n✅ Челлендж створено!")
            print(f"🎯 {challenge['name']}")
            print(f"📋 {challenge['description']}")
            print(f"🏆 Нагорода: {challenge['reward']}")
            print(f"📅 Тривалість: {challenge['duration_days']} днів")
        except ValueError:
            print("❌ Будь ласка, введіть число для тривалості")
    
    def export_todoist(self):
        print("\n📈 ЕКСПОРТ У TODOIST")
        tasks = self.assistant.export_to_todoist()
        
        if not tasks:
            print("❌ Немає задач для експорту")
            return
        
        filename = f"/tmp/todoist_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Експорт завершено!")
        print(f"📁 Файл збережено: {filename}")
        print(f"📊 Задач експортовано: {len(tasks)}")
    
    def run(self):
        print("🎯 Ласкаво просимо до системи продуктивності Алі Абдаала!")
        
        while True:
            self.display_menu()
            choice = input("Ваш вибір: ").strip()
            
            if choice == "1":
                self.set_goal()
            elif choice == "2":
                self.set_daily_intention()
            elif choice == "3":
                self.track_energy()
            elif choice == "4":
                self.daily_reflection()
            elif choice == "5":
                self.show_progress()
            elif choice == "6":
                self.create_challenge()
            elif choice == "7":
                self.view_goals()
            elif choice == "8":
                self.view_energy_ledger()
            elif choice == "9":
                self.export_todoist()
            elif choice == "0":
                print("👋 До побачення! Продовжуйте будувати свою систему продуктивності!")
                break
            else:
                print("❌ Невірний вибір. Будь ласка, оберіть 0-9.")

if __name__ == "__main__":
    cli = ProductivityCLI()
    cli.run()
