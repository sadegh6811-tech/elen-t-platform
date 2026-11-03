from pathlib import Path

engine_file = Path.home() / "Nazi" / "security_engine.py"
content = engine_file.read_text(encoding='utf-8')

old_get_status = '''    def get_status(self):
        """دریافت وضعیت فعلی"""
        levels = {0: "عادی", 1: "هشدار", 2: "سایه", 3: "قفل کامل"}
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                level = state.get('level', 0)
                return {
                    'level': level,
                    'level_name': levels.get(level, 'نامشخص'),
                    'lockdown_active': self.lockdown_flag.exists(),
                    'shadow_active': self.shadow_flag.exists(),
                    'last_updated': state.get('last_updated'),
                }
        except Exception:
            pass
        return {'level': 0, 'level_name': 'عادی', 'lockdown_active': False,
                'shadow_active': False, 'last_updated': None}'''

new_get_status = '''    def get_status(self):
        """دریافت وضعیت فعلی (مستقل از state.json)"""
        levels = {0: "عادی", 1: "هشدار", 2: "سایه", 3: "قفل کامل"}

        # اول پرچم‌ها را چک کن (مهم‌ترین منبع حقیقت)
        lockdown_active = self.lockdown_flag.exists()
        shadow_active = self.shadow_flag.exists()

        # تعیین سطح بر اساس پرچم‌ها
        if lockdown_active:
            level = 3
        elif shadow_active:
            level = 2
        else:
            level = 0

        # تلاش برای خواندن state.json (اگر وجود دارد)
        last_updated = None
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                level = max(level, state.get('level', 0))
                last_updated = state.get('last_updated')
        except Exception:
            pass

        return {
            'level': level,
            'level_name': levels.get(level, 'نامشخص'),
            'lockdown_active': lockdown_active,
            'shadow_active': shadow_active,
            'last_updated': last_updated,
        }'''

if old_get_status in content:
    content = content.replace(old_get_status, new_get_status)
    engine_file.write_text(content, encoding='utf-8')
    print("✅ get_status اصلاح شد.")
else:
    print("⚠️ الگوی قدیمی پیدا نشد. لطفاً دستی بررسی کنید.")
