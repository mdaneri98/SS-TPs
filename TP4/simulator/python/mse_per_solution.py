import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Función para calcular la diferencia cuadrada punto por punto
def calculate_mse_per_point(reference, target):
    return (reference - target) ** 2

# Cargar los archivos CSV en dataframes
base_dir = 'outputs/'
analitic_data = pd.read_csv(base_dir + 'analitic/particle.csv')
verlet_data = pd.read_csv(base_dir + 'verlet/particle.csv')
beeman_data = pd.read_csv(base_dir + 'beeman/particle.csv')

# Obtener las posiciones de las partículas
analitic_positions = analitic_data['position']
verlet_positions = verlet_data['position']
beeman_positions = beeman_data['position']

# Calcular el MSE para cada punto (posición) de Verlet y Beeman respecto a Analitic
mse_verlet_per_point = calculate_mse_per_point(analitic_positions, verlet_positions)
mse_beeman_per_point = calculate_mse_per_point(analitic_positions, beeman_positions)

# Crear un DataFrame para almacenar los resultados
mse_results = pd.DataFrame({
    'time': analitic_data['time'],  # Incluimos la columna de tiempo
    'mse_verlet': mse_verlet_per_point,
    'mse_beeman': mse_beeman_per_point
})

# Guardar los resultados en un nuevo archivo CSV (opcional)
mse_results.to_csv(base_dir + 'mse_results.csv', index=False)

# Graficar MSE para Verlet y Beeman respecto a Analitic
plt.figure(figsize=(12, 6))

# Gráfico de MSE entre Analitic y Verlet
plt.subplot(1, 2, 1)
plt.plot(mse_results['time'], mse_results['mse_verlet'], label='MSE Verlet', color='blue')
plt.xlabel('Time')
plt.ylabel('MSE')
plt.title('MSE: Verlet vs Analitic')
plt.grid(True)
plt.legend()

# Gráfico de MSE entre Analitic y Beeman
plt.subplot(1, 2, 2)
plt.plot(mse_results['time'], mse_results['mse_beeman'], label='MSE Beeman', color='green')
plt.xlabel('Time')
plt.ylabel('MSE')
plt.title('MSE: Beeman vs Analitic')
plt.grid(True)
plt.legend()

# Mostrar los gráficos
plt.tight_layout()
plt.show()
