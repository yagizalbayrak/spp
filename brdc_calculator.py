import numpy as np
import gps_timer

def calculate_satellite_position(nav_body_data, t_gps):
    """
    Uydu pozisyonunu hesaplayan fonksiyon.
    
    Parametreler:
      nav_body_data: Parse edilmiş navigasyon verisi, her biri bir sözlük (dictionary) olarak; 
                     her kayıtta "prn", "toe", "sqrtA", "e", "i0", "OMEGA0", "omega",
                     "M0", "dn", "OMEGA", "idot", "cuc", "cus", "crc", "crs", "cic", "cis", 
                     "a0", "a1", "a2" vb. değerler bulunur.
      t_gps: Gözlem zamanı (GPS zamanı, saniye cinsinden). Bu değer spp_basic1'den epok bazlı olarak veriliyor.
    
    Dönüş:
      X, Y, Z: Uydunun ECEF koordinatları (metre).
      dts: Uydu saat hatası (saniye).
    """
    # Sabitler
    mu = 3.986004418e14      # Yerçekimi parametresi (m^3/s^2)
    OMEGA_e = 7.2921151467e-5  # Dünyanın dönüş hızı (rad/s)
    
    # NAV verisi doğrudan parametre olarak geldiği için filtrelemeye gerek yok
    data = nav_body_data  # NAV verisi zaten ilgili uydu için filtrelenmiş olarak geliyor
    
    # Kepler parametreleri
    sqrtA = data["sqrtA"]
    e = data["e"]
    i0 = data["i0"]
    OMEGA0 = data["OMEGA0"]
    omega = data["omega"]
    M0 = data["M0"]
    dn = data["dn"]
    OMEGA = data["OMEGA"]
    idot = data["idot"]
    toe = data["toe"]
    cuc = data["cuc"]
    cus = data["cus"]
    crc = data["crc"]
    crs = data["crs"]
    cic = data["cic"]
    cis = data["cis"]
    a0 = data["a0"]
    a1 = data["a1"]
    a2 = data["a2"]
    
    # Hesaplama: Yarıçapı (A) hesaplayın
    A = sqrtA ** 2
    n = np.sqrt(mu / A**3) + dn  # Düzeltilmiş ortalama hareket
    
    # Zaman farkı
    tk = t_gps - toe
    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800
        
    # Uydu saat hatası (clock bias)
    dts = a0 + a1 * tk + a2 * tk**2
    
    # Ortalama anomali (Mk)
    Mk = M0 + n * tk
    
    # Kepler denklemi: Dışmerkez anomali (Ek) iteratif olarak çözülüyor.
    Ek = Mk
    for _ in range(10):
        Ek_prev = Ek
        Ek = Mk + e * np.sin(Ek)
        if abs(Ek - Ek_prev) < 1e-12:
            break
    
    # Gerçek anomali (vk)
    vk = np.arctan2(np.sqrt(1 - e**2) * np.sin(Ek), np.cos(Ek) - e)
    
    # Enlem argümanı (phik) ve düzeltmeler
    phik = vk + omega
    delta_uk = cus * np.sin(2 * phik) + cuc * np.cos(2 * phik)
    Uk = phik + delta_uk
    
    # Yarıçap (r) ve düzeltme
    r = A * (1 - e * np.cos(Ek))
    delta_rk = crs * np.sin(2 * phik) + crc * np.cos(2 * phik)
    rk = r + delta_rk
    
    # Eğim (i) ve düzeltme
    i = i0 + idot * tk
    delta_ik = cis * np.sin(2 * phik) + cic * np.cos(2 * phik)
    ik = i + delta_ik
    
    # Yükselen düğüm noktasının (OMEGA_k) hesabı
    Omegak = OMEGA0 + (OMEGA - OMEGA_e) * tk - OMEGA_e * toe
    
    # Yörünge düzlemindeki koordinatlar
    x_prime = rk * np.cos(Uk)
    y_prime = rk * np.sin(Uk)
    
    # ECEF koordinatları
    X = x_prime * np.cos(Omegak) - y_prime * np.cos(ik) * np.sin(Omegak)
    Y = x_prime * np.sin(Omegak) + y_prime * np.cos(ik) * np.cos(Omegak)
    Z = y_prime * np.sin(ik)
    
    return X, Y, Z, dts
