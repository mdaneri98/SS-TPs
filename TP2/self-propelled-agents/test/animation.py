import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import cm
from dynamic_particle import DynamicParticle

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
                particle_states.append(DynamicParticle(idx, x, y, v, theta))
            timesteps.append((t, particle_states))
    return timesteps


# Función para convertir ángulo en color usando colormap 'hsv'
def angle_to_color(theta):
    normalized_value = (theta % (2 * np.pi)) / (2 * np.pi)
    color = cm.hsv(normalized_value)
    return color


def angle_to_gray(theta):
    normalized_value = (theta % (2 * np.pi)) / (2 * np.pi)
    gray_value = str(normalized_value)
    return gray_value


# Función para actualizar la animación
def update(frame, arrows, timesteps):
    _, particle_states = timesteps[frame]
    for i, arrow in enumerate(arrows):
        particle = particle_states[i]

        u = particle.vel * np.cos(particle.theta)
        w = particle.vel * np.sin(particle.theta)

        start_x = particle.posX - u * 0.05 * L
        start_y = particle.posY - w * 0.05 * L
        end_x = particle.posX + u * 0.05 * L
        end_y = particle.posY + w * 0.05 * L

        gray_color = angle_to_color(particle.theta)
        arrow.set_color(gray_color)

        arrow.set_positions((start_x, start_y), (end_x, end_y))

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
        arrow = patches.FancyArrowPatch((0, 0), (0, 0), color='red', arrowstyle='-|>', mutation_scale=10)
        ax.add_patch(arrow)
        arrows.append(arrow)

    ani = FuncAnimation(fig, update, frames=len(timesteps), fargs=(arrows, timesteps), repeat=False, blit=False)
    plt.show()


# Función para graficar un frame específico
def plot_specific_frame(static_file, dynamic_file, frame_number):
    N, L, particles_info = read_static_file(static_file)
    timesteps = read_dynamic_file(dynamic_file, N)

    if frame_number >= len(timesteps) or frame_number < 0:
        raise ValueError("El número de frame está fuera de los límites.")

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    _, particle_states = timesteps[frame_number]

    for i, (idx, radius, _) in enumerate(particles_info):
        particle = particle_states[i]

        u = particle.vel * np.cos(particle.theta)
        w = particle.vel * np.sin(particle.theta)

        start_x = particle.posX
        start_y = particle.posY

        end_x = particle.posX + u * 0.1 * L
        end_y = particle.posY + w * 0.1 * L

        arrow = patches.FancyArrowPatch((start_x, start_y), (end_x, end_y), color=angle_to_color(particle.theta),
                                        arrowstyle='-|>', mutation_scale=0.1 * L)
        ax.add_patch(arrow)

    plt.show()


# Llamada a la función principal con los archivos correspondientes
animate_particles('N4000L32/static', 'N4000L32/dynamic')
