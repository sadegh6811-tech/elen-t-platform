import pandas as pd
import os

# ساخت پوشه data اگر وجود ندارد
os.makedirs('data', exist_ok=True)

base_url = "https://raw.githubusercontent.com/ejtraderLabs/historical-data/main/EURUSD/"

timeframes = {
    'h4': 'EURUSDh4.csv',
    'd1': 'EURUSDd1.csv'
}

for tf_name, filename in timeframes.items():
    url = base_url + filename
    print(f"⏳ در حال دانلود داده {tf_name.upper()} از {url} ...")
    try:
        df = pd.read_csv(url)
        output_path = f'data/EURUSD_{tf_name}.csv'
        df.to_csv(output_path, index=False)
        print(f"✅ داده {tf_name.upper()} با {len(df)} کندل در {output_path} ذخیره شد.")
        print(f"   📅 بازه زمانی: از {df.iloc[0, 0]} تا {df.iloc[-1, 0]}")
        print(f"   📊 ستون‌ها: {list(df.columns)}")
    except Exception as e:
        print(f"❌ خطا در دانلود {tf_name}: {e}")

print("\n✅ دانلود کامل شد. حالا می‌توانید تست بعد ۱۶ را روی این داده‌ها اجرا کنید.")
