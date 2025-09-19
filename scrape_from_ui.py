

def scrape_from_ui(self):
    url = self.entry_url.get().strip()
    if not url:
        messagebox.showwarning("Uyarı", "Lütfen hedef URL girin.")
        return

    self.log(f"Scrape başlatılıyor: {url}")
    self.txt_recipients.delete("1.0", tk.END)

    # Thread ile çalıştırarak UI’nin donmasını önlüyoruz
    def scrape_thread():
        try:
            from email_scraper import (
                scrape_website,
            )  # email_scraper.py dosyasından fonksiyon

            emails = scrape_website(
                url, max_count=50
            )  # max_count isteğe göre ayarlanabilir
            if emails:
                self.recipients = [{"email": e} for e in emails]
                for r in self.recipients:
                    self.txt_recipients.insert(tk.END, r["email"] + "\n")
                self.log(f"Scrape tamamlandı, {len(emails)} email bulundu.")
            else:
                self.log("Scrape tamamlandı, email bulunamadı.")
                messagebox.showinfo("Bilgi", "Email bulunamadı.")
        except Exception as e:
            self.log(f"Scrape hatası: {e}")
            messagebox.showerror("Hata", f"Scrape sırasında hata oluştu: {e}")

    t = threading.Thread(target=scrape_thread, daemon=True)
    t.start()
