import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Leer el archivo CSV desde el directorio coupled_beeman
df = pd.read_csv('outputs/coupled_beeman/particle.csv')

# Filtrar los tiempos únicos
times = df['time'].unique()

# Crear la figura y el eje
fig, ax = plt.subplots()
ax.set_xlim(0, 10)  # Establecer los límites del eje x (ajusta según tus datos)
ax.set_ylim(-5, 5)  # Establecer los límites del eje y (ajusta según tus datos)
ax.set_xlabel('Position')
ax.set_ylabel('Velocity')

# Inicializar el gráfico de dispersión
scatter = ax.scatter([], [], s=50)

# Función para actualizar la animación en cada frame
def update(frame):
    current_time = times[frame]

    # Filtrar los datos del tiempo actual
    current_data = df[df['time'] == current_time]

    # Actualizar las posiciones y las velocidades de las partículas
    positions = current_data['position']
    velocities = current_data['velocity']

    # Actualizar los datos del gráfico de dispersión
    scatter.set_offsets(list(zip(positions, velocities)))

    # Actualizar el título con el tiempo actual
    ax.set_title(f'Time: {current_time:.3f}')
    return scatter,

# Crear la animación
anim = FuncAnimation(fig, update, frames=len(times), interval=200, blit=True)

# Mostrar la animación
plt.show()
