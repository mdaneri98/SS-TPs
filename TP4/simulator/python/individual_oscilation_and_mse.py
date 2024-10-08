import os
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_analitic_and_numeric(base_dir, pattern):
    csv_files = glob.glob(pattern, recursive=True)

    # Leer y graficar cada archivo CSV en gráficos separados
    for csv_file in csv_files:
        # Leer el archivo CSV
        df = pd.read_csv(csv_file, delimiter=',')

        # Crear una nueva figura para cada archivo
        plt.figure(figsize=(10, 6))

        # Graficar la posición de la partícula a lo largo del tiempo
        plt.plot(df['time'], df['position'], marker='o', linestyle='-', label=csv_file)

        # Configurar el gráfico
        plt.title(f'Oscilación de la Partícula - {csv_file}')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Posición (m)')
        plt.grid()

        # Limitar los ejes
        plt.xlim(df['time'].min(), df['time'].max())
        plt.ylim(df['position'].min() - 0.05, df['position'].max() + 0.05)

        # Agregar una línea horizontal en la posición 0
        plt.axhline(0, color='grey', linewidth=0.5, linestyle='--')

        # Mostrar la leyenda
        plt.legend(loc='upper right')

        # Mostrar el gráfico
        plt.show()


def find_csv_file(base_dir, method, timestep):
    pattern = os.path.join(base_dir, f"{method}_{timestep}/particle.csv")
    files = glob.glob(pattern)
    return files[0] if files else None


def calculate_cumulative_mse(reference, target):
    squared_diff = (reference - target) ** 2
    cumulative_sum = np.cumsum(squared_diff)
    return cumulative_sum / np.arange(1, len(cumulative_sum) + 1)


def generate_mse_errors_for_all(base_dir):
    timesteps = ['0.000010', '0.000100', '0.001000', '0.010000']
    methods = ['verlet', 'beeman']

    results = []

    for timestep in timesteps:
        analytic_file = find_csv_file(base_dir, 'analitic', timestep)
        if not analytic_file:
            print(f"Warning: Analytic file not found for timestep {timestep}")
            continue

        try:
            analytic_data = pd.read_csv(analytic_file)
        except Exception as e:
            print(f"Error reading analytic file for timestep {timestep}: {e}")
            continue

        for method in methods:
            method_file = find_csv_file(base_dir, method, timestep)
            if not method_file:
                print(f"Warning: {method} file not found for timestep {timestep}")
                continue

            try:
                method_data = pd.read_csv(method_file)
            except Exception as e:
                print(f"Error reading {method} file for timestep {timestep}: {e}")
                continue

            # Ensure both datasets have the same length
            min_length = min(len(analytic_data), len(method_data))
            analytic_positions = analytic_data['position'][:min_length].values
            method_positions = method_data['position'][:min_length].values

            cumulative_mse = calculate_cumulative_mse(analytic_positions, method_positions)
            final_mse = cumulative_mse[-1]  # Now it's a numpy array, so -1 indexing works

            results.append({
                'timestep': float(timestep),
                'method': method,
                'mse': final_mse
            })

    # Create a DataFrame with the results
    results_df = pd.DataFrame(results)

    if results_df.empty:
        print("No data to plot. Check if the files exist and the directory structure is correct.")
        return results_df

    # Plot the results
    plt.figure(figsize=(10, 6))
    for method in methods:
        method_data = results_df[results_df['method'] == method]
        plt.plot(method_data['timestep'], method_data['mse'], marker='o', label=method)

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('s')
    plt.ylabel('m^2')
    plt.title('MSE respecto del paso temporal')
    plt.legend()
    plt.grid(True)

    # Save the plot
    plt.savefig(os.path.join(base_dir, '..', 'mse_comparison.png'))
    plt.close()

    # Save the results to a CSV file
    results_df.to_csv(os.path.join(base_dir, '..', 'mse_results.csv'), index=False)

    return results_df


# Obtener todas las carpetas dentro de 'outputs/'
base_dir = 'outputs/individual'
pattern = os.path.join(base_dir, '**/particle.csv')  # Busca en subcarpetas también

mse_results = generate_mse_errors_for_all(base_dir)
