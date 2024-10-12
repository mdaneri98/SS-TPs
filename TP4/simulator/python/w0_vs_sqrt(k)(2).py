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

def traverse_directories(base_path):
    k_values = []
    w0_values = []
    max_amplitudes = {}

    for root, dirs, files in os.walk(base_path):
        if 'particle.csv' in files and 'static.csv' in files:
            particle_csv_path = os.path.join(root, 'particle.csv')
            static_csv_path = os.path.join(root, 'static.csv')

            k = get_k(static_csv_path)
            w = float(os.path.basename(root))  # Asumiendo que el nombre de la carpeta es el valor de w

            max_amplitude = process_particle_csv(particle_csv_path)

            if k not in max_amplitudes:
                max_amplitudes[k] = {'w': w, 'amplitude': max_amplitude}
            elif max_amplitude > max_amplitudes[k]['amplitude']:
                max_amplitudes[k] = {'w': w, 'amplitude': max_amplitude}

            k_values.append(k)

    # Obtener los w0 (w de máxima amplitud) para cada k
    w0_values = [max_amplitudes[k]['w'] for k in sorted(max_amplitudes.keys())]
    k_values = sorted(max_amplitudes.keys())

    return k_values, w0_values

# Generamos los 'w0' para cada k
base_directory = 'outputs/multiple'
k_values, w0_values = traverse_directories(base_directory)

# Convertir a arrays de numpy
k_values = np.array(k_values)
w0_values = np.array(w0_values)

# Calcular sqrt(k)
sqrt_k_values = np.sqrt(k_values)

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.scatter(sqrt_k_values, w0_values, c='blue', s=50)
plt.xlabel('k^(1/2)')
plt.ylabel('w_0 (frecuencia de resonancia)')
plt.title('w_0 en función de k^(1/2)')

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