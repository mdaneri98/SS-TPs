import os
import matplotlib.pyplot as plt
import numpy as np

def read_order_file(filename) -> float:
    with open(filename, 'r') as file:
        order = float(file.readline())
    return order

def plot_orders(orders_info):
    plt.figure(figsize=(10, 6))

    orders_info.sort(key=lambda x: x[0])  # Ordenar por valor de densidad (eje X)
    densities, averages, std_devs = zip(*orders_info)

    plt.errorbar(densities, averages, yerr=std_devs, fmt='o-', capsize=5, label='Promedio con desviación estándar')

    plt.ylim(0, 1)
    plt.xlabel('Densidad')
    plt.ylabel('Va')
    plt.grid(True)
    plt.legend()
    plt.show()

def gather_and_plot_data(root_dir, num_iterations):
    orders_info_dict = {}

    for iteration in range(num_iterations):
        iteration_dir = f'{root_dir}_{iteration}'
        density_dir = os.path.join(iteration_dir, 'density')

        if os.path.exists(density_dir):
            for folder_name in os.listdir(density_dir):
                folder_path = os.path.join(density_dir, folder_name)
                if os.path.isdir(folder_path):
                    orders_file = os.path.join(folder_path, 'prom_order_density')
                    if os.path.exists(orders_file):
                        density_value_str = folder_name.split('_p')[-1].replace(',', '.')
                        density_value = float(density_value_str)
                        order_value = read_order_file(orders_file)

                        if density_value not in orders_info_dict:
                            orders_info_dict[density_value] = []

                        orders_info_dict[density_value].append(order_value)

    # Calcular promedio y desviación estándar
    orders_info = []
    for density_value, orders in orders_info_dict.items():
        average_order_value = np.mean(orders)
        std_dev_order_value = np.std(orders)
        orders_info.append((density_value, average_order_value, std_dev_order_value))

    # Graficar las densidades, los promedios y las desviaciones estándar
    plot_orders(orders_info)


root_directory = 'outputs'
num_iterations = 10
gather_and_plot_data(root_directory, num_iterations)
