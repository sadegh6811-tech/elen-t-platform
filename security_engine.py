#!/usr/bin/env python3
"""
ELEN-T Security Engine
======================
موتور تصمیم‌گیری امنیتی که بر اساس سیگنال‌های سنسور،
سطح واکنش مناسب را تعیین و اجرا می‌کند.
"""

import os
import sys
import time
import json
import signal
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime


class SecurityEngine:
    """موتور تصمیم‌گیری و اجرای واکنش‌های امنیتی"""

    def __init__(self):
        self.state_dir = Path.home() / ".elen_security"
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / "state.json"
        self.lockdown_flag = self.state_dir / "lockdown.flag"
        self.shadow_flag = self.state_dir / "shadow.flag"
        self.core_pid_file = self.state_dir / "core.pid"
        self.vault_script = Path.home() / "Nazi" / "shadow_vault.py"

        # تنظیمات تلگرام (اختیاری)
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat = os.environ.get("TELEGRAM_CHAT_ID", "")

        # مسیر هسته اصلی
        self.core_script = Path.home() / "Nazi" / "shadow_core.py"

    # ==========================================
    # واکنش‌های اصلی
    # ==========================================

    def respond(self, level, reason=""):
        """واکنش به سطح امنیتی مشخص"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if level == 0:
            self._log(f"[{timestamp}] ✅ سطح ۰: عملیات عادی")
            # پاکسازی پرچم‌های قبلی
            for flag in [self.lockdown_flag, self.shadow_flag]:
                if flag.exists():
                    flag.unlink()
                    self._log(f"[{timestamp}] 🔄 پرچم {flag.name} پاک شد")

        elif level == 1:
            self._log(f"[{timestamp}] ⚠️ سطح ۱: هشدار - {reason}")
            self._send_telegram(f"⚠️ هشدار امنیتی\n{reason}")

        elif level == 2:
            self._log(f"[{timestamp}] 🌑 سطح ۲: ورود به حالت سایه - {reason}")
            self._trigger_shadow_mode(reason)
            self._send_telegram(f"🌑 حالت سایه فعال شد\nدلیل: {reason}")

        elif level == 3:
            self._log(f"[{timestamp}] 🚨 سطح ۳: قفل کامل - {reason}")
            self._trigger_lockdown(reason)
            self._send_telegram(f"🚨 قفل کامل فعال شد!\nدلیل: {reason}")

        else:
            self._log(f"[{timestamp}] ❓ سطح ناشناخته: {level}")

    # ==========================================
    # حالت سایه (Shadow Mode)
    # ==========================================

    def _trigger_shadow_mode(self, reason):
        """فعال‌سازی حالت سایه: هسته اصلی پنهان می‌شود"""
        try:
            # نوشتن پرچم سایه
            with open(self.shadow_flag, 'w', encoding='utf-8') as f:
                json.dump({
                    'time': time.time(),
                    'reason': reason,
                    'date': datetime.now().isoformat()
                }, f, ensure_ascii=False)

            self._log("🌑 پرچم سایه نوشته شد. درخواست‌ها از این پس به honeypot می‌روند.")

            # اختیاری: متوقف کردن هسته اصلی (اگر بخواهید)
            # self._stop_core_gracefully()

        except Exception as e:
            self._log(f"❌ خطا در فعال‌سازی حالت سایه: {e}")

    # ==========================================
    # قفل کامل (Full Lockdown)
    # ==========================================

    def _trigger_lockdown(self, reason):
        """قفل کامل: کشتن هسته + رمزنگاری گاوصندوق"""
        try:
            # ۱. نوشتن پرچم قفل
            with open(self.lockdown_flag, 'w', encoding='utf-8') as f:
                json.dump({
                    'time': time.time(),
                    'reason': reason,
                    'date': datetime.now().isoformat()
                }, f, ensure_ascii=False)
            self._log("🚨 پرچم قفل نوشته شد.")

            # ۲. کشتن هسته اصلی
            self._stop_core()

            # ۳. رمزنگاری گاوصندوق (اگر وجود داشته باشد)
            if self.vault_script.exists():
                self._encrypt_vault()
            else:
                self._log(f"⚠️ اسکریپت گاوصندوق پیدا نشد: {self.vault_script}")

            # ۴. فعال کردن حالت سایه هم (به عنوان لایه دوم)
            self._trigger_shadow_mode(f"lockdown: {reason}")

            self._log("🔒 قفل کامل با موفقیت اجرا شد.")

        except Exception as e:
            self._log(f"❌ خطا در قفل کامل: {e}")

    def _stop_core(self):
        """کشتن فرآیند هسته اصلی"""
        try:
            # روش ۱: با PID فایل
            if self.core_pid_file.exists():
                with open(self.core_pid_file) as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, signal.SIGTERM)
                    self._log(f"💀 هسته با PID {pid} کشته شد (SIGTERM)")
                    time.sleep(0.5)
                    # اگر هنوز زنده بود، SIGKILL
                    try:
                        os.kill(pid, 0)
                        os.kill(pid, signal.SIGKILL)
                        self._log(f"💀 هسته با SIGKILL کشته شد")
                    except OSError:
                        pass  # قبلاً مرده
                except ProcessLookupError:
                    self._log(f"⚠️ فرآیند {pid} وجود ندارد")

            # روش ۲: با pkill (به عنوان پشتیبان)
            result = subprocess.run(
                ["pkill", "-f", "shadow_core.py"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self._log("💀 pkill موفق بود (فرآیندهای باقیمانده)")

        except Exception as e:
            self._log(f"❌ خطا در کشتن هسته: {e}")

    def _encrypt_vault(self):
        """اجرای رمزنگاری گاوصندوق"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.vault_script), "lock"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self._log(f"🔒 گاوصندوق رمزنگاری شد")
                if result.stdout:
                    self._log(f"   {result.stdout.strip()}")
            else:
                self._log(f"❌ خطا در رمزنگاری: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            self._log("❌ رمزنگاری بیش از ۳۰ ثانیه طول کشید")
        except Exception as e:
            self._log(f"❌ خطا در اجرای گاوصندوق: {e}")

    # ==========================================
    # بازگشت به حالت عادی (Manual Recovery)
    # ==========================================

    def recover(self):
        """بازگشت دستی به حالت عادی (فقط ادمین)"""
        self._log("🔓 در حال بازگشت به حالت عادی...")

        # ۱. حذف پرچم‌ها
        for flag in [self.lockdown_flag, self.shadow_flag]:
            if flag.exists():
                flag.unlink()
                self._log(f"🔄 پرچم {flag.name} حذف شد")

        # ۲. رمزگشایی گاوصندوق
        if self.vault_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(self.vault_script), "unlock"],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    self._log("🔓 گاوصندوق رمزگشایی شد")
                else:
                    self._log(f"❌ خطا در رمزگشایی: {result.stderr}")
            except Exception as e:
                self._log(f"❌ خطا: {e}")

        # ۳. بازنشانی وضعیت
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                state['level'] = 0
                state['last_updated'] = datetime.now().isoformat()
                with open(self.state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                self._log("✅ وضعیت به سطح ۰ بازگشت")
        except Exception as e:
            self._log(f"❌ خطا در بازنشانی وضعیت: {e}")

        self._log("🔓 بازیابی کامل شد. حالا هسته را دستی روشن کنید:")
        self._log(f"   cd ~/Nazi && python3 shadow_core.py")

    # ==========================================
    # اطلاع‌رسانی
    # ==========================================

    def _send_telegram(self, message):
        """ارسال هشدار به تلگرام (اگر تنظیم شده باشد)"""
        if not self.telegram_token or not self.telegram_chat:
            return  # تلگرام تنظیم نشده، نادیده بگیر

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML'
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    self._log("📱 هشدار تلگرام ارسال شد")
        except Exception as e:
            self._log(f"⚠️ خطا در ارسال تلگرام: {e}")

    # ==========================================
    # لاگ‌گیری
    # ==========================================

    def _log(self, message):
        """لاگ هم به فایل و هم به stdout"""
        print(message)
        try:
            log_file = self.state_dir / "engine.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception:
            pass

    # ==========================================
    # وضعیت
    # ==========================================

    def get_status(self):
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
        }


# ==========================================
# تست خودکار
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 تست موتور تصمیم‌گیری امنیتی")
    print("=" * 60)

    engine = SecurityEngine()

    # تست ۱: وضعیت اولیه
    print("\n[تست ۱] وضعیت اولیه:")
    status = engine.get_status()
    print(f"  سطح: {status['level']} ({status['level_name']})")
    print(f"  قفل: {status['lockdown_active']}")
    print(f"  سایه: {status['shadow_active']}")

    # تست ۲: سطح ۱ (هشدار)
    print("\n[تست ۲] سطح ۱ (هشدار):")
    engine.respond(1, "تست هشدار - نرخ بالا")

    # تست ۳: سطح ۲ (سایه)
    print("\n[تست ۳] سطح ۲ (سایه):")
    engine.respond(2, "تست سایه - الگوی حمله")
    status = engine.get_status()
    print(f"  سایه فعال: {status['shadow_active']}")

    # تست ۴: سطح ۳ (قفل کامل)
    print("\n[تست ۴] سطح ۳ (قفل کامل):")
    engine.respond(3, "تست قفل - حمله جدی")

    # تست ۵: بررسی پرچم‌ها
    print("\n[تست ۵] بررسی پرچم‌ها:")
    print(f"  lockdown.flag: {engine.lockdown_flag.exists()}")
    print(f"  shadow.flag: {engine.shadow_flag.exists()}")

    if engine.lockdown_flag.exists():
        with open(engine.lockdown_flag) as f:
            content = json.load(f)
        print(f"  محتوا: {content}")

    # تست ۶: بازیابی
    print("\n[تست ۶] بازیابی به حالت عادی:")
    engine.recover()

    print("\n" + "=" * 60)
    print("✅ تست کامل شد")
    print("=" * 60)
    print("\n📋 خلاصه:")
    print("  - موتور تصمیم ساخته شد")
    print("  - ۴ سطح واکنش کار می‌کند")
    print("  - پرچم‌ها در ~/.elen_security/ ذخیره می‌شوند")
    print("  - هشدار تلگرام (اگر تنظیم شود) ارسال می‌شود")
    print("=" * 60)
