import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation
from models import Particle

# Definimos las variables N, L y M a nivel del script
N = 0  # Número de partículas (será leído del archivo static.txt)
L = 0  # Tamaño del gráfico (será leído del archivo static.txt)
M = 0  # Valor adicional si es necesario (por ejemplo, para dimensiones adicionales)

# Función para leer el archivo static.txt
def read_static_file(filename):
    global N, L
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        particles_info = []
        for idx in range(N):
            radius, mass, color = file.readline().strip().split('\t')
            radius = float(radius)
            particles_info.append((idx, radius, mass, color))
    return (N, L, particles_info)


# Función para leer el archivo dynamic.txt
def read_dynamic_file(filename, particles_info, N):
    states = []
    with open(filename, 'r') as file:
        while True:
            time_line = file.readline().strip()
            if not time_line:
                break
            t = float(time_line)
            particles = []
            for i in range(N):
                values = file.readline().strip().split('\t')
                idx = int(values[0])
                x = float(values[1])
                y = float(values[2])
                vx = float(values[3])
                vy = float(values[4])
                # Crear instancia de Particle con el orden correcto
                particle = Particle(idx, particles_info[i][1], particles_info[i][2], x, y, vx, vy)
                particles.append(particle)
            states.append((t, particles))
    return states


# Función para actualizar la animación
def update(frame, circles, timesteps, particles_info):
    _, particle_states = timesteps[frame]

    for i, circle in enumerate(circles):
        particle = particle_states[i]
        radius = particles_info[i][1]

        # Actualizamos la posición de la circunferencia
        circle.center = (particle.x, particle.y)
        circle.radius = radius

    return circles


# Función principal para generar la animación
def animate_particles(static_file, dynamic_file):
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    # Crear las circunferencias para representar las partículas
    circles = []
    for idx, radius, _, color in particles_info:
        if (idx == 0):
            circle = patches.Circle((0, 0), radius=radius, color='orange', fill=True)
        else:
            circle = patches.Circle((0, 0), radius=radius, color='black', fill=True)
        ax.add_patch(circle)
        circles.append(circle)

    # Crear la animación
    ani = FuncAnimation(fig, update, frames=len(states), fargs=(circles, states, particles_info),
                        repeat=False, blit=False)
    plt.show()



# Función para graficar un frame específico
def plot_specific_frame(static_file, dynamic_file, frame_number):
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info, N)

    # Verificar que el número de frame esté en el rango válido
    if frame_number < 0 or frame_number >= len(states):
        print(f"Frame {frame_number} fuera de rango.")
        return

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    # Obtener la información del frame específico
    _, particle_states = states[frame_number]

    # Crear y dibujar las circunferencias de las partículas
    for particle in particle_states:
        color = 'orange' if particle.id == 0 else 'black'

        # Crear la circunferencia en la posición (x, y)
        circle = patches.Circle((particle.x, particle.y), radius=particle.radius, color=color, fill=True)
        ax.add_patch(circle)

        # Agregar el índice de la partícula cerca de la circunferencia
        ax.text(particle.x, particle.y, str(particle.id), color='green', fontsize=12, ha='center', va='center')

    plt.title(f"Frame {frame_number}")
    plt.show()



# Llamada a la función principal con los archivos correspondientes
#animate_particles('output/static.txt', 'output/dynamic.txt')

plot_specific_frame('output/static.txt', 'output/dynamic.txt', 0)
