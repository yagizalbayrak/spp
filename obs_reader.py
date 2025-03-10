import subprocess
import os

# Function to convert RINEX to 3.05 format using gfzrnx.exe
def convert_to_305(file_path):
    file_directory, file_name = os.path.split(file_path)
    base_name, ext = os.path.splitext(file_name)
    converted_file_name = f"{base_name}_3.05{ext}"
    converted_file_path = os.path.join(file_directory, converted_file_name)
    gfzrnx_command = f'gfzrnx -finp "{file_path}" -fout "{converted_file_path}" -f 3.05'
    
    try:
        subprocess.run(gfzrnx_command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Conversion failed: {str(e)}")
    
    return converted_file_path

# Global sözlük: RINEX verilerini saklamak için
rinex_data_store = {}

# Function to decode OBS RINEX header
def decode_obs_header_data(file_path):
    obs_header_data = {
        "rinex_version": None,
        "file_type": None,
        "satellite_system": None,
        "pgm": None,
        "run_by": None,
        "date": None,
        "marker_name": None,
        "marker_number": None,
        "marker_type": None,
        "observer": None,
        "agency": None,
        "rec_num": None,
        "rec_type": None,
        "rec_version": None,
        "approx_position_xyz": [],
        "antenna_num_type": [],
        "antenna_delta_hen": [],
        "antenna_delta_xyz": [],
        "antenna_phasecenter": [],
        "antenna_bsight_xyz": None,
        "antenna_zerodir_azi": None,
        "antenna_zerodir_xyz": None,
        "center_of_mass_xyz": None,
        "sys_obs_types": {},
        "signal_strength_unit": None,
        "interval": None,
        "time_of_first_obs": None,
        "time_of_last_obs": None,
        "rec_clock_offs_appl": None,
        "sys_dcbs_applied": [],
        "sys_pcvs_applied": [],
        "sys_scale_factor": [],
        "sys_phase_shift": [],
        "leap_seconds": None,
        "num_of_satellites": None,
        "prn_obs": [],
        "glonass_slot_frq": []
    }

    with open(file_path, 'r') as file:
        for line in file:
            label = line[60:].strip()
            if "RINEX VERSION / TYPE" in label:
                obs_header_data["rinex_version"] = float(line[0:20].strip())
                obs_header_data["file_type"] = line[20:40]
                obs_header_data["satellite_system"] = line[40:60].strip()
            elif "MARKER NAME" in label:
                obs_header_data["marker_name"] = line[0:60].strip()
            elif "MARKER NUMBER" in label:
                obs_header_data["marker_number"] = line[0:20].strip()
            elif "MARKER TYPE" in label:
                obs_header_data["marker_type"] = line[0:60].strip()
            elif "OBSERVER / AGENCY" in label:
                obs_header_data["observer"] = line[0:20]
                obs_header_data["agency"] = line[20:60]
            elif "REC # / TYPE / VERS" in label:
                obs_header_data["rec_num"] = line[0:20].strip()
                obs_header_data["rec_type"] = line[20:40]
                obs_header_data["rec_version"] = line[40:60]
            elif "ANT # / TYPE" in label:
                obs_header_data["antenna_num_type"] = [line[0:20].strip(), line[20:40].strip()]
            elif "APPROX POSITION XYZ" in label:
                obs_header_data["approx_position_xyz"] = [float(line[0:14].strip()), float(line[14:28].strip()), float(line[28:42].strip())]
            elif "ANTENNA: DELTA H/E/N" in label:
                obs_header_data["antenna_delta_hen"] = [float(line[0:14].strip()), float(line[14:28].strip()), float(line[28:42].strip())]
            elif "ANTENNA: DELTA X/Y/Z" in label:
                obs_header_data["antenna_delta_xyz"] = [float(line[0:14].strip()), float(line[14:28].strip()), float(line[28:42].strip())]
            elif "ANTENNA: PHASECENTER" in label:
                obs_header_data["antenna_phasecenter"] = [line[0:1], line[3:6], float(line[7:20].strip()), float(line[20:34].strip()), float(line[34:60].strip())]
            elif "ANTENNA: B.SIGHT XYZ" in label:
                obs_header_data["antenna_bsight_xyz"] = [float(line[0:14].strip()), float(line[14:28].strip()), float(line[28:42].strip())]
            elif "ANTENNA: ZERODIR AZI" in label:
                obs_header_data["antenna_zerodir_azi"] = float(line[0:14].strip())
            elif "ANTENNA: ZERODIR XYZ" in label:
                obs_header_data["antenna_zerodir_xyz"] = [float(line[0:14].strip()), float(line[14:28].strip()), float(line[28:42].strip())]
            elif "CENTER OF MASS: XYZ" in label:
                obs_header_data["center_of_mass_xyz"] = [float(line[0:14]), float(line[14:28]), float(line[28:42])]
            elif "SYS / # / OBS TYPES" in label:
                sys = line[0:1].strip()
                num_obs = int(line[2:6].strip())
                obs_types = [line[i:i+4].strip() for i in range(7, 60, 4)]  # 1X, A3 formatında gözlem kodlarını almak için

                # Use continuation lines if the observation types span multiple lines
                while len(obs_types) < num_obs:
                    line = next(file)
                    obs_types.extend([line[i:i+4].strip() for i in range(6, 60, 4)])

                obs_header_data["sys_obs_types"][sys] = {
                    "num_obs": num_obs,
                    "obs_types": obs_types
                }
            elif "TIME OF FIRST OBS" in label:
                year = int(line[0:6].strip())
                month = int(line[6:12].strip())
                day = int(line[12:18].strip())
                hour = int(line[18:24].strip())
                minute = int(line[24:30].strip())
                second = float(line[30:43].strip())
                time_system = line[48:51].strip()
                obs_header_data["time_of_first_obs"] = {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "time_system": time_system
                }                
            elif "TIME OF LAST OBS" in label:
                year = int(line[0:6].strip())
                month = int(line[6:12].strip())
                day = int(line[12:18].strip())
                hour = int(line[18:24].strip())
                minute = int(line[24:30].strip())
                second = float(line[30:43].strip())
                time_system = line[48:51].strip()
                obs_header_data["time_of_last_obs"] = {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "time_system": time_system
                }
            elif "INTERVAL" in label:
                obs_header_data["interval"] = float(line[0:10].strip())
            elif "RCV CLOCK OFFS APPL" in label:
                obs_header_data["rec_clock_offs_appl"] = int((line[0:6]).strip())
            elif "SYS / DCBS APPLIED" in label:
                system = line[0:1].strip()
                program = line[1:19].strip()
                source = line[20:60].strip()
                obs_header_data["sys_dcbs_applied"].append({
                    "system": system,
                    "program": program,
                    "source": source
                })
            elif "SYS / PCVS APPLIED" in label:
                system = line[0:1].strip()
                program = line[1:19].strip()
                source = line[20:60].strip()
                obs_header_data["sys_pcvs_applied"].append({
                    "system": system,
                    "program": program,
                    "source": source
                })
            elif "SYS / SCALE FACTOR" in label:
                system = line[0:1].strip()
                factor = int(line[2:6].strip())
                num_obs_types = int(line[8:10].strip() or 0)
                obs_types = line[11:60].split()

                # Use continuation lines if the observation types span multiple lines
                if num_obs_types > 12:
                    while len(obs_types) < num_obs_types:
                        line = next(file)
                        obs_types.extend(line[11:60].split())

                obs_header_data["sys_scale_factor"].append({
                    "system": system,
                    "factor": factor,
                    "num_obs_types": num_obs_types,
                    "obs_types": obs_types
                })
            elif "SYS / PHASE SHIFT" in label:
                system = line[0:1].strip()
                obs_code = line[2:5].strip()
                try:
                    correction = float(line[6:14].strip())
                    correction = f"{correction:8.5f}"  # F8.5 formatında correction'ı ayarla
                except ValueError:
                    correction = None  # Bu durumda boş veri varsa None olarak ayarla
                num_satellites = int(line[15:18].strip() or 0)
                satellites = line[19:60].split()

                # Use continuation lines if the number of satellites span multiple lines
                while len(satellites) < num_satellites:
                    line = next(file)
                    satellites.extend(line[19:60].split())

                obs_header_data["sys_phase_shift"].append({
                    "system": system,
                    "obs_code": obs_code,
                    "correction": correction,
                    "num_satellites": num_satellites,
                    "satellites": satellites
                })

            elif "GLONASS SLOT / FRQ #" in label:
                num_satellites = int(line[0:3].strip())
                satellites = []
                freq_numbers = []

                # İlk 8 uydu için
                for i in range(8):
                    if i < num_satellites:
                        # Her bir uydu ve frekans numarasını al
                        # 4X boşluk, 1 karakter uydu numarası, 2 karakter frekans numarası
                        satellite = line[4 + i*8:5 + i*8].strip()  # A1
                        freq_number = line[6 + i*8:8 + i*8].strip()  # I2.2
                        if satellite and freq_number:
                            satellites.append(satellite)
                            try:
                                freq_numbers.append(int(freq_number))
                            except ValueError:
                                freq_numbers.append(None)

                # Daha fazla uydu varsa, devam satırlarını oku
                while len(satellites) < num_satellites:
                    line = next(file)
                    for i in range(4):  # Her devam satırı için 4 uydu bilgisi okunur
                        if len(satellites) < num_satellites:
                            satellite = line[4 + i*8:5 + i*8].strip()  # A1
                            freq_number = line[6 + i*8:8 + i*8].strip()  # I2.2
                            if satellite and freq_number:
                                satellites.append(satellite)
                                try:
                                    freq_numbers.append(int(freq_number))
                                except ValueError:
                                    freq_numbers.append(None)

                obs_header_data["glonass_slot_frq"].append({
                    "num_satellites": num_satellites,
                    "satellites": satellites,
                    "freq_numbers": freq_numbers
                })
            elif "# OF SATELLITES" in label:
                num_of_satellites = int(line[0:6].strip())
                obs_header_data["num_of_satellites"] = num_of_satellites
            elif "LEAP SECONDS" in label:
                current_leap_seconds = int(line[0:6].strip())
                future_past_leap_seconds = int(line[6:12].strip())
                week_number = int(line[12:18].strip())
                day_number = int(line[18:24].strip())
                time_system_identifier = line[24:27].strip()
                obs_header_data["leap_seconds"] = {
                    "current_leap_seconds": current_leap_seconds,
                    "future_past_leap_seconds": future_past_leap_seconds,
                    "week_number": week_number,
                    "day_number": day_number,
                    "time_system_identifier": time_system_identifier
                }
            elif "PRN / # OF OBS" in label:
                prn_obs_data = []

                while True:
                    prn_id = line[3:6].strip()
                    observation_counts = [int(line[6 + i*6:12 + i*6].strip()) for i in range(9) if line[6 + i*6:12 + i*6].strip()]

                    # Eğer 9'dan fazla gözlem türü varsa, devam satırlarını oku
                    while len(observation_counts) % 9 == 0 and len(observation_counts) > 0:
                        line = next(file)
                        observation_counts.extend([int(line[6 + i*6:12 + i*6].strip()) for i in range(9) if line[6 + i*6:12 + i*6].strip()])

                    prn_obs_data.append({
                        "prn_id": prn_id,
                        "observation_counts": observation_counts
                    })

                    # Bir sonraki satırda PRN / # OF OBS etiketi yoksa döngüyü kır
                    line = next(file)
                    if "PRN / # OF OBS" not in line:
                        break

                obs_header_data["prn_obs"] = prn_obs_data

    return obs_header_data

# Function to decode OBS RINEX data with dynamic observation types for GPS
def decode_obs_body_data(file_path):
    obs_header_data = decode_obs_header_data(file_path)
    obs_body_data = []

    with open(file_path, 'r') as file:
        header_end = False
        epoch_recording = False
        num_satellites_in_epoch = 0
        satellites_read = 0

        for line in file:
            if "END OF HEADER" in line:
                header_end = True
                continue
            if not header_end:
                continue

            # Epoch record (starts with '>')
            if line.startswith('>'):
                # Yeni bir epoch başlıyor
                year = int(line[2:6])
                month = int(line[7:9])
                day = int(line[10:12])
                hour = int(line[13:15])
                minute = int(line[16:18])
                second = int(float(line[19:30]))
                epoch_flag = int(line[31:32])
                num_satellites_in_epoch = int(line[33:36])
                # Alıcı saat ofseti varsa
                if len(line) > 40:
                    receiver_clock_offset = float(line[41:56].strip())
                else:
                    receiver_clock_offset = None

                obs_body_data.append({
                    "epoch": {
                        "year": year,
                        "month": month,
                        "day": day,
                        "hour": hour,
                        "minute": minute,
                        "second": second,
                        "epoch_flag": epoch_flag,
                        "num_satellites": num_satellites_in_epoch,
                        "receiver_clock_offset": receiver_clock_offset
                    },
                    "observations": []
                })
                epoch_recording = True
                satellites_read = 0
                continue

            if epoch_recording:
                # Her uydu satırını okuyoruz
                prn = line[0:3].strip()
                if not prn:
                    # Boş satırlarda sorun çıkmasın
                    continue

                # Uydu sistemine göre obs_types listesini al
                system_code = prn[0]  # Örn: 'G' veya 'R'
                if system_code != 'G': # Sadece GPS uydu verilerini okuyoruz isterseniz diğer sistemler için de ekleyebilirsiniz, ya da burayı silerek tüm sistemler için okuma yapabilirsiniz
                    continue
                if system_code in obs_header_data['sys_obs_types']:
                    obs_types = obs_header_data['sys_obs_types'][system_code]['obs_types']
                else:
                    # Eğer header'da bu sistem için obs_types yoksa boş liste
                    obs_types = []

                obs_line = line[3:].rstrip('\n')
                length = len(obs_line)

                satellite_info = {
                    "prn": prn,
                    "observation_data": {},
                    "aux_data": {}  # LLI ve SNR bilgileri burada tutulacak
                }

                # obs_types sayısı kadar 16 karakterlik bloklar halinde oku
                for i, obs_type in enumerate(obs_types):
                    start_idx = i * 16
                    if start_idx >= length:
                        # Satırın sonuna geldik, daha fazla veri yok
                        break
                    end_idx = start_idx + 16
                    if end_idx > length:
                        # Son blok 16 karakterden kısa olabilir
                        end_idx = length

                    observation_field = obs_line[start_idx:end_idx]

                    # İlk 14 karakter gözlem değeri
                    obs_value_str = observation_field[0:14].strip()
                    # 15. karakter LLI
                    LLI = observation_field[14:15].strip() if len(observation_field) >= 15 else None
                    # 16. karakter SNR/SSI
                    SNR = observation_field[15:16].strip() if len(observation_field) == 16 else None

                    # Boşlukları None yap
                    LLI = LLI if LLI else None
                    SNR = SNR if SNR else None

                    # Gözlem değerini float'a çevir
                    if obs_value_str:
                        try:
                            obs_value = float(obs_value_str)
                        except ValueError:
                            obs_value = None
                    else:
                        obs_value = None

                    # Gözlem değerini observation_data altına koy
                    satellite_info["observation_data"][obs_type] = obs_value

                    # LLI ve SNR bilgilerini aux_data altına koy
                    satellite_info["aux_data"][obs_type] = {
                        "LLI": LLI,
                        "SNR": SNR
                    }

                obs_body_data[-1]["observations"].append(satellite_info)

                satellites_read += 1
                # Tüm uydular okunduysa bu epoch bitti
                if satellites_read == num_satellites_in_epoch:
                    epoch_recording = False

    return obs_body_data