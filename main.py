import os
import time
import random
import sys 

# Import library Selenium yang diperlukan
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. KONSTANTA PENGATURAN BOT ---
# Akun TikTok yang pengikutnya akan kita target
TARGET_ACCOUNT = "racuntiktok.office" 
# Batasi jumlah follow per sesi untuk keamanan
MAX_FOLLOW_PER_SESSION = 20 

# --- 2. AMBIL KREDENSIAL DARI VARIABEL LINGKUNGAN ---
USERNAME = os.environ.get("TIKTOK_USERNAME")
PASSWORD = os.environ.get("TIKTOK_PASSWORD")

# --- 3. KONFIGURASI HEADLESS DRIVER & JALUR LOKASI ---
def setup_driver():
    """Mengatur dan mengembalikan Chrome WebDriver dalam mode Headless."""
    
    if not USERNAME or not PASSWORD:
        print("❌ ERROR: Variabel lingkungan TIKTOK_USERNAME atau TIKTOK_PASSWORD tidak ditemukan.")
        print("Silakan atur di Environment Variables Railway Anda.")
        return None

    chrome_options = Options()
    # Opsi WAJIB untuk server/cloud hosting
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")         
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--disable-extensions")
    
    # Menambahkan User Agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    # --- PENTING: Perbaikan Jalur Driver untuk Railway (PATH ABSOLUT) ---
    try:
        # Menghapus Service dan langsung menggunakan binary location yang diinstal via apt-get
        chrome_options.binary_location = '/usr/bin/chromium-browser' 
        
        # NOTE: Kita harus memastikan 'chromedriver' ada di PATH sistem.
        # Jika apt-get install chromium-browser berhasil, chromedriver seharusnya ada di /usr/bin/
        
        print("✅ Menginisialisasi Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Gagal menginisialisasi driver. Pastikan Chromium sudah terinstal di server! Error: {e}")
        # Keluar dari script jika driver gagal diinisialisasi
        sys.exit(1) 


def login_tiktok(driver, wait):
    """Melakukan proses login otomatis ke TikTok."""
    print("➡️ Membuka halaman login TikTok...")
    
    driver.get("https://www.tiktok.com/login")
    time.sleep(5) 

    try:
        # 1. Klik opsi login dengan Email/Username
        email_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Log in with email or username']"))
        )
        email_tab.click()
        print("   -> Memilih login dengan Username.")
        
        # 2. Masukkan Username
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(USERNAME)
        
        # 3. Masukkan Password
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(PASSWORD)
        
        # 4. Klik Tombol Login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        print("   -> Mengirim kredensial login.")
        
        # Tunggu proses login
        time.sleep(random.randint(10, 20)) 
        
        # 5. Cek keberhasilan login
        if "login" not in driver.current_url:
            print("🎉 Login berhasil!")
            return True
        else:
            print("⚠️ Login gagal. Mungkin ada CAPTCHA atau notifikasi lain yang memblokir.")
            return False

    except Exception as e:
        print(f"❌ Login Gagal Total. Error: {e}")
        return False


def auto_follow(driver, wait):
    """Menjalankan logika auto follow di followers akun target."""
    print(f"\n🚀 Mulai proses auto follow di followers dari @{TARGET_ACCOUNT}...")
    
    # Navigasi ke halaman followers dari akun target
    driver.get(f"https://www.tiktok.com/@{TARGET_ACCOUNT}/followers")
    time.sleep(5) 

    try:
        # Tunggu pop-up followers (list) muncul
        followers_list_xpath = "//div[@data-e2e='followers-list']"
        wait.until(EC.presence_of_element_located((By.XPATH, followers_list_xpath)))
        
        followers_container = driver.find_element(By.XPATH, followers_list_xpath)
        
        follow_count = 0
        
        # Loop untuk mencari dan mengklik tombol 'Follow'
        while follow_count < MAX_FOLLOW_PER_SESSION:
            try:
                # 1. Cari tombol 'Follow' yang dapat diklik
                follow_button = followers_container.find_element(By.XPATH, ".//button[text()='Follow']")
                
                # 2. Klik tombol follow
                follow_button.click()
                follow_count += 1
                
                print(f"   ✅ Follow ke-{follow_count} berhasil.")
                
                # 3. Jeda ACAL (sangat penting: 30-90 detik)
                sleep_time = random.randint(30, 90) 
                print(f"   ⏳ Menunggu {sleep_time} detik...")
                time.sleep(sleep_time)

            except:
                # Jika tombol 'Follow' tidak ditemukan, scroll
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 500;", followers_container)
                print("   -> Scrolling untuk memuat lebih banyak pengguna.")
                time.sleep(random.uniform(3, 7))
                
                if follow_count >= MAX_FOLLOW_PER_SESSION:
                    break
        
        print(f"\n🎉 Sesi auto follow selesai. Total {follow_count} di-follow.")

    except Exception as e:
        print(f"❌ Error saat proses auto follow: {e}")


# --- FUNGSI UTAMA BOT (ENTRY POINT) ---
if __name__ == "__main__":
    
    driver = setup_driver()
    if driver is None:
        sys.exit(1)

    # Inisialisasi waktu tunggu global
    wait = WebDriverWait(driver, 30) 

    try:
        # 1. Jalankan Login
        if login_tiktok(driver, wait):
            # 2. Jika Login berhasil, jalankan Auto Follow
            auto_follow(driver, wait)
        else:
            print("Tidak dapat menjalankan auto follow karena login gagal.")
            
    except Exception as final_e:
        print(f"❌ Kesalahan fatal dalam eksekusi bot: {final_e}")
        
    finally:
        # Tutup driver
        if driver:
            driver.quit()
            print("\n🏁 Driver ditutup. Bot selesai dieksekusi.")
