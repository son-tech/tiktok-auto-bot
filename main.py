import os
import time
import random

# Import library Selenium yang diperlukan
# Catatan: Kita mengandalkan Selenium versi terbaru yang dapat 
# mengelola WebDriver secara otomatis.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. AMBIL KREDENSIAL DARI VARIABEL LINGKUNGAN ---
# Nilai TIKTOK_USERNAME dan TIKTOK_PASSWORD dibaca dari Environment Variables di Render
USERNAME = os.environ.get("TIKTOK_USERNAME")
PASSWORD = os.environ.get("TIKTOK_PASSWORD")

# --- 2. KONFIGURASI HEADLESS DRIVER (WAJIB DI SERVER) ---
def setup_driver():
    """Mengatur dan mengembalikan Chrome WebDriver dalam mode Headless."""
    
    if not USERNAME or not PASSWORD:
        print("❌ ERROR: Variabel lingkungan TIKTOK_USERNAME atau TIKTOK_PASSWORD tidak ditemukan.")
        print("Silakan atur di Environment Variables Render Anda.")
        return None

    chrome_options = Options()
    # Opsi WAJIB untuk server/cloud hosting
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu") 
    
    # Menambahkan User Agent untuk terlihat seperti browser biasa
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    print("✅ Menginisialisasi Chrome WebDriver...")
    try:
        # Menginisialisasi driver dengan opsi yang telah dikonfigurasi
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Gagal menginisialisasi driver: {e}")
        return None


def login_tiktok(driver, wait):
    """Melakukan proses login otomatis ke TikTok."""
    print("➡️ Membuka halaman login TikTok...")
    
    # TikTok login flow
    driver.get("https://www.tiktok.com/login")
    time.sleep(5) # Tunggu halaman awal dimuat

    try:
        # Klik opsi login dengan Email/Username
        email_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Log in with email or username']"))
        )
        email_tab.click()
        print("   -> Memilih login dengan Username.")
        
        # Masukkan Username
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(USERNAME)
        
        # Masukkan Password
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(PASSWORD)
        
        # Klik Tombol Login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        print("   -> Mengirim kredensial login.")
        
        # Tunggu proses login (perlu waktu jika ada CAPTCHA atau verifikasi)
        time.sleep(random.randint(10, 15)) 
        
        # Cek apakah login berhasil dengan mendeteksi URL yang bukan halaman login
        if "login" not in driver.current_url:
            print("🎉 Login berhasil! Melanjutkan ke aksi bot.")
            return True
        else:
            print("⚠️ Gagal login. Mungkin ada CAPTCHA atau notifikasi lain yang memblokir.")
            return False

    except Exception as e:
        print(f"❌ Login Gagal Total: {e}")
        return False


def auto_follow(driver, wait, target_username="target_akun_populer"):
    """Menjalankan logika auto follow di followers akun target."""
    print(f"\n🚀 Mulai proses auto follow di followers dari @{target_username}...")
    
    # Navigasi ke halaman followers dari akun target
    driver.get(f"https://www.tiktok.com/@{target_username}/followers")
    time.sleep(5) # Tunggu halaman dimuat

    try:
        # Tunggu pop-up followers (list) muncul
        followers_list_xpath = "//div[@data-e2e='followers-list']"
        wait.until(EC.presence_of_element_located((By.XPATH, followers_list_xpath)))
        
        followers_container = driver.find_element(By.XPATH, followers_list_xpath)
        
        follow_count = 0
        MAX_FOLLOW = 20 # Batasi jumlah follow per sesi untuk keamanan
        
        # Loop untuk mencari dan mengklik tombol 'Follow'
        while follow_count < MAX_FOLLOW:
            try:
                # Cari tombol 'Follow' yang dapat diklik di dalam kontainer followers
                # XPATH ini mungkin perlu disesuaikan jika TikTok mengubah struktur HTML
                follow_button = followers_container.find_element(By.XPATH, ".//button[text()='Follow']")
                
                # Klik tombol follow
                follow_button.click()
                follow_count += 1
                
                print(f"   ✅ Follow ke-{follow_count} berhasil.")
                
                # Jeda ACAL (sangat penting untuk menghindari deteksi)
                sleep_time = random.randint(30, 90) 
                print(f"   ⏳ Menunggu {sleep_time} detik...")
                time.sleep(sleep_time)

            except:
                # Jika tombol 'Follow' tidak ditemukan lagi, scroll ke bawah
                # Jalankan script JS untuk scroll list followers
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 500;", followers_container)
                time.sleep(random.uniform(3, 7))
                
                # Periksa apakah target sudah tercapai
                if follow_count >= MAX_FOLLOW:
                    break
        
        print(f"\n🎉 Sesi auto follow selesai. Total {follow_count} di-follow.")

    except Exception as e:
        print(f"❌ Error saat proses auto follow: {e}")


# --- FUNGSI UTAMA BOT ---
if __name__ == "__main__":
    
    driver = setup_driver()
    if driver is None:
        exit()

    wait = WebDriverWait(driver, 30) # Waktu tunggu global

    try:
        # Jalankan Login
        if login_tiktok(driver, wait):
            # Jika Login berhasil, jalankan Auto Follow
            auto_follow(driver, wait, target_username="target_akun_populer")
        else:
            print("Tidak dapat menjalankan auto follow karena login gagal.")
            
    except Exception as final_e:
        print(f"❌ Kesalahan fatal dalam eksekusi bot: {final_e}")
        
    finally:
        # Tutup driver
        if driver:
            driver.quit()
            print("\n🏁 Driver ditutup. Bot selesai dieksekusi.")
