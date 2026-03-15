# %% IMPORTACIONES Y DEFINICIONES
import scipy.signal as signal
import math 
import biosppy
from biosppy.signals import ecg as ekg
import numpy as np
import matplotlib.pyplot as plt
import pyedflib
import nolds
import neurokit2 as nk
from datetime import datetime, timedelta
import pandas as pd

#defino las funciones
def abrir_y_corroborar(nombre_archivo, canal, freq_muestreo):
    ruta_archivo_edf = nombre_archivo
    archivo_edf = pyedflib.EdfReader(ruta_archivo_edf)
    cantidad_canales = archivo_edf.signals_in_file 
    num_muestras = archivo_edf.getNSamples()[canal]  
    frecuencia_muestreo = 512
    datos_canal = archivo_edf.readSignal(canal)
    eje_temp=np.arange(0, num_muestras/frecuencia_muestreo, 1/frecuencia_muestreo)
    archivo_edf.close()
    
    out = ekg.ecg(signal=datos_canal, sampling_rate=frecuencia_muestreo, show=True)
    senial_filt = out['filtered']
    rpeaks = out['rpeaks']
    heart_rate_ts0 = out['heart_rate_ts'] #LOS TIEMPOS EN SEGUNDOS EN QUE SE CALCULO 
    heart_rate0 = out['heart_rate']       #EL VALOR DE FRECUENCIA CARDIACA
    eje_temp0 = out['ts'] 
    plt.plot(eje_temp[5000:5500], senial_filt[5000:5500])
    return rpeaks, eje_temp, senial_filt



def calcular_segundos(hora_inicio, hora_evento, mismo_dia=True):
    # Convertir las horas a objetos datetime
    inicio = datetime.strptime(hora_inicio, "%H.%M.%S")
    evento = datetime.strptime(hora_evento, "%H.%M.%S")
    
    # Si el evento ocurre al día siguiente, sumamos 1 día al evento
    if not mismo_dia:
        evento += timedelta(days=1)
    
    # Calcular la diferencia en segundos
    segundos_transcurridos = int((evento - inicio).total_seconds())
    
    return segundos_transcurridos

# %% IMPORTACIONES Y DEFINICIONES
import pyhrv.tools as tools
import pyhrv.time_domain as td 
import pyhrv.frequency_domain as fd
import pyhrv.nonlinear as nl 

   
 
# %% PACIENTE 0 SEIZURE 2
ventana_len = 180
ventana_solap = 60


frecuencia_muestreo = 512
canal = 32
nombre = '../siena-scalp-eeg-database-1.0.0/siena-scalp-eeg-database-1.0.0/PN01/PN01-1.edf'
rpeaks, eje_temp, ecg = abrir_y_corroborar(nombre, canal, frecuencia_muestreo)
hora_inicio_registro = "19.00.44"
hora_inicio_crisis1 = "21.51.02"
hora_fin_crisis1 = "21.51.56"
hora_inicio_crisis2 = "07.53.17"
hora_fin_crisis2 = "07.53.17"
hora_fin_registro = "08.29.41"
nombre_paciente = "P1"


segundos_inicio_crisis1 = calcular_segundos(hora_inicio_registro, hora_inicio_crisis1, True)
segundos_fin_crisis1 = calcular_segundos(hora_inicio_registro, hora_fin_crisis1, True)

segundos_inicio_crisis2 = calcular_segundos(hora_inicio_registro, hora_inicio_crisis2, False)
segundos_fin_crisis2 = calcular_segundos(hora_inicio_registro, hora_fin_crisis2, False)

segundos_fin_registro = calcular_segundos(hora_inicio_registro, hora_fin_registro, False)

muestra_inicial_crisis1 = segundos_inicio_crisis1 * frecuencia_muestreo
muestra_final_crisis1 = segundos_fin_crisis1 * frecuencia_muestreo

muestra_inicial_crisis2 = segundos_inicio_crisis2 * frecuencia_muestreo
muestra_final_crisis2 = segundos_fin_crisis2 * frecuencia_muestreo

muestra_inicial_preictal1 = (segundos_inicio_crisis1 - 15*60) * frecuencia_muestreo
muestra_final_preictal1 = segundos_fin_crisis1 * frecuencia_muestreo

muestra_inicial_preictal2 = (segundos_inicio_crisis2 - 15*60) * frecuencia_muestreo
muestra_final_preictal2 = segundos_fin_crisis2 * frecuencia_muestreo

muestra_inicial_interictal = 0
muestra_final_interictal = 0
clasificacion = []
ventanas_rpeaks = []
for i in range(0, len(rpeaks), ventana_len - ventana_solap):
    # extraigo la ventana de la señal
    ventana_rpeaks = rpeaks[i:i + ventana_len]    #la ultima ventana puede tener longitud menor
    # Extraer la señal correspondiente en senial_filtrada
    ventana_ecg = ecg[ventana_rpeaks[0]:ventana_rpeaks[-1] + 1]    
    if (len(ventana_rpeaks) == 180):
        ventanas_rpeaks.append(ventana_rpeaks)
        if (i + 180 < len(rpeaks) and ((rpeaks[i] > muestra_inicial_preictal1 and rpeaks[i+180] < muestra_final_crisis1+15*60*frecuencia_muestreo) 
                                    or (rpeaks[i] > muestra_inicial_preictal2 and rpeaks[i+180] < muestra_final_crisis2+15*60*frecuencia_muestreo))):
            clasificacion.append('preictal')
        else:
                clasificacion.append('no_preictal')
        
ventanas_ms = []
time_domain_features = []
freq_features = []
nonlinear_features = []
nn_intervals = []
ventanas_intervalos_nn = []




for i in range(len(ventanas_rpeaks)):

    diferencias = np.diff(ventanas_rpeaks[i])  # Esto calcula nn_intervals[i][j] - nn_intervals[i][j+1]
    ventanas_intervalos_nn.append(diferencias/frecuencia_muestreo*1000)  # Agregar las diferencias a la lista

# diferencias = np.diff(nn_intervals[0])
intervalo_nn=ventanas_intervalos_nn[0]

#ventanas_intervalos_nn = ventanas_intervalos_nn[0:50]
# Calculo de parametros temporales, frecuenciales (welch) y no lineales con el diagrama de poincaré

#%% Temporales
time_features = []
nni = []
hr_mean = []
hr_min = []
hr_max = []
hr_std = []
for i in range (len(ventanas_intervalos_nn)):
    time_features.append(td.time_domain(ventanas_intervalos_nn[i]))
    nni.append(time_features[i]['nni_diff_mean'])
    hr_mean.append(time_features[i]['hr_mean'])
    hr_min.append(time_features[i]['hr_mean'])
    hr_max.append(time_features[i]['hr_max'])
    hr_std.append(time_features[i]['hr_std'])



#%% Frecuenciales
freq_features = []
VLF_power = []
lf_power = []
hf_power = []

for i in range (len(ventanas_intervalos_nn)):
    freq_features.append(fd.welch_psd(ventanas_intervalos_nn[i]))
    VLF_power.append(freq_features[i]['fft_abs'][0]) #0,1,2 porque asi lo hace la libreria esta
    lf_power.append(freq_features[i]['fft_abs'][1])
    hf_power.append(freq_features[i]['fft_abs'][2])




#%% No lineales
nonlinear_features = []
sd1 = []
sd2 = []
sd_ratio = []
elipse_area = []

for i in range (len(ventanas_intervalos_nn)):
    nonlinear_features.append(nl.poincare(ventanas_intervalos_nn[i]))
    sd1.append(nonlinear_features[i]['sd1'])
    sd2.append(nonlinear_features[i]['sd2'])
    sd_ratio.append(nonlinear_features[i]['sd_ratio'])
    elipse_area.append(nonlinear_features[i]['ellipse_area'])
    
#%% Armo el DataFrame

data = {
    'nni_diff_mean': [nni[i] for i in range(len(nni))],
    'hr_mean': [hr_mean[i] for i in range(len(hr_mean))],
    'hr_max': [hr_max[i] for i in range(len(hr_max))],
    'hr_std': [hr_std[i] for i in range(len(hr_std))],
    'VLF_power': [VLF_power[i] for i in range(len(VLF_power))],
    'LF_power': [lf_power[i] for i in range(len(lf_power))],
    'HF_power': [hf_power[i] for i in range(len(hf_power))],
    'sd1': [sd1[i] for i in range(len(sd1))],
    'sd2': [sd2[i] for i in range(len(sd2))],
    'sd_ratio': [sd_ratio[i] for i in range(len(sd_ratio))],
    'elipse_area': [elipse_area[i] for i in range(len(elipse_area))],
    'clasificacion': [clasificacion[i] for i in range(len(clasificacion))]
}
#%% Agrego una hoja al archivo excell
df = pd.DataFrame(data)
with pd.ExcelWriter('parametros_clasificacion.xlsx', mode='a', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='P1', index=False)