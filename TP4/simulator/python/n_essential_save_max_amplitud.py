import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def get_k_folders(base_path='outputs/multiple/'):
    return [f for f in os.listdir(base_path) if f.startswith('k_')]


def get_verlet_folders(k_folder, base_path='outputs/multiple/'):
    k_path = os.path.join(base_path, k_folder)
    return [f for f in os.listdir(k_path) if f.startswith('verlet_')]


def process_folders(base_path='outputs/multiple/'):
    all_data = []
    for k_folder in get_k_folders(base_path):
        k_path = os.path.join(base_path, k_folder)
        k_value = float(k_folder.split('_')[1])

        for verlet_folder in get_verlet_folders(k_folder, base_path):
            folder_path = os.path.join(k_path, verlet_folder)

            # Leer los archivos CSV
            static_df = pd.read_csv(os.path.join(folder_path, 'static.csv'), header=None, skiprows=1)
            df = pd.read_csv(os.path.join(folder_path, 'particle.csv'))

            # Asignar nombres de columnas
            static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']

            # Obtener el valor de wf de static.csv (w usado en esa simulación)
            wf = float(static_df['wf'].values[0])

            # Calcular la amplitud máxima (posición máxima) en particle.csv
            max_amplitude = df['position'].abs().max()

            # Almacenar los datos
            all_data.append({
                'k': k_value,
                'w': wf,
                'max_amplitude': max_amplitude
            })

            # Guardar la amplitud máxima en un archivo
            with open(os.path.join(folder_path, 'max_amplitude.txt'), 'w') as f:
                f.write(f"k: {k_value}\nw: {wf}\nmax_amplitude: {max_amplitude}")

    return pd.DataFrame(all_data)


# --------- Save max_amplitud for k and w ---------
data = process_folders()
print("Proceso completado. Se han guardado los archivos max_amplitude.txt en cada carpeta.")
