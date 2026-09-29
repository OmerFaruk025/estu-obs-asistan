from playwright.sync_api import sync_playwright
import time
from win10toast import ToastNotifier

toaster = ToastNotifier()

en_son_okunan_mesaj = ""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) 
    page = browser.new_page()

    try:
        print("Giriş Yapılıyor...")
        page.goto("https://giris.eskisehir.edu.tr/login?redirect_uri=https://obs.eskisehir.edu.tr")
        
        # BİLGİLERİNİ GİRMEYİ UNUTMA
        page.fill("input[name='username']", "@ogr.eskisehir.edu.tr")
        page.fill("input[name='password']", "sifreniz")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        print("Giriş Başarılı, ana sayfanın oturması bekleniyor...")
        
        time.sleep(3)
        
        
        print("Mesajlar sayfasına geçiliyor...")
        page.goto("https://obs.eskisehir.edu.tr/#/mesajlasma")
        page.wait_for_load_state("networkidle")
        
    except Exception as e:
        print("Giriş Başarısız:", e)

    while True:
        try:
            print("\n--- Sayfa tazeleniyor (F5 atılıyor) ve kontrol ediliyor ---")
            
            page.reload(wait_until="networkidle")
            
            page.wait_for_selector("div[ng-click='konununMesajiniGetir(konu);']", timeout=15000)

            mesaj_kutulari = page.query_selector_all("div[ng-click='konununMesajiniGetir(konu);']")
            
            if len(mesaj_kutulari) > 0:
                kutu = mesaj_kutulari[0] 
                gonderen = kutu.query_selector("p.col-xs-6.top-pad-10").inner_text()
                
                konu_elementi = kutu.query_selector("p.col-xs-12:has-text('Konu')")
                konu = konu_elementi.inner_text() if konu_elementi else "Detay için OBS'ye gir"
                
                bildirim_metni = f"{gonderen}\n{konu}"
                
                # Hafıza kontrolü
                if bildirim_metni != en_son_okunan_mesaj:
                    print(f"-> YENİ MESAJ YAKALANDI: {bildirim_metni}")
                    toaster.show_toast("ESTÜ OBS YENİ MESAJ", bildirim_metni, duration=7, threaded=True)
                    en_son_okunan_mesaj = bildirim_metni
                else:
                    print("Yeni mesaj yok.")
            
            bekleme_suresi = 300 # 5 dakika

        except Exception as e:
            print("Pürüz çıktı (Oturum düşmüş olabilir):", e)
            bekleme_suresi = 60 

        # GERİ SAYIM DÖNGÜSÜ
        print(f"Sonraki kontrol için bekleniyor...")
        try:
            for kalan in range(bekleme_suresi, 0, -1):
                dakika = kalan // 60
                saniye = kalan % 60
                print(f"\rKalan süre: {dakika:02d}:{saniye:02d} ", end="", flush=True)
                time.sleep(1)
            print() 
        except KeyboardInterrupt:
            print("\nBekleme modunda.")
            break