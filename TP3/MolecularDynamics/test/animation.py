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
                        repeat=False, blit=True)
    plt.show()

# Función para graficar un frame específico
def plot_specific_frame(static_file, dynamic_file, frame_number):
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info, N)

    if frame_number >= len(states) or frame_number < 0:
        raise ValueError("El número de frame está fuera de los límites.")

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    _, particle_states = states[frame_number]

    for i, (idx, radius, _) in enumerate(particles_info):
        particle = particle_states[i]

        # Posición inicial de la flecha (en la cola)
        start_x = particle.x
        start_y = particle.y

        end_x = particle.x + particle.vx * 1
        end_y = particle.y + particle.vy * 1 # dt = 1

        # Dibujo de la flecha alineada con el movimiento
        arrow = patches.FancyArrowPatch((start_x, start_y), (end_x, end_y), color='black',
                                        arrowstyle='-|>', mutation_scale=1)
        ax.add_patch(arrow)

    plt.show()

# Llamada a la función principal con los archivos correspondientes
animate_particles('output/static.txt', 'output/interpolated_dynamic.txt')

# plot_specific_frame('static.txt', 'dynamic.txt', 0)
