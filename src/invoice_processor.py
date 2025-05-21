import cv2
import pytesseract
from PIL import Image
import os

class InvoiceProcessor:
    def __init__(self, tesseract_cmd_path=None):
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    #Görseli yükle ve ön işleme yap.Eğer dosya yoksa uyarı mesajı ver.
    def load_and_preprocess_image(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"'{image_path}' dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")

        img_cv = cv2.imread(image_path)
        if img_cv is None:
            raise ValueError(f"'{image_path}' görseli yüklenemedi. Bozuk veya desteklenmeyen format olabilir.")

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # OTSU eşikleme, metin ve arka planı ayırmak için genellikle iyi sonuç verir.
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        img_pil = Image.fromarray(thresh)
        
        return img_cv, img_pil

    #Ön işleme yapılmış görselden metin çıkarır.
    def extract_text(self, img_pil):
        full_text = pytesseract.image_to_string(img_pil, lang='tur+eng')
        return full_text

    def get_ocr_data(self, img_pil):
        data = pytesseract.image_to_data(img_pil, lang='tur+eng', output_type=pytesseract.Output.DICT)
        return data
    

    #Çıkarılan verileri görselleştirir.
    def visualize_extracted_data(self, image_path, extracted_data, output_path=None):
        _, img_pil = self.load_and_preprocess_image(image_path)
        ocr_data = self.get_ocr_data(img_pil)
        
        return self.visualizer.visualize(
            image_path=image_path,
            ocr_data=ocr_data,
            extracted_data=extracted_data,
            output_path=output_path
        )