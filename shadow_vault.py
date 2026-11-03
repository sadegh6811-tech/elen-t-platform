#!/usr/bin/env python3
"""
ELEN-T Shadow Vault
===================
گاوصندوق رمزنگاری AES برای فایل‌های حساس پروژه.

دستورات:
  backup   - تهیه نسخه پشتیبان رمزنگاری‌شده (فایل‌های اصلی دست‌نخورده)
  lock     - رمزنگاری فایل‌های اصلی و حذف آن‌ها (Lockdown)
  unlock   - رمزگشایی و بازیابی فایل‌های اصلی
  verify   - بررسی صحت گاوصندوق
  list     - نمایش محتوای گاوصندوق
  restore  - بازیابی از جدیدترین نسخه پشتیبان
  rotate   - چرخش کلید رمزنگاری
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("❌ کتابخانه cryptography نصب نیست.")
    print("   نصب: pip install cryptography")
    sys.exit(1)


CRITICAL_FILES = [
    "v13_core.py",
    "engine_v31.py",
    "discover_all_physics_v13.py",
    "discover_9d_boundary_v41.py",
    "engine_v27_clean.py",
    "lab_1024d_log_space.py",
    "lab_1024d_log_space_unleashed.py",
    "shadow_core.py",
    "public_proxy.py",
]


class ShadowVault:
    def __init__(self):
        self.base_dir = Path.home() / ".elen_vault"
        self.backup_dir = self.base_dir / "backups"
        self.encrypted_dir = self.base_dir / "encrypted"
        self.key_file = self.base_dir / ".master_key"
        self.source_dir = Path.home() / "Nazi"

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.encrypted_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.base_dir, 0o700)
        os.chmod(self.backup_dir, 0o700)
        os.chmod(self.encrypted_dir, 0o700)

    def _ensure_key(self):
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            os.chmod(self.key_file, 0o600)
            print("🔑 کلید جدید ساخته شد.")
            print(f"   مسیر: {self.key_file}")
            print("   ⚠️ این کلید را در جای امن (خارج از گوشی) کپی کنید!")
            return True
        return False

    def _get_fernet(self):
        self._ensure_key()
        return Fernet(self.key_file.read_bytes())

    def backup(self):
        print("=" * 60)
        print("💾 تهیه نسخه پشتیبان")
        print("=" * 60)
        fernet = self._get_fernet()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        metadata = {'timestamp': timestamp, 'files': {}}
        for filename in CRITICAL_FILES:
            src = self.source_dir / filename
            if not src.exists():
                print(f"  ⚠️ {filename} پیدا نشد")
                continue
            data = src.read_bytes()
            encrypted = fernet.encrypt(data)
            (backup_path / (filename + ".enc")).write_bytes(encrypted)
            metadata['files'][filename] = {
                'size': len(data),
                'sha256': hashlib.sha256(data).hexdigest(),
            }
            print(f"  ✅ {filename}")

        (backup_path / "metadata.json").write_text(json.dumps(metadata, indent=2))
        print(f"\n✅ نسخه پشتیبان در {backup_path} ساخته شد")
        print(f"📊 تعداد فایل‌ها: {len(metadata['files'])}")

    def lock(self):
        print("=" * 60)
        print("🔒 قفل کردن گاوصندوق")
        print("=" * 60)
        print("📦 مرحله ۱: تهیه نسخه پشتیبان اجباری...")
        self.backup()

        print("\n🔐 مرحله ۲: رمزنگاری و حذف فایل‌های اصلی...")
        fernet = self._get_fernet()
        encrypted_count = 0

        for filename in CRITICAL_FILES:
            src = self.source_dir / filename
            if not src.exists():
                continue
            try:
                data = src.read_bytes()
                encrypted = fernet.encrypt(data)
                dst = self.encrypted_dir / (filename + ".enc")
                dst.write_bytes(encrypted)
                os.chmod(dst, 0o600)
                src.unlink()
                encrypted_count += 1
                print(f"  🔒 {filename} رمزنگاری و حذف شد")
            except Exception as e:
                print(f"  ❌ خطا در {filename}: {e}")

        print(f"\n✅ {encrypted_count} فایل قفل شدند.")
        print("🚨 سیستم اکنون در حالت قفل است.")
        print("🔓 برای بازیابی: python3 shadow_vault.py unlock")

    def unlock(self):
        print("=" * 60)
        print("🔓 باز کردن گاوصندوق")
        print("=" * 60)
        encrypted = list(self.encrypted_dir.glob("*.enc"))
        if not encrypted:
            print("⚠️ هیچ فایل رمزنگاری‌شده‌ای وجود ندارد.")
            return

        fernet = self._get_fernet()
        restored = 0
        for enc_file in encrypted:
            filename = enc_file.name.replace(".enc", "")
            dst = self.source_dir / filename
            try:
                decrypted = fernet.decrypt(enc_file.read_bytes())
                dst.write_bytes(decrypted)
                os.chmod(dst, 0o600)
                enc_file.unlink()
                restored += 1
                print(f"  🔓 {filename} بازیابی شد")
            except Exception as e:
                print(f"  ❌ خطا در {filename}: {e}")

        print(f"\n✅ {restored} فایل بازیابی شد.")
        print("🔓 گاوصندوق باز شد.")

    def verify(self):
        print("=" * 60)
        print("🔍 بررسی صحت گاوصندوق")
        print("=" * 60)
        if not self.key_file.exists():
            print("❌ کلید اصلی وجود ندارد!")
            return False
        print(f"✅ کلید اصلی: {self.key_file}")
        backups = list(self.backup_dir.glob("backup_*"))
        print(f"✅ نسخه‌های پشتیبان: {len(backups)}")
        encrypted = list(self.encrypted_dir.glob("*.enc"))
        print(f"✅ فایل‌های رمزنگاری‌شده: {len(encrypted)}")
        if encrypted:
            try:
                fernet = self._get_fernet()
                test_data = fernet.decrypt(encrypted[0].read_bytes())
                print(f"✅ تست رمزگشایی: موفق ({len(test_data)} بایت)")
            except Exception as e:
                print(f"❌ تست رمزگشایی: ناموفق ({e})")
                return False
        print("\n✅ گاوصندوق سالم است.")
        return True

    def list_contents(self):
        print("=" * 60)
        print("📋 محتوای گاوصندوق")
        print("=" * 60)
        print("\n🔑 کلید:", "✅" if self.key_file.exists() else "❌")
        backups = sorted(self.backup_dir.glob("backup_*"), reverse=True)
        print(f"\n💾 نسخه‌های پشتیبان: {len(backups)}")
        for b in backups[:5]:
            file_count = len(list(b.glob("*.enc")))
            print(f"   📦 {b.name} ({file_count} فایل)")
        encrypted = list(self.encrypted_dir.glob("*.enc"))
        print(f"\n🔒 فایل‌های در حالت قفل: {len(encrypted)}")
        for e in encrypted:
            print(f"   🔐 {e.name}")

    def restore_from_backup(self, backup_name=None):
        backups = sorted(self.backup_dir.glob("backup_*"), reverse=True)
        if not backups:
            print("❌ هیچ نسخه پشتیبانی پیدا نشد.")
            return
        backup_path = self.backup_dir / backup_name if backup_name else backups[0]
        print(f"📦 بازیابی از: {backup_path.name}")
        fernet = self._get_fernet()
        restored = 0
        for enc_file in backup_path.glob("*.enc"):
            filename = enc_file.name.replace(".enc", "")
            dst = self.source_dir / filename
            try:
                decrypted = fernet.decrypt(enc_file.read_bytes())
                dst.write_bytes(decrypted)
                os.chmod(dst, 0o600)
                restored += 1
                print(f"  🔓 {filename}")
            except Exception as e:
                print(f"  ❌ {filename}: {e}")
        print(f"\n✅ {restored} فایل بازیابی شد.")

    def rotate_key(self):
        print("=" * 60)
        print("🔄 چرخش کلید")
        print("=" * 60)
        if not self.key_file.exists():
            print("❌ کلید قدیمی وجود ندارد!")
            return
        old_fernet = self._get_fernet()
        print("📖 رمزگشایی با کلید قدیمی...")
        decrypted_data = {}
        for enc_file in list(self.backup_dir.rglob("*.enc")) + list(self.encrypted_dir.glob("*.enc")):
            try:
                decrypted_data[str(enc_file)] = old_fernet.decrypt(enc_file.read_bytes())
            except Exception as e:
                print(f"  ❌ {enc_file.name}: {e}")
        print(f"  ✅ {len(decrypted_data)} فایل")
        print("\n🔑 تولید کلید جدید...")
        old_key_file = self.key_file.with_suffix(".key.old")
        old_key_file.write_bytes(self.key_file.read_bytes())
        os.chmod(old_key_file, 0o600)
        new_key = Fernet.generate_key()
        self.key_file.write_bytes(new_key)
        os.chmod(self.key_file, 0o600)
        new_fernet = Fernet(new_key)
        print("\n🔒 رمزنگاری مجدد...")
        for filepath, data in decrypted_data.items():
            Path(filepath).write_bytes(new_fernet.encrypt(data))
        print(f"✅ {len(decrypted_data)} فایل با کلید جدید رمزنگاری شد")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 shadow_vault.py [backup|lock|unlock|verify|list|restore|rotate]")
        sys.exit(1)
    vault = ShadowVault()
    cmd = sys.argv[1].lower()
    if cmd == "backup": vault.backup()
    elif cmd == "lock": vault.lock()
    elif cmd == "unlock": vault.unlock()
    elif cmd == "verify": vault.verify()
    elif cmd == "list": vault.list_contents()
    elif cmd == "restore":
        vault.restore_from_backup(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "rotate": vault.rotate_key()
    else:
        print(f"❌ دستور ناشناخته: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
