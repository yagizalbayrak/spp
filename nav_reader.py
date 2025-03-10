import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import re
import os
import subprocess
from tkinter import ttk


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

# Function to decode NAV RINEX header
def decode_nav_header_data(file_path):
    
    def convert_to_e(line):
        return line.replace('D', 'E').replace('d', 'E').replace('e', 'E')
    
        
    header_data = {
        "version": None,
        "type": None,
        "run_by_date": None,
        "ion_alpha": None,
        "ion_beta": None,
        "delta_utc": None,
        "leap_seconds": None,
    }

    with open(file_path, 'r') as file:
        for line in file:
            label = line[60:].strip()

            if "RINEX VERSION / TYPE" in label:
                header_data["version"] = line[:9].strip()
                header_data["type"] = line[20:40].strip()
            elif "PGM / RUN BY / DATE" in label:
                header_data["run_by_date"] = line[:60].strip()
            elif "IONOSPHERIC CORR" in label and line[:4].strip() == "GPSA":
                header_data["ion_alpha"] = [
                    float(line[6:18].strip()),
                    float(line[18:30].strip()),
                    float(line[30:42].strip()),
                    float(line[42:54].strip())
                ]
            elif "IONOSPHERIC CORR" in label and line[:4].strip() == "GPSB":
                header_data["ion_beta"] = [
                    float(line[6:18].strip()),
                    float(line[18:30].strip()),
                    float(line[30:42].strip()),
                    float(line[42:54].strip())
                ]
            elif "DELTA-UTC: A0,A1,T,W" in label:
                header_data["delta_utc"] = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_to_e(line[5:60]))))
            elif "LEAP SECONDS" in label:
                header_data["leap_seconds"] = int(line[:6].strip())
            elif "END OF HEADER" in label:
                break

    return header_data

# Function to parse NAV RINEX body
def decode_nav_body_data(file_path):
    body_data = []


    def convert_to_e(line):
        return line.replace('D', 'E').replace('d', 'E').replace('e', 'E')

    def parse_float(value):
        return float(value) if value else None

    with open(file_path, 'r') as file:
        header_parsed = False
        while True:
            line = file.readline()
            if not line:
                break

            if not header_parsed:
                if "END OF HEADER" in line:
                    header_parsed = True
                continue

            if line[0] in ('G', 'R', 'J', 'C', 'S', 'I'):  # Identify satellite data
                identifier = line[0]
                observation = {}

                # First line data
                if identifier == 'G':
                    observation["prn"] = line[0:4].strip()
                    observation["epoch"] = line[4:23].strip()
                
                if identifier == 'G':  # GPS data
                    observation["a0"] = parse_float(convert_to_e(line[23:42].strip()))
                    observation["a1"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["a2"] = parse_float(convert_to_e(line[61:80].strip()))

                    # Continue reading the following lines
                    line = file.readline()
                    observation["IODC"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["crs"] = parse_float(convert_to_e(line[23:42].strip()))
                    observation["dn"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["M0"] = parse_float(convert_to_e(line[61:80].strip()))


                    line = file.readline()
                    observation["cuc"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["e"] = parse_float(convert_to_e(line[23:42].strip()))
                    observation["cus"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["sqrtA"] = parse_float(convert_to_e(line[61:80].strip()))


                    line = file.readline()
                    observation["toe"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["cic"] = parse_float(convert_to_e(line[23:42].strip()))
                    observation["OMEGA0"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["cis"] = parse_float(convert_to_e(line[61:80].strip()))


                    line = file.readline()
                    observation["i0"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["crc"] = parse_float(convert_to_e(line[23:42].strip()))
                    observation["omega"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["OMEGA"] = parse_float(convert_to_e(line[61:80].strip()))


                    line = file.readline()
                    observation["idot"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["L2_code"] = parse_float(line[23:42].strip())
                    observation["GPS_week"] = parse_float(line[42:61].strip())
                    observation["L2_P_flag"] = parse_float(line[61:80].strip())


                    line = file.readline()
                    observation["SV_accuracy"] = parse_float(convert_to_e(line[4:23].strip()))
                    observation["SV_health"] = parse_float(line[23:42].strip())
                    observation["TGD"] = parse_float(convert_to_e(line[42:61].strip()))
                    observation["IODC_clock"] = parse_float(line[61:80].strip())


                    line = file.readline()
                    observation["trans_time"] = parse_float(convert_to_e(line[4:23].strip()))


                    fit_interval = line[23:42].strip()
                    observation["fit_interval"] = parse_float(convert_to_e(fit_interval)) if fit_interval else None


                    spare1 = line[42:61].strip()
                    observation["spare1"] = parse_float(convert_to_e(spare1)) if spare1 else None


                    spare2 = line[61:80].strip()
                    observation["spare2"] = parse_float(convert_to_e(spare2)) if spare2 else None


                # Additional code for GLONASS, BDS, etc.

                body_data.append(observation)

    return body_data


# Function to format values for output
def format_value(value):

    if isinstance(value, float) or isinstance(value, int):
        return f"{value:.12E}"
    elif isinstance(value, str) and re.search(r'[eEdD]', value):
        return value.replace('d', 'E').replace('D', 'E').replace('e', 'E')
    return str(value)
