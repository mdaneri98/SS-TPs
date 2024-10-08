import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Leer los archivos CSV
df = pd.read_csv('outputs/multiple/verlet_10.000000/particle.csv')
static_df = pd.read_csv('outputs/multiple/verlet_10.000000/static.csv', header=None, skiprows=1)

# Asignar nombres a las columnas
static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']

# Convertir los valores de las columnas a float (en caso de que sean strings)
n = float(static_df['n'].values[0])
k = float(static_df['k'].values[0])
mass = float(static_df['mass'].values[0])
distance = float(static_df['distance'].values[0])
amplitud = float(static_df['amplitud'].values[0])

# Definir el nuevo timestep
new_timestep = 0.05  # Por ejemplo, 0.05 segundos

# Filtrar los tiempos únicos
times = df['time'].unique()

# Quedarse solo con los tiempos que sean múltiplos del nuevo timestep
times = times[(times % new_timestep) < 1e-4]

# Crear la figura y el eje
fig, ax = plt.subplots()
ax.set_xlim(0, distance * n)  # Usar la distancia del archivo estático para x
ax.set_ylim(-(1.1*amplitud), amplitud*1.1)  # Usar amplitud para los límites de y
ax.set_xlabel('Distance (Index * distance)')
ax.set_ylabel('Position (Vertical)')

# Inicializar el gráfico de dispersión con un color por defecto
scatter = ax.scatter([], [], s=50, c='blue')

# Inicializar la línea que conectará los puntos
line, = ax.plot([], [], lw=2, color='blue')


# Función para actualizar la animación en cada frame
def update(frame):
    current_time = times[frame]

    # Filtrar los datos del tiempo actual
    current_data = df[df['time'] == current_time]

    # Calcular la posición en x como el índice de la partícula multiplicado por la distancia
    particle_indices = current_data['id']
    x_positions = particle_indices * distance  # Usar la distancia del archivo estático

    # La posición en y será la posición vertical
    y_positions = current_data['position']

    # Crear un array de colores
    colors = ['red' if id == 0 else 'blue' for id in particle_indices]

    # Actualizar los datos del gráfico de dispersión
    scatter.set_offsets(list(zip(x_positions, y_positions)))
    scatter.set_color(colors)

    # Actualizar la línea para conectar las partículas
    line.set_data(x_positions, y_positions)

    # Actualizar el título con el tiempo actual
    ax.set_title(f'Time: {current_time:.3f}')

    return scatter, line


# Crear la animación
anim = FuncAnimation(fig, update, frames=len(times), blit=False)

# Mostrar la animación
plt.show()
