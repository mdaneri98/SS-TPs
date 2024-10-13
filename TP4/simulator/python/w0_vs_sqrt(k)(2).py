import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def process_particle_csv(file_path):
    df = pd.read_csv(file_path)
    max_amplitude = df['position'].abs().max()
    return max_amplitude

def get_k(static_csv_path):
    static_df = pd.read_csv(static_csv_path, header=None, skiprows=1)
    static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']
    return float(static_df['k'].values[0])

# Función que obtiene k y w0 del archivo static.csv
def get_k_and_w0(static_csv_path):
    static_df = pd.read_csv(static_csv_path, header=None, skiprows=1)
    static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']
    return float(static_df['k'].values[0]), float(static_df['wf'].values[0])


import os


def traverse_directories(base_path):
    k_values = []
    resonant_w_values = []
    max_amplitudes_for_w = []

    # Recorre solo los subdirectorios de cada 'k'
    for root_k, dirs_k, files_k in os.walk(base_path):
        if root_k == base_path:  # Solo entramos a subdirectorios de 'base_path'
            continue

        max_amplitude_for_k = -1
        resonant_w_for_k = None
        k_value = None

        # Recorremos solo los directorios inmediatos (nivel 1) dentro de cada 'k'
        for dir_w in dirs_k:
            root_w = os.path.join(root_k, dir_w)
            files_w = os.listdir(root_w)

            if 'particle.csv' in files_w and 'static.csv' in files_w:
                # Ruta de archivos CSV
                particle_csv_path = os.path.join(root_w, 'particle.csv')
                static_csv_path = os.path.join(root_w, 'static.csv')

                # Obtener la amplitud máxima para este 'w'
                current_amplitude = process_particle_csv(particle_csv_path)

                # Obtener el valor de 'k' y 'w0' desde el archivo 'static.csv'
                k_value, w0_value = get_k_and_w0(static_csv_path)

                # Comparamos la amplitud para encontrar el 'w' resonante (mayor amplitud)
                if current_amplitude > max_amplitude_for_k:
                    max_amplitude_for_k = current_amplitude
                    resonant_w_for_k = w0_value

        # Guardamos los valores una vez que terminamos de recorrer todos los 'w' para el k actual
        if k_value is not None and resonant_w_for_k is not None:
            k_values.append(k_value)
            resonant_w_values.append(resonant_w_for_k)
            max_amplitudes_for_w.append(max_amplitude_for_k)

    return k_values, resonant_w_values, max_amplitudes_for_w


# Generamos los 'w0' para cada k
base_directory = 'outputs/multiple'
k_values, w0_values, max_amplitudes = traverse_directories(base_directory)

# Convertir a arrays de numpy
k_values = np.array(k_values)
w0_values = np.array(w0_values)

# Calcular sqrt(k)
sqrt_k_values = np.sqrt(k_values)

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.scatter(sqrt_k_values, w0_values, c='blue', s=50)
plt.xlabel(r'$k^{1/2}$ (N/m)')
plt.xlabel('frecuencia angular' + '$\omega$ (rad/s)')
#plt.ylabel(r'$\omega$ (rad/s)')

#plt.scatter(sqrt_k_values, w0_values, c=max_amplitudes, cmap='plasma', label='Frecuencias de resonancia')
#plt.colorbar(label='Amplitud Máxima')
#
#plt.xlabel(r'$k^{1/2}$ (N/m)')
#plt.ylabel(r'$\omega$ (rad/s)')
#plt.legend(loc='best')


# Añadir una línea de tendencia
z = np.polyfit(sqrt_k_values, w0_values, 1)
p = np.poly1d(z)
plt.plot(sqrt_k_values, p(sqrt_k_values), "r--", alpha=0.8)

# Mostrar el gráfico
plt.show()

# Guardar el gráfico
output_path = os.path.join(base_directory, 'w0_vs_sqrt_k.png')
plt.savefig(output_path)
plt.close()

print(f"Gráfico guardado en: {output_path}")
print("Proceso completado.")