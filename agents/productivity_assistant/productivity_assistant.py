#!/usr/bin/env python3
"""
Агент-асистент продуктивності за системою Алі Абдаала
Реалізує 9-крокову систему продуктивності з гейміфікацією та енергетичним менеджментом
"""

import json
import os
from datetime import datetime, timedelta
import uuid

class ProductivityAssistant:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.data_dir = f"/a0/instruments/custom/iskala/agents/productivity_assistant/data/{user_id}"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.goals_file = f"{self.data_dir}/goals.json"
        self.weekly_plans_file = f"{self.data_dir}/weekly_plans.json"
        self.daily_intentions_file = f"{self.data_dir}/daily_intentions.json"
        self.energy_ledger_file = f"{self.data_dir}/energy_ledger.json"
        self.reflections_file = f"{self.data_dir}/reflections.json"
        
        self.load_data()
    
    def load_data(self):
        """Завантажити всі дані користувача"""
        self.goals = self._load_json(self.goals_file, {"long_term": [], "mid_term": [], "short_term": []})
        self.weekly_plans = self._load_json(self.weekly_plans_file, [])
        self.daily_intentions = self._load_json(self.daily_intentions_file, [])
        self.energy_ledger = self._load_json(self.energy_ledger_file, {"activities": [], "energy_balance": {}})
        self.reflections = self._load_json(self.reflections_file, [])
    
    def _load_json(self, filepath, default):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default
    
    def _save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def set_goal(self, goal_type, description, timeframe, why_important):
        """Встановити ціль на один з трьох горизонтів"""
        goal = {
            "id": str(uuid.uuid4()),
            "description": description,
            "timeframe": timeframe,
            "why_important": why_important,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.goals[goal_type].append(goal)
        self._save_json(self.goals_file, self.goals)
        return f"✅ Ціль додано: {description}"
    
    def set_daily_intention(self, date, main_priority, energy_level, focus_blocks):
        """Встановити щоденний намір і пріоритет"""
        intention = {
            "date": date,
            "main_priority": main_priority,
            "energy_level": energy_level,
            "focus_blocks": focus_blocks,
            "completed": False,
            "reflection": None,
            "created_at": datetime.now().isoformat()
        }
        
        self.daily_intentions.append(intention)
        self._save_json(self.daily_intentions_file, self.daily_intentions)
        return f"✅ Щоденний намір встановлено: {main_priority}"
    
    def track_energy(self, activity, energy_change, notes=""):
        """Відстежити зміну енергії від активності"""
        entry = {
            "activity": activity,
            "energy_change": energy_change,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.energy_ledger["activities"].append(entry)
        self._save_json(self.energy_ledger_file, self.energy_ledger)
        return f"✅ Енергія зафіксована: {activity} ({energy_change:+d})"
    
    def daily_reflection(self, date, wins, challenges, energy_level, tomorrow_focus):
        """Провести вечірню рефлексію"""
        reflection = {
            "date": date,
            "wins": wins,
            "challenges": challenges,
            "energy_level": energy_level,
            "tomorrow_focus": tomorrow_focus,
            "timestamp": datetime.now().isoformat()
        }
        
        self.reflections.append(reflection)
        self._save_json(self.reflections_file, self.reflections)
        
        # Update daily intention as completed
        for intention in self.daily_intentions:
            if intention["date"] == date:
                intention["completed"] = True
                intention["reflection"] = reflection
        
        self._save_json(self.daily_intentions_file, self.daily_intentions)
        return "✅ Щоденна рефлексія збережена"
    
    def get_progress_report(self, period="week"):
        """Отримати звіт про прогрес"""
        today = datetime.now()
        
        if period == "week":
            start_date = today - timedelta(days=7)
        elif period == "month":
            start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=7)
        
        # Calculate completion rate
        recent_intentions = [i for i in self.daily_intentions 
                           if datetime.fromisoformat(i["date"]) >= start_date]
        
        if recent_intentions:
            completion_rate = sum(1 for i in recent_intentions if i["completed"]) / len(recent_intentions) * 100
        else:
            completion_rate = 0
        
        # Energy analysis
        recent_energy = [e for e in self.energy_ledger["activities"] 
                        if datetime.fromisoformat(e["timestamp"]) >= start_date]
        
        energy_balance = sum(e["energy_change"] for e in recent_energy)
        
        report = {
            "period": period,
            "completion_rate": round(completion_rate, 1),
            "energy_balance": energy_balance,
            "total_intentions": len(recent_intentions),
            "active_goals": len(self.goals["long_term"]) + len(self.goals["mid_term"]) + len(self.goals["short_term"]),
            "generated_at": today.isoformat()
        }
        
        return report

# CLI Interface
if __name__ == "__main__":
    assistant = ProductivityAssistant()
    
    print("🎯 Агент продуктивності активовано!")
    print("Команди:")
    print("/start_day - почати планування дня")
    print("/weekly_review - щотижневий огляд")
    print("/energy_check - перевірити енергію")
    print("/progress_report - звіт про прогрес")
