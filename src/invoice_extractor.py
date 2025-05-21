import re

#Fatura metninden tarih,toplam,fatura no çıkarmak için kullanılan sınıftır.
class InvoiceExtractor:
    def __init__(self):
        #Farklı formatlardaki tarihleri yakalamak için 3 farklı Regex kalıbı
        self.date_patterns = [
            r'(?:Fatura\s+Tarihi|Tarih)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4})', # DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY 
            r'(?:Fatura\s+Tarihi|Tarih)\s*:\s*(\d{1,2}\s+(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4})', # DD Ay YYYY 
            r'Tarih\s+(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4})', # Sadece "Tarih" kelimesi ve ardından gelen tarih (fatura2.png için)
        ]

        #Farklı şekillerde yazılmış toplam tutarları yakalamak için 3 desen
        self.total_amount_patterns = [
            r'Genel\s+Toplam\s*[\n\r]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*₺?', # "Genel Toplam" (fatura2 ve fatura3)
            r'KDV \(\%\d+\)[\s\S]*?Toplam\s*[\n\r]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*₺?', # KDV sonrası "Toplam"
            r'Toplam\s*[\n\r]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*₺?' # Sadece "Toplam"
        ]

        #Farklı formatlardaki fatura numaralarını yakalamak için 3 desen
        self.invoice_no_patterns = [
            r'Fatura No\s*:\s*(#?[A-Za-z0-9-/]+)', # "Fatura No: PRO2024" veya "Fatura No: 0123456789101" (en spesifik)
            r'PROFORMA\s+FATURA[\s\S]*?Fatura No:\s*(#?[A-Za-z0-9-/]+)', # Proforma Fatura içindeki "Fatura No:"
            r'Fatura\s*[\n\r]?\s*([A-Za-z0-9-]+)' # "Fatura" kelimesinden sonraki numara (fatura2 için yedek)
        ]

    #Metin içinden tarih bilgisini çıkarır.
    def extract_date(self, text):
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                # Ay isimli format için dönüşüm
                if any(m in date_str for m in ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']):
                    month_map = {
                        'ocak': '01', 'şubat': '02', 'mart': '03', 'nisan': '04', 'mayıs': '05', 'haziran': '06',
                        'temmuz': '07', 'ağustos': '08', 'eylül': '09', 'ekim': '10', 'kasım': '11', 'aralık': '12'
                    }
                    parts = date_str.split()
                    if len(parts) == 3:
                        day = parts[0].zfill(2)
                        month = month_map.get(parts[1].lower(), '00')
                        year = parts[2]
                        return f"{day}.{month}.{year}"
                return date_str
        return 'Bulunamadı'

    #Metin içinden toplam tutarı çıkarır.
    def extract_total_amount(self, text):
        for pattern in self.total_amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount = match.group(1).strip()
                return amount.replace('.', '').replace(',', '.')
        return 'Bulunamadı'

    #Metin içinden fatura numarasını çıkarır.
    def extract_invoice_number(self, text):
        for pattern in self.invoice_no_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return 'Bulunamadı'

    #Tüm bilgileri tek bir çağrıda çıkarır.
    def extract_all_info(self, full_text):
        return {
            'Fatura Tarihi': self.extract_date(full_text),
            'Toplam Tutar': self.extract_total_amount(full_text),
            'Fatura No': self.extract_invoice_number(full_text)
        }