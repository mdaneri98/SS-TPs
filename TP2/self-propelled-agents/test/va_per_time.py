import os
import matplotlib.pyplot as plt
import numpy as np

def read_order_file(filename):
    time_values = []
    va_values = []

    with open(filename, 'r') as file:
        for line in file:
            time, va = line.split()
            time_values.append(int(time))
            va_values.append(float(va.replace(',', '.')))

    return time_values, va_values

def plot_time_vs_va(time_values, avg_va_values, std_va_values, noise_value, label):
    plt.errorbar(time_values, avg_va_values, yerr=std_va_values, marker='o', linestyle='-',
                 label=f'Noise: {noise_value}', capsize=5)

def gather_and_plot_data_for_all_noises(root_dir, label, num_iterations, target_noises):
    plt.figure(figsize=(10, 6))

    noise_values_dict = {}

    for i in range(num_iterations):
        iteration_dir = f'{root_dir}_{i}'
        for folder_name in os.listdir(iteration_dir):
            if folder_name.startswith(label):
                folder_path = os.path.join(iteration_dir, folder_name)
                if os.path.isdir(folder_path):
                    orders_file = os.path.join(folder_path, 'orders')
                    if os.path.exists(orders_file):
                        noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                        noise_value = float(noise_value_str)
                        if noise_value in target_noises:
                            if noise_value not in noise_values_dict:
                                noise_values_dict[noise_value] = []

                            time_values, va_values = read_order_file(orders_file)
                            noise_values_dict[noise_value].append(va_values)

    # Calcular promedio y desvío estándar
    for noise_value, all_va_values in noise_values_dict.items():
        avg_va_values = np.mean(all_va_values, axis=0)
        std_va_values = np.std(all_va_values, axis=0)

        # Selecciona cada décimo punto
        selected_indices = range(0, len(time_values), 20)
        selected_time_values = [time_values[i] for i in selected_indices]
        selected_avg_va_values = [avg_va_values[i] for i in selected_indices]
        selected_std_va_values = [std_va_values[i] for i in selected_indices]

        plot_time_vs_va(selected_time_values, selected_avg_va_values, selected_std_va_values, noise_value, label)

    plt.ylim(0, 1)
    plt.xlabel('Tiempo')
    plt.ylabel('Va')
    plt.legend(title="Noise Values")
    plt.grid(True)
    plt.show()

# Especifica la carpeta raíz, el prefijo de las carpetas, el número de iteraciones y los valores de ruido a considerar
root_directory = 'outputs'  # Directorio donde están las carpetas
label_prefix = 'N400L10'  # Prefijo para identificar las carpetas
num_iterations = 10  # Ajusta esto al número de iteraciones disponibles
noises = [0, 1, 3.50, 5]  # Lista de ruidos de interés

gather_and_plot_data_for_all_noises(root_directory, label_prefix, num_iterations, noises)
