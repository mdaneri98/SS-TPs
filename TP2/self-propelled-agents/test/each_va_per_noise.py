import os
import matplotlib
import statistics

matplotlib.use('TkAgg')  # O 'Qt5Agg', dependiendo de tu entorno
import matplotlib.pyplot as plt

def read_order_file(filename):
    va_values = []
    with open(filename, 'r') as file:
        for line in file:
            _, va = line.split()  # Ignorar el tiempo
            va_values.append(float(va.replace(',', '.')))

    return va_values

def plot_va_vs_noise(noise_values, va_means, va_stds):
    plt.errorbar(noise_values, va_means, yerr=va_stds, marker='o', linestyle='-', capsize=5)
    plt.ylim(0, 1)
    plt.xlabel('Ruido')
    plt.ylabel('Va')
    plt.grid(True)

def gather_and_plot_data_for_all_noises(root_dir, label):
    noise_values = []
    va_means = []
    va_stds = []

    for folder_name in os.listdir(root_dir):
        if folder_name.startswith(label):
            folder_path = os.path.join(root_dir, folder_name)
            if os.path.isdir(folder_path):
                orders_file = os.path.join(folder_path, 'orders')
                if os.path.exists(orders_file):
                    noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                    noise_value = float(noise_value_str)
                    va_values = read_order_file(orders_file)
                    # Obtener los últimos 100 valores
                    last_100_values = va_values[-100:]

                    mean_va = statistics.mean(last_100_values)
                    std_dev_va = statistics.stdev(last_100_values) if len(last_100_values) > 1 else 0

                    noise_values.append(noise_value)
                    va_means.append(mean_va)
                    va_stds.append(std_dev_va)

    # Crear el gráfico Va vs. Ruido
    plt.figure(figsize=(10, 6))
    plot_va_vs_noise(noise_values, va_means, va_stds)
    plt.show()

# Especifica la carpeta raíz y el prefijo de las carpetas que deseas analizar
root_directory = 'outputs'  # Directorio donde están las carpetas
label_prefix = 'N40L3'  # Prefijo para identificar las carpetas

gather_and_plot_data_for_all_noises(root_directory, label_prefix)

