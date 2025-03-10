import numpy as np

def earth_rotation_correction(traveltime, Xsat, Omegae_dot):
    # Xsat'ı sütun vektörü haline getir (reshape to column vector)
    Xsat = np.array(Xsat).reshape(-1, 1)

    # Dönme açısını hesapla (find the rotation angle)
    omegatau = Omegae_dot * (traveltime + 0.00173454)

    # Dönüş matrisi oluştur (build a rotation matrix)
    R3 = np.array([[np.cos(omegatau),  np.sin(omegatau), 0],
                   [-np.sin(omegatau), np.cos(omegatau), 0],
                   [0,                 0,                1]])

    # Dönüşü uygula (apply the rotation)
    Xsat_rot = np.dot(R3, Xsat)

    return Xsat_rot.flatten()  # Sonucu düzleştirilmiş bir dizi olarak döndür (flatten the result for consistency)