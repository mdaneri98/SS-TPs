import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Obtener todas las carpetas dentro de 'outputs/'
base_dir = 'python/outputs/'
pattern = os.path.join(base_dir, '**/particle.csv')  # Busca en subcarpetas también

# Buscar todos los archivos 'particle.csv' dentro de 'outputs/' y sus subcarpetas
csv_files = glob.glob(pattern, recursive=True)

# Leer y graficar cada archivo CSV en gráficos separados
for csv_file in csv_files:
    # Leer el archivo CSV
    df = pd.read_csv(csv_file, delimiter=',')

    # Crear una nueva figura para cada archivo
    plt.figure(figsize=(10, 6))

    # Graficar la posición de la partícula a lo largo del tiempo
    plt.plot(df['time'], df['position'], marker='o', linestyle='-', label=csv_file)

    # Configurar el gráfico
    plt.title(f'Oscilación de la Partícula - {csv_file}')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Posición (m)')
    plt.grid()

    # Limitar los ejes
    plt.xlim(df['time'].min(), df['time'].max())
    plt.ylim(df['position'].min() - 10, df['position'].max() + 10)

    # Agregar una línea horizontal en la posición 0
    plt.axhline(0, color='grey', linewidth=0.5, linestyle='--')

    # Mostrar la leyenda
    plt.legend(loc='upper right')

    # Mostrar el gráfico
    plt.show()
