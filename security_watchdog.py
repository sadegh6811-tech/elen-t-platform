#!/usr/bin/env python3
"""
ELEN-T Security Watchdog
========================
نگهبان مستقل که هر ۲ ثانیه وضعیت را چک می‌کند.
اگر پرچم قفل (lockdown.flag) را دید، فوراً فایل‌ها را رمزنگاری می‌کند.
"""

import os
import time
import signal
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class SecurityWatchdog:
    def __init__(self):
        self.state_dir = Path.home() / ".elen_security"
        self.lockdown_flag = self.state_dir / "lockdown.flag"
        self.shadow_flag = self.state_dir / "shadow.flag"
        self.vault_script = Path.home() / "Nazi" / "shadow_vault.py"
        self.core_script = Path.home() / "Nazi" / "shadow_core.py"
        self.running = True

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        # ذخیره در فایل لاگ
        try:
            log_file = self.state_dir / "watchdog.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except Exception:
            pass

    def handle_lockdown(self):
        """واکنش به پرچم قفل"""
        self.log("🚨 پرچم قفل شناسایی شد! شروع فرآیند Lockdown...")

        # ۱. کشتن هسته اصلی
        try:
            subprocess.run(["pkill", "-f", "shadow_core.py"], check=False)
            self.log("💀 فرآیند هسته کشته شد.")
        except Exception as e:
            self.log(f"⚠️ خطا در کشتن هسته: {e}")

        # ۲. اجرای دستور lock در گاوصندوق
        if self.vault_script.exists():
            try:
                self.log("🔒 در حال رمزنگاری فایل‌ها...")
                result = subprocess.run(
                    [sys.executable, str(self.vault_script), "lock"],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    self.log("✅ فایل‌ها با موفقیت قفل شدند.")
                else:
                    self.log(f"❌ خطا در قفل کردن: {result.stderr}")
            except Exception as e:
                self.log(f"❌ خطا در اجرای گاوصندوق: {e}")

        # ۳. حذف پرچم قفل (تا دوباره اجرا نشود)
        try:
            if self.lockdown_flag.exists():
                self.lockdown_flag.unlink()
                self.log("🔄 پرچم قفل حذف شد (برای جلوگیری از تکرار).")
        except Exception as e:
            self.log(f"⚠️ خطا در حذف پرچم: {e}")

    def run(self):
        self.log("👁️ نگهبان امنیتی فعال شد (بررسی هر ۲ ثانیه).")
        self.log("   برای توقف: Ctrl+C")

        last_state = "normal"

        while self.running:
            try:
                if self.lockdown_flag.exists():
                    if last_state != "lockdown":
                        self.handle_lockdown()
                        last_state = "lockdown"
                elif self.shadow_flag.exists():
                    if last_state != "shadow":
                        self.log("🌑 حالت سایه فعال است. (هسته اصلی پنهان شده)")
                        last_state = "shadow"
                else:
                    if last_state != "normal":
                        self.log("✅ سیستم به حالت عادی بازگشت.")
                        last_state = "normal"

                time.sleep(2)

            except KeyboardInterrupt:
                self.log("👋 نگهبان توسط کاربر متوقف شد.")
                self.running = False
            except Exception as e:
                self.log(f"⚠️ خطای غیرمنتظره: {e}")
                time.sleep(5)

if __name__ == "__main__":
    # مدیریت سیگنال‌ها برای خروج تمیز
    def signal_handler(sig, frame):
        print("\n👋 سیگنال دریافت شد. در حال خروج...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    watchdog = SecurityWatchdog()
    watchdog.run()
