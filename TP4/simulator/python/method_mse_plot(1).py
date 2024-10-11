import os
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_csv_file(base_dir, method, timestep):
    pattern = os.path.join(base_dir, f"{method}_{timestep}/particle.csv")
    files = glob.glob(pattern)
    return files[0] if files else None


def calculate_cumulative_mse(reference, target):
    squared_diff = (reference - target) ** 2
    cumulative_sum = np.cumsum(squared_diff)
    return cumulative_sum / np.arange(1, len(cumulative_sum) + 1)


def generate_mse_errors_and_plot(base_dir):
    timesteps = ['0.010000', '0.001000', '0.000100', '0.000010', '0.000001']
    methods = ['gear', 'verlet', 'beeman']

    results = []

    for timestep in timesteps:
        # Buscar archivo analítico para el timestep actual
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
            # Buscar archivo del método numérico para el timestep actual
            method_file = find_csv_file(base_dir, method, timestep)
            if not method_file:
                print(f"Warning: {method} file not found for timestep {timestep}")
                continue

            try:
                method_data = pd.read_csv(method_file)
            except Exception as e:
                print(f"Error reading {method} file for timestep {timestep}: {e}")
                continue

            # Asegurarse de que ambos datasets tengan la misma longitud
            min_length = min(len(analytic_data), len(method_data))
            analytic_positions = analytic_data['position'][:min_length].values
            method_positions = method_data['position'][:min_length].values

            # Calcular el MSE acumulativo
            cumulative_mse = calculate_cumulative_mse(analytic_positions, method_positions)
            final_mse = cumulative_mse[-1]  # Usar el último valor del MSE acumulativo

            results.append({
                'timestep': float(timestep),
                'method': method,
                'mse': final_mse
            })

    # Crear un DataFrame con los resultados
    results_df = pd.DataFrame(results)

    if results_df.empty:
        print("No data to plot. Check if the files exist and the directory structure is correct.")
        return

    # Graficar los resultados
    plt.figure(figsize=(10, 6))
    for method in methods:
        method_data = results_df[results_df['method'] == method]
        plt.plot(method_data['timestep'], method_data['mse'], marker='o', label=method)

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Paso de tiempo (s)')
    plt.ylabel('MSE (m^2)')
    plt.title('Comparación del MSE según el paso temporal')
    plt.legend()
    plt.grid(True)

    # Mostrar el gráfico sin guardarlo
    plt.show()


# Directorio base general
base_dir = 'outputs/individuals/'

# Ejecutar la función para calcular el MSE y generar el gráfico
generate_mse_errors_and_plot(base_dir)
