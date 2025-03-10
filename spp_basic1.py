import obs_reader
import obs_reader_pnds
import nav_reader
import gps_timer
import numpy as np
import json
from brdc_calculator import calculate_satellite_position
import brdc_c_test1
from gps_timer import utc_to_gps_sow  # GPS zamanı dönüşümü için import
from datetime import datetime  # datetime nesnesi oluşturmak için

obs_file_path = r"C:\Users\Root\Desktop\SPP Python Codes\base123i.24o"
nav_file_path = r"C:\Users\Root\Desktop\SPP Python Codes\base123i.24p"
obs_convert305 = obs_reader.convert_to_305(obs_file_path)
nav_convert305 = nav_reader.convert_to_305(nav_file_path)

obs_header_data = obs_reader.decode_obs_header_data(obs_convert305)
obs_body_data = obs_reader.decode_obs_body_data(obs_convert305)

nav_header_data = nav_reader.decode_nav_header_data(nav_convert305)
nav_body_data = nav_reader.decode_nav_body_data(nav_convert305)

# Tüm epoch'ları içeren listeyi oluştur
epoch_times = []
t_obs = []

# obs_body_data listesinin uzunluğunu bul
num_epochs = len(obs_body_data)

# Her epoch için döngü
for i in range(num_epochs):
    # Epoch bilgilerini al
    epoch_data = obs_body_data[i]['epoch']
    
    # Epoch zamanını string olarak formatla
    epoch_time = f"{epoch_data['year']} {epoch_data['month']} {epoch_data['day']} {epoch_data['hour']} {epoch_data['minute']} {epoch_data['second']}"
    
    # Epoch zamanını listeye ekle
    epoch_times.append(epoch_time)
    
    # GPS zamanına çevir ve t_obs listesine ekle
    _, gps_sow = utc_to_gps_sow(epoch_time)
    t_obs.append(gps_sow)

# Işık hızı (m/s)
c = 299792458.0

# Dünyanın dönüş hızı (rad/s)
OMEGA_dot_Earth = 7.2921151467e-5

# Her epoch için gözlemlenen PRN'leri ve uydu konumlarını tutan sözlükler
epoch_prns = {}
satellite_positions = {}  # Her epoch için uydu konumlarını saklayacak sözlük

# Alıcı yaklaşık konumu (XYZ0)
XYZ0 = obs_header_data['approx_position_xyz']

# Tüm epoch'lar için döngü
for epoch_idx, epoch_data in enumerate(obs_body_data):
    # Bu epoch için PRN listesi
    prn_list = []
    epoch_positions = {}  # Bu epoch'taki uydu konumlarını saklayacak sözlük
    
    # t_rec değeri (alıcı zamanı) - MATLAB'daki trec'e denk gelir
    t_rec = t_obs[epoch_idx]
    
    # Bu epoch'taki tüm gözlemler için döngü
    for sat_data in epoch_data['observations']:
        prn = sat_data['prn']
        
        # Pseudorange değerini al (C1C - MATLAB'daki OBS(i,2)'ye denk gelir)
        if 'C1C' in sat_data['observation_data']:
            pseudorange = sat_data['observation_data']['C1C']
            
            if prn not in prn_list:
                prn_list.append(prn)
                
                # Bu PRN için NAV verisini bul
                nav_data = next((data for data in nav_body_data if data['prn'] == prn), None)
                
                if nav_data:
                    # t_emi hesapla (sinyal gönderim zamanı) - MATLAB'daki Temi'ye denk gelir
                    t_emi = t_rec - pseudorange / c
                    
                    # İlk uydu pozisyonu hesaplaması
                    X, Y, Z, dts = calculate_satellite_position(nav_data, t_emi)
                    
                    # Düzeltilmiş t_emi hesaplaması (uydu saat hatası düzeltmesi ile)
                    t_emi = t_rec - pseudorange / c - dts
                    
                    # Son uydu pozisyonu hesaplaması
                    X, Y, Z, dts = calculate_satellite_position(nav_data, t_emi)
                    
                    # Uydu ve alıcı arasındaki fark vektörü (dXYZ)
                    dXYZ = np.array([X - XYZ0[0], Y - XYZ0[1], Z - XYZ0[2]])
                    
                    # Sinyalin yayılma süresi (tau)
                    tau = np.linalg.norm(dXYZ) / c
                    
                    # Dünya dönüşü düzeltme matrisi
                    R = np.array([
                        [np.cos(OMEGA_dot_Earth * tau), np.sin(OMEGA_dot_Earth * tau), 0],
                        [-np.sin(OMEGA_dot_Earth * tau), np.cos(OMEGA_dot_Earth * tau), 0],
                        [0, 0, 1]
                    ])
                    
                    # Düzeltilmiş uydu pozisyonu
                    XYZsat_corrected = np.dot(R, np.array([X, Y, Z]))
                    
                    # Uydu pozisyonunu kaydet
                    epoch_positions[prn] = {
                        'X': float(XYZsat_corrected[0]),
                        'Y': float(XYZsat_corrected[1]),
                        'Z': float(XYZsat_corrected[2]),
                        'dts': dts,
                        'pseudorange': pseudorange,
                        't_emi': t_emi,
                        'dXYZ': dXYZ.tolist(),
                        'tau': tau
                    }
    
    # Sözlüklere ekle
    epoch_prns[epoch_idx] = prn_list
    satellite_positions[epoch_idx] = epoch_positions

# Sonuçları yazdır ve kaydet
print(satellite_positions)
file_path = r"C:\Users\Root\Desktop\SPP Python Codes\satellite_positions.json"
with open(file_path, "w") as file:
    json.dump(satellite_positions, file)























