import os
from src.invoice_processor import InvoiceProcessor
from src.invoice_extractor import InvoiceExtractor
from src.invoice_visualizer import InvoiceVisualizer
from src.data_manager import DataManager

def main():
    # Tesseract'ın kurulu olduğu yolu belirtir.
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

    processor = InvoiceProcessor(tesseract_cmd_path=tesseract_path)
    extractor = InvoiceExtractor()
    visualizer = InvoiceVisualizer()
    data_manager = DataManager()

    invoices_dir = 'belgeler'  #Fatura görsellerinizin bulunduğu klasör
    output_images_dir = 'output_images' #Görselleştirilmiş çıktıların kaydedileceği klasör
    output_data_dir = 'output_data' #Çıkarılan CSV/JSON verilerinin kaydedileceği klasör
    
    all_extracted_data = []
    supported_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')

    # `belgeler` klasörünün varmı kontrol et eğer yoksa uyarı ver.
    if not os.path.exists(invoices_dir):
        print(f"Hata: '{invoices_dir}' klasörü bulunamadı. Lütfen fatura görsellerini bu klasöre yerleştirin.")
        return

    # output_images ve output_data klasörlerini oluştur(eğer yoksa)
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_data_dir, exist_ok=True)

    for filename in os.listdir(invoices_dir):
        if filename.lower().endswith(supported_extensions):
            image_path = os.path.join(invoices_dir, filename)
            print(f"\n--- '{filename}' belgesi işleniyor... ---")
            
            try:
                #1. Görseli yükle ve ön işle
                original_img_cv, img_pil = processor.load_and_preprocess_image(image_path)
                
                #2. Metni çıkar
                full_text = processor.extract_text(img_pil)
                
                #3. OCR detay verilerini al (görselleştirme için)
                ocr_data = processor.get_ocr_data(img_pil)
                
                print(f"--- Çıkarılan Ham Metin ({filename}): ---\n{full_text}\n" + "-" * 50)

                #4. Bilgileri çıkar
                extracted_info = extractor.extract_all_info(full_text)
                
                #5. Dosya Adını da extracted_info'ya ekle
                extracted_info['Dosya Adı'] = os.path.basename(image_path)
                all_extracted_data.append(extracted_info)

                #6. Çıkarılan bilgileri yazdır
                print(f"Çıkarılan Fatura Tarihi: {extracted_info['Fatura Tarihi']}")
                print(f"Çıkarılan Toplam Tutar: {extracted_info['Toplam Tutar']}")
                print(f"Çıkarılan Fatura No: {extracted_info['Fatura No']}")

                #7. Görselleştirme yap ve kaydet
                output_image_path = os.path.join(output_images_dir, f"annotated_{filename}")
                visualizer.visualize(
                    image_path=image_path,
                    ocr_data=ocr_data,
                    extracted_data=extracted_info,
                    output_path=output_image_path
                )
                print(f"\n ✅ Görselleştirilmiş çıktı kaydedildi: {output_image_path}")

            except Exception as e:
                print(f"'{filename}' işlenirken hata oluştu: {str(e)}")
                continue

    if all_extracted_data:
        csv_output_path = os.path.join(output_data_dir, 'tum_faturalar_cikartilan_veriler.csv')
        json_output_path = os.path.join(output_data_dir, 'tum_faturalar_cikartilan_veriler.json')
        
        data_manager.save_to_csv(all_extracted_data, csv_output_path)
        data_manager.save_to_json(all_extracted_data, json_output_path)
        print(f"\n ✅ Tüm veriler başarıyla kaydedildi:\n- {csv_output_path}\n- {json_output_path}")
    else:
        print("\n Hiçbir belgeden veri çekilemedi. Çıktı dosyaları oluşturulmadı.")

if __name__ == "__main__":
    main()