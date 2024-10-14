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
    return float(static_df['k'].values[0]), float(static_df['wf'].values[0])

def traverse_directories(base_path):
    k_values = []
    resonant_w_values = []
    max_amplitudes_for_w = []

    for root_k, dirs_k, files_k in os.walk(base_path):
        if root_k == base_path:
            continue

        max_amplitude_for_k = -1
        resonant_w_for_k = None
        k_value = None

        for dir_w in dirs_k:
            root_w = os.path.join(root_k, dir_w)
            files_w = os.listdir(root_w)

            if 'particle.csv' in files_w and 'static.csv' in files_w:
                particle_csv_path = os.path.join(root_w, 'particle.csv')
                static_csv_path = os.path.join(root_w, 'static.csv')

                current_amplitude = process_particle_csv(particle_csv_path)

                k_value, w0_value = get_k_and_w0(static_csv_path)

                if current_amplitude > max_amplitude_for_k:
                    max_amplitude_for_k = current_amplitude
                    resonant_w_for_k = w0_value

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
plt.ylabel(r'frecuencia (rad/s)')

# Añadir la recta y = x
plt.plot(sqrt_k_values, sqrt_k_values, "g-", label="y = x")

# Añadir la línea de tendencia ajustada (recta de ajuste)
z = np.polyfit(sqrt_k_values, w0_values, 1)
p = np.poly1d(z)
plt.plot(sqrt_k_values, p(sqrt_k_values), "r--", alpha=0.8, label="Línea de tendencia")

# Calcular el MSE entre w0_values y sqrt_k_values (recta y = x)
mse = np.mean((w0_values - sqrt_k_values) ** 2)
print(f"Error Cuadrático Medio (MSE) entre la recta y=x y la línea de tendencia: {mse}")

# Mostrar el MSE en el gráfico
plt.title(f"")
plt.legend(loc='best')

# Mostrar el gráfico
plt.show()

# Guardar el gráfico
output_path = os.path.join(base_directory, 'w0_vs_sqrt_k_mse.png')
plt.savefig(output_path)
plt.close()

print(f"Gráfico guardado en: {output_path}")
print("Proceso completado.")
