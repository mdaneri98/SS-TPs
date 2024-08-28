import os
import matplotlib.pyplot as plt


def read_order_file(filename) -> float:
    with open(filename, 'r') as file:
        order = float(file.readline())
    return order


def plot_orders(orders_info_dict):
    plt.figure(figsize=(10, 6))

    for label, orders_info in orders_info_dict.items():
        # Asegurarse de que los datos estén ordenados correctamente
        orders_info.sort(key=lambda x: x[0])  # Ordenar por valor de ruido (eje X)
        noises, orders = zip(*orders_info)

        plt.plot(noises, orders, marker='o', linestyle='-', label=label)

    plt.ylim(0, 1)
    plt.xlabel('Densidad')
    plt.ylabel('Va')
    plt.legend()
    plt.grid(True)
    plt.show()


def gather_and_plot_data(root_dir):
    orders_info_dict = {}

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)
        if os.path.isdir(folder_path):
            orders_file = os.path.join(folder_path, 'prom_order-density')
            if os.path.exists(orders_file):
                noise_value_str = folder_name.split('_n')[-1].replace(',', '.')
                noise_value = float(noise_value_str)
                order_value = read_order_file(orders_file)

                N_L_value = folder_name.split('_')[0]

                if N_L_value not in orders_info_dict:
                    orders_info_dict[N_L_value] = []

                orders_info_dict[N_L_value].append((noise_value, order_value))

    plot_orders(orders_info_dict)


root_directory = 'outputs/density'
gather_and_plot_data(root_directory)
