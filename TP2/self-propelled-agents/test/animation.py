import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation

# Definimos las variables N, L y M a nivel del script
N = 0  # Número de partículas (será leído del archivo static.txt)
L = 0  # Tamaño del gráfico (será leído del archivo static.txt)
M = 0  # Valor adicional si es necesario (por ejemplo, para dimensiones adicionales)

min_radius = 1
default_color = 'black'


# Función para leer el archivo static.txt
def read_static_file(filename):
    global N, L
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        particles_info = []
        for idx in range(N):
            radius, color = file.readline().strip().split()
            radius = float(radius)
            particles_info.append((idx, radius, color))
    return (N, L, particles_info)


# Función para leer el archivo dynamic.txt
def read_dynamic_file(filename, N):
    timesteps = []
    with open(filename, 'r') as file:
        while True:
            time_line = file.readline().strip()
            if not time_line:
                break
            t = float(time_line)
            particle_states = []
            for i in range(N):
                values = file.readline().strip().split('\t')
                idx = int(values[0])
                x = float(values[1])
                y = float(values[2])
                v = float(values[3])
                theta = float(values[4])
                particle_states.append((idx, x, y, v, theta))
            timesteps.append((t, particle_states))
    return timesteps


# Función para actualizar la animación
def update(frame, arrows, timesteps):
    _, particle_states = timesteps[frame]
    for i, arrow in enumerate(arrows):
        idx, x, y, v, theta = particle_states[i]

        # Calculamos las componentes x e y de la velocidad
        u = v * np.cos(theta)
        w = v * np.sin(theta)

        # Actualizamos la posición y dirección de la flecha con cola
        arrow.set_positions((x - u, y - w), (x + u, y + w))

    return arrows


# Función principal para generar la animación
def animate_particles(static_file, dynamic_file):
    N, L, particles_info = read_static_file(static_file)
    timesteps = read_dynamic_file(dynamic_file, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    arrows = []
    for idx, radius, _ in particles_info:
        # Añadimos la flecha de velocidad con cola
        arrow = patches.FancyArrowPatch((0, 0), (0, 0), color='red', arrowstyle='-|>', mutation_scale=10)
        ax.add_patch(arrow)
        arrows.append(arrow)

    ani = FuncAnimation(fig, update, frames=len(timesteps), fargs=(arrows, timesteps), repeat=False, blit=False)
    plt.show()


# Función para mostrar un frame específico
def show_specific_frame(static_file, dynamic_file, frame_number):
    N, L, particles_info = read_static_file(static_file)
    timesteps = read_dynamic_file(dynamic_file, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    scatters = []
    quivers = []
    for idx, radius, _ in particles_info:
        scatter = patches.Circle((0, 0), max(radius, min_radius), fc=default_color)  # Radio mínimo de 0.5
        ax.add_patch(scatter)
        scatters.append(scatter)

        # Añadimos la flecha de velocidad
        if idx == 10:
            quiver = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='blue')
            quivers.append(quiver)
        else:
            quiver = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='red')
            quivers.append(quiver)

    # Actualizar el frame específico
    update(frame_number, scatters, quivers, timesteps)

    plt.show()


# Llamada a la función principal con los archivos correspondientes
animate_particles('static', 'dynamic')

# show_specific_frame('static.txt', 'dynamic.txt', 0)
