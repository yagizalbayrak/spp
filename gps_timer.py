from datetime import datetime

def utc_to_gps_sow(epoch):
    """
    UTC zamanını GPS haftası ve hafta içindeki saniyeye dönüştürür.

    Args:
        epoch_time (str): Epoch zamanı, "YYYY MM DD HH mm ss" formatında.
        
    Returns:
        tuple: (gps_week, gps_sow) GPS haftası ve hafta içindeki saniye.
    """
    gps_epoch = datetime(1980, 1, 6, 0, 0, 0)
    utc_time = datetime.strptime(epoch, "%Y %m %d %H %M %S")
    delta = utc_time - gps_epoch
    gps_week = delta.days // 7
    gps_sow = (delta.days % 7) * 86400 + delta.seconds
    return gps_week, gps_sow
  

