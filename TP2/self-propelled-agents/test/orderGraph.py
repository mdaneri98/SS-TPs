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


def plot_orders(orders_info):
    # Desempaquetar los datos
    times, orders = zip(*orders_info)

    # Crear la gráfica
    plt.figure(figsize=(10, 6))
    plt.plot(times, orders, marker='o', linestyle='-', color='b', label='Order')

    # Ajustar la escala del eje Y entre 0 y 1
    plt.ylim(0, 1)

    # Etiquetas y título
    plt.xlabel('Time')
    plt.ylabel('Order')
    plt.title('Order vs Time')
    plt.legend()

    # Mostrar la gráfica
    plt.grid(True)
    plt.show()


orders_info = read_orders_file('orders_per_noise')
plot_orders(orders_info)