import pandas as pd
import matplotlib.pyplot as plt

def read_static_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        orders_info = []
        for line in lines:
            time = int(line[0])
            order = float(line[1])
            orders_info.append((time, order))
    return orders_info


# Leer el archivo con columnas separadas por tabuladores
df = pd.read_csv('C:\Users\Admin\Desktop\SS-TPs\TP2\self-propelled-agents\test\orders', sep='\t')

# Asumiendo que la primera columna es el tiempo y la segunda es el parámetro de orden
tiempo = df.iloc[:, 0]
parametro_orden = df.iloc[:, 1]

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.plot(parametro_orden, tiempo, marker='o', linestyle='-')
plt.xlabel('Parámetro de Orden (Eje X)')
plt.ylabel('Tiempo (Eje Y)')
plt.title('Gráfico de Tiempo vs Parámetro de Orden')
plt.grid(True)

# Mostrar el gráfico
plt.show()
