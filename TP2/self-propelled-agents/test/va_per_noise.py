import os
import matplotlib.pyplot as plt


def read_order_file(filename) -> float:
    # Lee el único float en el archivo 'orders'
    with open(filename, 'r') as file:
        order = float(file.readline())
    return order


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
    plt.legend()

    # Mostrar la gráfica
    plt.grid(True)
    plt.show()


def gather_and_plot_data(root_dir):
    orders_info_dict = {}

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)
        if os.path.isdir(folder_path):
            orders_file = os.path.join(folder_path, 'prom_order')
            if os.path.exists(orders_file):
                noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                noise_value = float(noise_value_str)
                order_value = read_order_file(orders_file)

                N_L_value = folder_name.split('_')[0]  # Esto separa el valor N y L

                if N_L_value not in orders_info_dict:
                    orders_info_dict[N_L_value] = []

                orders_info_dict[N_L_value].append((noise_value, order_value))

    # Ordenar cada lista por valor de ruido antes de graficar
    for key in orders_info_dict:
        orders_info_dict[key].sort(key=lambda x: x[0])

    plot_orders(orders_info_dict)


# Llamada a la función principal con el directorio raíz que contiene las carpetas
root_directory = 'outputs'  # Ajusta esto al directorio donde están las carpetas /N40L3_n0,00, /N40L3_n0,25, etc.
gather_and_plot_data(root_directory)
