import os
import pandas as pd
import matplotlib.pyplot as plt


def read_orders_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        orders_info = []
        for line in lines:
            data = line.strip().split('\t')
            noise = float(data[0])
            order = float(data[1])
            orders_info.append((noise, order))
    return orders_info


def plot_orders(orders_info_dict):
    plt.figure(figsize=(10, 6))

    for label, orders_info in orders_info_dict.items():
        noises, orders = zip(*orders_info)
        plt.plot(noises, orders, marker='o', linestyle='-', label=label)

    # Ajustar la escala del eje Y entre 0 y 1
    plt.ylim(0, 1)

    # Etiquetas y título
    plt.xlabel('Ruido')
    plt.ylabel('Va')
    # plt.title('Order vs Noise for Different Simulations')
    plt.legend()

    # Mostrar la gráfica
    plt.grid(True)
    plt.show()


def gather_and_plot_data(root_dir):
    orders_info_dict = {}

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)
        if os.path.isdir(folder_path):
            orders_file = os.path.join(folder_path, 'orders_per_noise')
            if os.path.exists(orders_file):
                orders_info = read_orders_file(orders_file)
                orders_info_dict[folder_name] = orders_info

    plot_orders(orders_info_dict)


# Llamada a la función principal con el directorio raíz que contiene las carpetas
root_directory = '.'  # Puedes cambiar esto al directorio donde están las carpetas /N100L7, /N400L7, etc.
gather_and_plot_data(root_directory)
