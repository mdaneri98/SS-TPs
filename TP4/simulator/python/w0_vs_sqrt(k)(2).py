import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def process_particle_csv(file_path):
    df = pd.read_csv(file_path)
    max_amplitude = df['position'].abs().max()
    return max_amplitude


def get_k_and_w0(static_csv_path):
    static_df = pd.read_csv(static_csv_path, header=None, skiprows=1)
    static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']
    return float(static_df['k'].values[0]), float(static_df['w0'].values[0])


def traverse_directories(base_path):
    k_values = []
    w0_values = []
    max_amplitudes = []

    for root, dirs, files in os.walk(base_path):
        if 'particle.csv' in files and 'static.csv' in files:
            particle_csv_path = os.path.join(root, 'particle.csv')
            static_csv_path = os.path.join(root, 'static.csv')

            max_amplitude = process_particle_csv(particle_csv_path)
            k, w0 = get_k_and_w0(static_csv_path)

            k_values.append(k)
            w0_values.append(w0)
            max_amplitudes.append(max_amplitude)

    return k_values, w0_values, max_amplitudes


# --- Generamos los 'max_amplitud' para cada k, w ---
base_directory = 'outputs/multiple'

# Iniciar el recorrido de directorios
k_values, w0_values, max_amplitudes = traverse_directories(base_directory)

# --- Generamos los 'max_amplitud' para cada k, w ---
k_values = np.array(k_values)
w0_values = np.array(w0_values)
max_amplitudes = np.array(max_amplitudes)

# Calcular sqrt(k)
sqrt_k_values = np.sqrt(k_values)

# Crear el gráfico
plt.figure(figsize=(10, 6))
scatter = plt.scatter(sqrt_k_values, w0_values, c=max_amplitudes, cmap='viridis', s=50)
plt.colorbar(scatter, label='Max Amplitude')

plt.xlabel('')
plt.ylabel('')
plt.title('w_0 en función de k^(1/2)')

# Añadir una línea de tendencia
z = np.polyfit(sqrt_k_values, w0_values, 1)
p = np.poly1d(z)
plt.plot(sqrt_k_values, p(sqrt_k_values), "r--", alpha=0.8)
plt.show()

# Guardar el gráfico
output_path = os.path.join(base_directory, 'w0_vs_sqrt_k.png')
#plt.savefig(output_path)
#plt.close()

print(f"Gráfico guardado en: {output_path}")
print("Proceso completado.")
