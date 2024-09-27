import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Leer los archivos CSV
df = pd.read_csv('outputs/coupled_beeman/particle.csv')
static_df = pd.read_csv('outputs/coupled_beeman/static.csv', header=None, skiprows=1)

# Asignar nombres a las columnas
static_df.columns = ['b', 'k', 'mass', 'distance', 'amplitud']

# Convertir los valores de las columnas a float (en caso de que sean strings)
k = float(static_df['k'].values[0])
mass = float(static_df['mass'].values[0])
distance = float(static_df['distance'].values[0])
amplitud = float(static_df['amplitud'].values[0])

# Filtrar los tiempos únicos
times = df['time'].unique()

# Crear la figura y el eje
fig, ax = plt.subplots()
ax.set_xlim(0, distance * 100)  # Usar la distancia del archivo estático para x
ax.set_ylim(-amplitud, amplitud)  # Usar amplitud para los límites de y
ax.set_xlabel('Distance (Index * distance)')
ax.set_ylabel('Position (Vertical)')

# Inicializar el gráfico de dispersión
scatter = ax.scatter([], [], s=50)

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

    # Actualizar los datos del gráfico de dispersión
    scatter.set_offsets(list(zip(x_positions, y_positions)))

    # Actualizar el título con el tiempo actual
    ax.set_title(f'Time: {current_time:.3f}')
    return scatter,

# Crear la animación
anim = FuncAnimation(fig, update, frames=len(times), interval=200, blit=True)

# Mostrar la animación
plt.show()
