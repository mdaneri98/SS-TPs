import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

def read_order_file(filename) -> float:
    # Lee el único float en el archivo 'prom_order'
    with open(filename, 'r') as file:
        order = float(file.readline())
    return order

def plot_orders(orders_info_dict):
    plt.figure(figsize=(10, 6))

    for label, orders_info in orders_info_dict.items():
        noises, averages, std_devs = zip(*orders_info)
        plt.errorbar(noises, averages, yerr=std_devs, marker='o', linestyle='-', label=label, capsize=5)

    # Ajustar la escala del eje Y entre 0 y 1
    plt.ylim(0, 1)

    # Etiquetas y título
    plt.xlabel('Ruido')
    plt.ylabel('Promedio de Va')
    plt.legend()

    # Mostrar la gráfica
    plt.grid(True)
    plt.show()

def gather_and_plot_data(root_dir, num_iterations):
    orders_info_dict = defaultdict(list)

    for i in range(0, num_iterations):
        iteration_dir = f'{root_dir}_{i}'
        for folder_name in os.listdir(iteration_dir):
            folder_path = os.path.join(iteration_dir, folder_name)
            if os.path.isdir(folder_path):
                orders_file = os.path.join(folder_path, 'prom_order')
                if os.path.exists(orders_file):
                    noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                    noise_value = float(noise_value_str)
                    order_value = read_order_file(orders_file)

                    N_L_value = folder_name.split('_')[0]  # Esto separa el valor N y L

                    orders_info_dict[(N_L_value, noise_value)].append(order_value)

    # Calcular el promedio y el desvío estándar de 'order' para cada (N_L_value, noise_value)
    averaged_orders_info_dict = defaultdict(list)
    for (N_L_value, noise_value), orders in orders_info_dict.items():
        average_order = np.mean(orders)
        std_dev_order = np.std(orders)
        averaged_orders_info_dict[N_L_value].append((noise_value, average_order, std_dev_order))

    # Ordenar cada lista por valor de ruido antes de graficar
    for key in averaged_orders_info_dict:
        averaged_orders_info_dict[key].sort(key=lambda x: x[0])

    plot_orders(averaged_orders_info_dict)

# Llamada a la función principal con el directorio raíz y el número de iteraciones
root_directory = 'outputs'  # Ajusta esto al directorio base
num_iterations = 10  # Ajusta esto al número de iteraciones disponibles
gather_and_plot_data(root_directory, num_iterations)
