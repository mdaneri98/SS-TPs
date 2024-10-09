import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_mse(positions1, positions2):
    """Calcula el error cuadrático medio entre dos listas de posiciones."""
    return np.mean((positions1 - positions2) ** 2)

def plot_solutions(time, analitic_positions, numeric_positions, method_name, timestep, save_path):
    """Grafica las posiciones analítica y numérica."""
    plt.figure(figsize=(10, 6))
    plt.plot(time, analitic_positions, label='Solución Analítica', color='blue', linestyle='--')
    plt.plot(time, numeric_positions, label=f'Solución Numérica ({method_name})', color='red')
    plt.xlabel('Tiempo')
    plt.ylabel('Posición')
    plt.title(f'Soluciones Analítica y Numérica - Método: {method_name}, Timestep: {timestep}')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    print(f'Gráfico guardado en: {save_path}')

def process_files(base_dir):
    methods = ['analitic', 'beeman', 'verlet','gear']

    # Obtener todos los timesteps disponibles
    timesteps = set()
    for dirname in os.listdir(base_dir):
        for method in methods:
            if dirname.startswith(f'{method}_'):
                timesteps.add(dirname.split('_')[1])

    for timestep in timesteps:
        analitic_file = os.path.join(base_dir, f'analitic_{timestep}', 'particle.csv')

        if not os.path.exists(analitic_file):
            print(f'No se encontró el archivo analítico para timestep {timestep}')
            continue

        analitic_df = pd.read_csv(analitic_file)
        analitic_positions = analitic_df.set_index(['time', 'id'])['position']
        analitic_time = analitic_df['time'].unique()

        for method in methods:
            if method == 'analitic':
                continue  # No comparamos analítico consigo mismo

            method_file = os.path.join(base_dir, f'{method}_{timestep}', 'particle.csv')

            if not os.path.exists(method_file):
                print(f'No se encontró el archivo para el método {method} con timestep {timestep}')
                continue

            particles_df = pd.read_csv(method_file)
            numeric_positions = particles_df.set_index(['time', 'id'])['position']
            numeric_time = particles_df['time'].unique()

            common_index = numeric_positions.index.intersection(analitic_positions.index)

            if len(common_index) > 0:
                mse = calculate_mse(numeric_positions.loc[common_index], analitic_positions.loc[common_index])

                # Guardar MSE
                mse_dir = os.path.join(base_dir, f'{method}_{timestep}')
                os.makedirs(mse_dir, exist_ok=True)
                mse_file_path = os.path.join(mse_dir, 'mse.txt')
                with open(mse_file_path, 'w') as mse_file:
                    mse_file.write(f'MSE: {mse}\n')
                print(f'MSE calculado para {method}_{timestep} y guardado en {mse_file_path}')

                # Graficar soluciones
                plot_dir = os.path.join(mse_dir, 'plots')
                os.makedirs(plot_dir, exist_ok=True)
                plot_path = os.path.join(plot_dir, f'{method}_{timestep}_plot.png')
                plot_solutions(analitic_time, analitic_positions.loc[common_index], numeric_positions.loc[common_index], method, timestep, plot_path)
            else:
                print(f'No hay partículas comunes en {method}_{timestep} y el archivo analítico.')

if __name__ == '__main__':
    base_dir = 'outputs/individuals'  # Directorio base
    process_files(base_dir)