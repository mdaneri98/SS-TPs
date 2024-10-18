import matplotlib.pyplot as plt

# Función para leer las coordenadas desde el archivo
def read_data(archivo):
    x = []
    y = []
    with open(archivo, 'r') as f:
        for linea in f:
            # Separar las columnas por tabulador
            columnas = linea.strip().split('\t')  # Asumiendo separación por tabulador
            x.append(float(columnas[0]))  # Columna 1: X (abscisa - tiempo)
            y.append(float(columnas[1]))  # Columna 2: Y (ordenada - presión)
    return x, y

# Archivos de datos con las coordenadas
wall_data_file = 'output/wall_pressures.txt'  # Reemplaza con el nombre de tu archivo
static_data_file = 'output/static_pressures.txt'  # Reemplaza con el nombre de tu archivo

# Leer los datos del archivo para las paredes
x_wall, y_wall = read_data(wall_data_file)

# Leer los datos del archivo para la partícula estática
x_static, y_static = read_data(static_data_file)

# Generar el gráfico
plt.plot(x_wall, y_wall, 'o-', label='Presión en Paredes')  # 'o-' dibuja puntos conectados por líneas
plt.plot(x_static, y_static, 's-', label='Presión en Partícula Estática')  # 's-' dibuja cuadrados conectados por líneas

# Etiquetas y leyenda
plt.xlabel('Tiempo')
plt.ylabel('Presión')
plt.legend()
plt.grid(True)

# Mostrar el gráfico
plt.show()
