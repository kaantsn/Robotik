# 🛡️ Robotik: Hava Savunma Sistemi Simülasyonu

Bu proje, **ROS 2** altyapısı üzerinde çalışan otonom bir Komuta Kontrol (C2) ve Simülasyon sistemidir. 10 adet taretin (launcher), 360 derecelik bir taktik sahada sürü (swarm) halinde gelen 100 farklı tehdidi otonom olarak paylaşıp imha etmesini simüle eder.

> **📽️ Proje Tanıtım Videosu**
> https://github.com/user-attachments/assets/e5e299a3-3336-4173-bce4-2ce14c74a9de

## 🧠 Algoritma ve Mantıksal Altyapı

Sistem, insan müdahalesine ihtiyaç duymadan "Karar Destek" ve "Angajman" süreçlerini şu algoritmalarla yönetir:

*   **Otonom Hedef Dağıtımı (Target Allocation):** Çoklu hedefleri taretlere paylaştırırken mühimmat yönetimi yapar. Her hedef için en uygun (en yakın) tareti Öklid mesafesi ($d = \sqrt{\Delta x^2 + \Delta y^2 + \Delta z^2}$) kullanarak seçer.
*   **Kinematik Önleme (ProNav):** Savunma füzeleri, hedefin anlık konumuna değil, vektörel hız güncellemeleriyle çarpışma noktasına doğru otonom yönlenir.
*   **Tehdit Değerlendirmesi:** Her bir iz (track) için gerçek zamanlı **ETA** (Varış Süresi) ve **Pk** (Vuruş Olasılığı) hesaplayarak hedefleri KRİTİK/YÜKSEK olarak sınıflandırır.

## 🛠️ Teknik Mimari

*   **ROS 2 Jazzy/Humble:** Düğümler arası (Radar, Taret, GUI) yüksek hızlı DDS haberleşmesi.
*   **Taktik Kontrol Paneli:** Python Tkinter ile geliştirilmiş, Link-16 standartlarında AESA radar ekranı ve taktik olay günlüğü.
*   **3D Görselleştirme (RViz 2):** Süpersonik şok dalgaları, füze izleri ve taret hareketlerinin 3 boyutlu ortamda doğrulanması.
*   **Yıldız Formasyonu:** Maksimum kapsama alanı sağlayan özel geometrik taret dizilimi.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için:
```bash
# Workspace klasörüne gidin
cd ~/air_defense_ws

# Projeyi derleyin
colcon build --packages-select air_defense_core
source install/setup.bash

# Tek tıkla tüm sistemi (RViz + Dashboard + Simülasyon) başlatın
bash SUNUM_BASLAT.sh
