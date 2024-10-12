import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Función para buscar las carpetas con la estructura verlet_{numero_de_w_usado}
def get_verlet_folders(base_path='outputs/multiple/k_100.000000'):
    folders = [f for f in os.listdir(base_path) if f.startswith('verlet_')]
    return folders

# Listas para almacenar los valores de w y las amplitudes máximas
w_values = []
max_amplitudes = []

# Recorrer cada carpeta verlet_{numero_de_w_usado}
for folder in get_verlet_folders():
    # Leer los archivos CSV
    static_df = pd.read_csv(f'outputs/multiple/k_100.000000/{folder}/static.csv', header=None, skiprows=1)
    df = pd.read_csv(f'outputs/multiple/k_100.000000/{folder}/particle.csv')

    # Asignar nombres de columnas
    static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']

    # Obtener el valor de wf de static.csv (w usado en esa simulación)
    wf = float(static_df['wf'].values[0])

    # Calcular la amplitud máxima (posición máxima) en particle.csv
    max_amplitude = df['position'].abs().max()

    # Almacenar los valores de wf y la amplitud máxima
    w_values.append(wf)
    max_amplitudes.append(max_amplitude)

# Convertir las listas a arrays numpy para mayor facilidad
w_values = np.array(w_values)
max_amplitudes = np.array(max_amplitudes)

# Ordenar los valores de w y sus respectivas amplitudes máximas
sorted_indices = np.argsort(w_values)
w_values = w_values[sorted_indices]
max_amplitudes = max_amplitudes[sorted_indices]

# Graficar la amplitud máxima en función de w
plt.figure(figsize=(8, 6))
plt.plot(w_values, max_amplitudes, marker='o', linestyle='-', color='blue')
plt.title('Amplitud máxima en función de la frecuencia angular externa')
plt.xlabel('')
plt.ylabel('')
plt.grid(True)

# Guardar la gráfica en outputs/multiple/amplitud_vs_w.jpg
output_path = 'outputs/multiple/amplitud_vs_w.jpg'
plt.savefig(output_path, format='jpg')
#plt.show()
