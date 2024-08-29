import os
import matplotlib
matplotlib.use('TkAgg')  # O 'Qt5Agg', dependiendo de tu entorno
import matplotlib.pyplot as plt
import statistics


def read_order_file(filename):
    time_values = []
    va_values = []

    with open(filename, 'r') as file:
        for line in file:
            time, va = line.split()
            time_values.append(int(time))
            va_values.append(float(va.replace(',', '.')))

    return time_values, va_values


def plot_time_vs_va(time_values, va_values, noise_value, label):
    plt.plot(time_values, va_values, marker='o', linestyle='-', label=f'Noise: {noise_value}')


def gather_and_plot_data_for_all_noises(root_dir, label):
    plt.figure(figsize=(10, 6))

    for folder_name in os.listdir(root_dir):
        if folder_name.startswith(label):
            folder_path = os.path.join(root_dir, folder_name)
            if os.path.isdir(folder_path):
                orders_file = os.path.join(folder_path, 'orders')
                if os.path.exists(orders_file):
                    noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                    noise_value = float(noise_value_str)
                    if noise_value == 0.5:
                        time_values, va_values = read_order_file(orders_file)
                        plot_time_vs_va(time_values, va_values, noise_value, label)

    plt.ylim(0, 1)
    plt.xlabel('Tiempo')
    plt.ylabel('Va')
    plt.grid(True)
    plt.show()


# Especifica la carpeta raíz y el prefijo de las carpetas que deseas analizar
root_directory = 'outputs'  # Directorio donde están las carpetas
label_prefix = 'N400L10'  # Prefijo para identificar las carpetas

gather_and_plot_data_for_all_noises(root_directory, label_prefix)