#!/usr/bin/env python3
"""
ELEN-T Security Sensor
======================
سنسور فعال امنیتی که هر درخواست را در زمان واقعی تحلیل می‌کند.
"""

import os
import re
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class SecuritySensor:
    """سنسور تحلیل درخواست‌ها و تشخیص حملات"""

    def __init__(self):
        self.state_dir = Path.home() / ".elen_security"
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / "state.json"

        # الگوهای حمله (Regex)
        self.patterns = {
            'sql_injection': re.compile(
                r"(\b(union|select|insert|drop|exec|delete)\b.*\b(from|into|where)\b)",
                re.IGNORECASE
            ),
            'xss': re.compile(
                r"(<script|javascript:|onerror=|onload=|<iframe)",
                re.IGNORECASE
            ),
            'path_traversal': re.compile(
                r"(\.\./|\.\.\\|%2e%2e|%252e)",
                re.IGNORECASE
            ),
            'command_injection': re.compile(
                r"(;|\||&&|\$\(|`).*(rm|cat|wget|curl|nc|bash)",
                re.IGNORECASE
            ),
            'scanner': re.compile(
                r"(nikto|sqlmap|nmap|masscan|burp|acunetix|nessus)",
                re.IGNORECASE
            ),
        }

        # مسیرهای Honeypot (هر کسی این‌ها را امتحان کند، مهاجم است)
        self.honeypot_paths = [
            '/admin', '/wp-admin', '/wp-login', '/.env', '/.git',
            '/config', '/backup', '/phpmyadmin', '/api/secret',
            '/.htaccess', '/server-status', '/actuator', '/console'
        ]

        # حافظه درون‌فرآیندی
        self.request_history = defaultdict(list)
        self.auth_failures = defaultdict(int)

        # بارگذاری وضعیت قبلی
        self.state = self._load_state()

    def _load_state(self):
        """بارگذاری ایمن وضعیت از فایل"""
        default_state = {
            'level': 0,
            'blacklist': {},
            'events': [],
            'last_updated': None
        }
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # اطمینان از وجود کلیدهای ضروری
                    for key in default_state:
                        if key not in loaded:
                            loaded[key] = default_state[key]
                    return loaded
        except Exception:
            pass
        return default_state

    def _save_state(self):
        """ذخیره اتمیک وضعیت (safe from corruption)"""
        try:
            self.state['last_updated'] = datetime.now().isoformat()
            tmp_file = str(self.state_file) + ".tmp"
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            os.replace(tmp_file, self.state_file)
        except Exception as e:
            print(f"⚠️ خطا در ذخیره وضعیت: {e}")

    def analyze(self, ip, path, body=""):
        """تحلیل یک درخواست و بازگرداندن لیست سیگنال‌ها"""
        signals = []
        now = time.time()

        text = f"{path} {body}"

        # ۱. بررسی الگوهای حمله
        for name, pattern in self.patterns.items():
            if pattern.search(text):
                signals.append({
                    'type': name,
                    'severity': 8,
                    'detail': f'الگوی {name} در درخواست'
                })

        # ۲. بررسی Honeypot
        path_lower = path.lower()
        for trap in self.honeypot_paths:
            if trap in path_lower:
                signals.append({
                    'type': 'honeypot_probe',
                    'severity': 7,
                    'detail': f'تلاش برای دسترسی به {trap}'
                })
                break

        # ۳. نرخ درخواست (۵ دقیقه اخیر)
        window = 300
        self.request_history[ip] = [
            t for t in self.request_history[ip] if now - t < window
        ]
        self.request_history[ip].append(now)
        rate = len(self.request_history[ip])

        if rate > 100:
            signals.append({
                'type': 'rate_burst',
                'severity': 9,
                'detail': f'نرخ غیرعادی: {rate} درخواست در ۵ دقیقه'
            })
        elif rate > 30:
            signals.append({
                'type': 'rate_high',
                'severity': 5,
                'detail': f'نرخ بالا: {rate} درخواست در ۵ دقیقه'
            })

        # ۴. بررسی blacklist
        if ip in self.state.get('blacklist', {}):
            signals.append({
                'type': 'blacklisted',
                'severity': 10,
                'detail': f'IP در blacklist: {ip}'
            })

        return signals

    def record_auth_failure(self, ip):
        """ثبت شکست احراز هویت"""
        self.auth_failures[ip] += 1
        count = self.auth_failures[ip]
        if count >= 5:
            return {
                'type': 'auth_bruteforce',
                'severity': 8,
                'detail': f'{count} شکست احراز هویت متوالی'
            }
        return None

    def update(self, signals):
        """به‌روزرسانی وضعیت بر اساس سیگنال‌ها"""
        if not signals:
            return self.state['level']

        max_severity = max(s['severity'] for s in signals)
        now = datetime.now().isoformat()

        # ثبت رویدادها
        for s in signals:
            self.state['events'].append({
                'time': now,
                'type': s['type'],
                'severity': s['severity'],
                'detail': s.get('detail', '')
            })
        # فقط ۵۰۰ رویداد آخر
        self.state['events'] = self.state['events'][-500:]

        # به‌روزرسانی سطح
        if max_severity >= 10:
            self.state['level'] = 3
        elif max_severity >= 8:
            self.state['level'] = max(self.state['level'], 2)
        elif max_severity >= 5:
            self.state['level'] = max(self.state['level'], 1)

        self._save_state()
        return self.state['level']

    def add_to_blacklist(self, ip, duration=86400):
        """افزودن IP به blacklist (پیش‌فرض: ۲۴ ساعت)"""
        self.state['blacklist'][ip] = time.time() + duration
        self._save_state()

    def clean_expired_blacklist(self):
        """پاکسازی blacklist منقضی‌شده"""
        now = time.time()
        expired = [ip for ip, exp in self.state['blacklist'].items() if exp < now]
        for ip in expired:
            del self.state['blacklist'][ip]
        if expired:
            self._save_state()

    def get_status(self):
        """دریافت وضعیت فعلی برای نمایش"""
        levels = {0: "عادی", 1: "هشدار", 2: "سایه", 3: "قفل کامل"}
        return {
            'level': self.state['level'],
            'level_name': levels.get(self.state['level'], 'نامشخص'),
            'blacklist_count': len(self.state['blacklist']),
            'event_count': len(self.state['events']),
            'last_updated': self.state.get('last_updated')
        }


# ==========================================
# تست خودکار
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 تست سنسور امنیتی")
    print("=" * 60)

    sensor = SecuritySensor()

    # تست ۱: درخواست عادی
    print("\n[تست ۱] درخواست عادی:")
    signals = sensor.analyze("192.168.1.1", "/discover", '{"data": "normal"}')
    print(f"  سیگنال‌ها: {len(signals)}")

    # تست ۲: SQL Injection
    print("\n[تست ۲] تلاش SQL Injection:")
    signals = sensor.analyze("192.168.1.2", "/discover", "UNION SELECT * FROM users")
    print(f"  سیگنال‌ها: {len(signals)}")
    for s in signals:
        print(f"    - {s['type']} (شدت {s['severity']}): {s['detail']}")

    # تست ۳: Honeypot
    print("\n[تست ۳] تلاش دسترسی به /admin:")
    signals = sensor.analyze("192.168.1.3", "/admin", "")
    print(f"  سیگنال‌ها: {len(signals)}")
    for s in signals:
        print(f"    - {s['type']} (شدت {s['severity']}): {s['detail']}")

    # تست ۴: XSS
    print("\n[تست ۴] تلاش XSS:")
    signals = sensor.analyze("192.168.1.4", "/submit", "<script>alert('xss')</script>")
    print(f"  سیگنال‌ها: {len(signals)}")
    for s in signals:
        print(f"    - {s['type']} (شدت {s['severity']}): {s['detail']}")

    # تست ۵: نرخ بالا
    print("\n[تست ۵] نرخ بالا (۳۵ درخواست):")
    for _ in range(35):
        sensor.analyze("192.168.1.5", "/ping", "")
    signals = sensor.analyze("192.168.1.5", "/ping", "")
    for s in signals:
        if 'rate' in s['type']:
            print(f"    - {s['type']} (شدت {s['severity']}): {s['detail']}")

    # تست ۶: Bruteforce
    print("\n[تست ۶] Bruteforce (۵ شکست):")
    for i in range(5):
        signal = sensor.record_auth_failure("192.168.1.6")
        if signal:
            print(f"    - {signal['type']} (شدت {signal['severity']}): {signal['detail']}")

    # وضعیت نهایی
    print("\n" + "=" * 60)
    print("📊 وضعیت نهایی سیستم:")
    status = sensor.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    print("=" * 60)
