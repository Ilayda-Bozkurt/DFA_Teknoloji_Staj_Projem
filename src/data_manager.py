import csv
import json
import os

#DataManager adında bir sınıf oluşturuldu. Şimdilik __init__ metodu pass geçiliyor.
class DataManager:
    def __init__(self):
        pass

    def save_to_csv(self, data, csv_file_path):  #Metodun amacı veriyi CSV dosyasına kaydetmek.
        if not data:
            print("Kaydedilecek veri yok.")
            return
        
        #CSV kaydetme adımları
        fieldnames = list(data[0].keys())
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"\n✅ Tüm veriler '{csv_file_path}' dosyasına başarıyla kaydedildi.")

    def save_to_json(self, data, json_file_path):  #Metodun amacı veriyi JSON dosyasına kaydetmek.
        if not data:
            print("Kaydedilecek veri yok.")
            return

        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4, ensure_ascii=False)
        print(f"✅ Tüm veriler '{json_file_path}' dosyasına başarıyla kaydedildi.")