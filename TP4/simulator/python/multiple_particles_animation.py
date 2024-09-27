import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Leer el archivo CSV desde el directorio coupled_beeman
df = pd.read_csv('outputs/coupled_beeman/particle.csv')

# Filtrar los tiempos únicos
times = df['time'].unique()

# Constante de distancia para la posición en x
distance = 10e-3  # Ajusta esta constante según tu configuración

# Crear la figura y el eje
fig, ax = plt.subplots()
ax.set_xlim(0, distance*100)  # Establecer los límites del eje x (ajusta según tus datos)
ax.set_ylim(-10e-2, 10e-2)  # Establecer los límites del eje y (ajusta según tus datos)
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
    x_positions = particle_indices * distance

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
