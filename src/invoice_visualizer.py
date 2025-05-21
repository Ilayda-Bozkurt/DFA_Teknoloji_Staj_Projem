import cv2
import os
import numpy as np
from difflib import SequenceMatcher

#OCR ile çıkarılan verileri görsel üzerinde göstermek için tasarlanmış bir sınıftır.
class InvoiceVisualizer:
    def __init__(self):
        self.COLOR_MAP = {
            'Fatura No': (0, 255, 0),    # Yeşil 
            'Fatura Tarihi': (255, 0, 0), # Mavi
            'Toplam Tutar': (0, 0, 255)   # Kırmızı
        }
        self.box_thickness = 2
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.text_color = (0, 0, 0)       # Siyah
        self.text_bg_color = (220, 220, 220) # Gri

    #Görseli yükler, veri alanları ile eşleşen kutuları bulur ve tanımlı alanları işaretleyip kaydeder.
    def visualize(self, image_path, ocr_data, extracted_data, output_path=None):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Görsel yüklenemedi: {image_path}")

        for field_name, field_value in extracted_data.items():
            if field_value == 'Bulunamadı':
                continue
                
            boxes = self._find_matching_boxes(ocr_data, field_value)
            
            # Sadece COLOR_MAP'te tanımlı alanları işaretle
            if field_name in self.COLOR_MAP:
                for box in boxes:
                    self._draw_box(image, box, field_name)
        
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, image)
            print(f"✅ İşaretlenmiş görsel kaydedildi: {output_path}")
        
        return image

    def _find_matching_boxes(self, ocr_data, target_text, threshold=0.7):
        boxes = []
        for i, text in enumerate(ocr_data['text']):
            if self._similarity(text, target_text) >= threshold:
                box = (
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i]
                )
                boxes.append(box)
        return boxes

    def _draw_box(self, image, box, label):
        x, y, w, h = box
        
        # Eğer etiket COLOR_MAP'te yoksa çizim yapma
        if label not in self.COLOR_MAP:
            return
            
        color = self.COLOR_MAP[label]
        
        # Kutucuk çiz
        cv2.rectangle(image, (x, y), (x + w, y + h), color, self.box_thickness)
        
        # Etiket arka planı
        (text_w, text_h), _ = cv2.getTextSize(
            label, self.font, self.font_scale, 1)
        cv2.rectangle(
            image, 
            (x, y - text_h - 5), 
            (x + text_w, y - 5), 
            self.text_bg_color, -1)
        
        # Etiket metni
        cv2.putText(
            image, label, (x, y - 10),
            self.font, self.font_scale,
            self.text_color, 1)

    @staticmethod
    def _similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()