import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos desde un archivo de texto
file_path = 'borrar'

# Leer el archivo y crear un DataFrame
data = pd.read_csv(file_path, header=None, names=['datos'])

# Calcular media y desviación estándar
mean = data['datos'].mean()
std_dev = data['datos'].std()

# Crear una figura y ejes
plt.figure(figsize=(10, 6))

# Graficar los datos
plt.plot(data['datos'], label='Datos', color='blue', alpha=0.5, marker='o')

# Agregar líneas para la media y la desviación estándar
plt.axhline(mean, color='red', linestyle='--', label='Media')
plt.axhline(mean + std_dev, color='green', linestyle='--', label='Media + 1 Desv. Est.')
plt.axhline(mean - std_dev, color='green', linestyle='--', label='Media - 1 Desv. Est.')

# Configurar el gráfico
plt.title('Gráfico de Media y Desviación Estándar')
plt.xlabel('Índice')
plt.ylabel('Valor')
plt.legend()
plt.grid()

# Mostrar el gráfico
plt.show()
