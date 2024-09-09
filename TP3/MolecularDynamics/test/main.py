import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from models import Particle, State


# Función para leer el archivo static.txt
def read_static(file_path):
    with open(file_path, 'r') as f:
        L = float(f.readline().strip())  # Largo del cuadrado
        N = int(f.readline().strip())  # Número de partículas
        particles = []
        for _ in range(N):
            line = f.readline().strip().split()
            radius = float(line[0])
            mass = float(line[1])
            color = int(line[2])
            particles.append((radius, mass, color))
    return L, N, particles


# Función para leer el archivo dynamic.txt
def read_dynamic(file_path):
    states = []
    with open(file_path, 'r') as f:
        while True:
            try:
                particles_list = []
                time = float(f.readline().strip())  # Lee el tiempo
                for _ in range(N):
                    line = f.readline().strip().split()
                    particle_id = int(line[0])
                    x = float(line[1])
                    y = float(line[2])
                    vx = float(line[3])
                    vy = float(line[4])
                    particles_list.append(Particle(particle_id, x, y, vx, vy))
                states.append(State(time, particles_list))
            except:
                print("Termino abruptamente con {} states!".format(len(states)))
                break
    return states


# Función para graficar las partículas
def plot_particles(L, N, states):
    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'brown', 'pink', 'gray', 'cyan']

    for state_id, state in enumerate(states):
        ax.clear()
        ax.set_title(f'Time: {state.time:.3f}')
        ax.set_xlim(0, L)
        ax.set_ylim(0, L)
        for i, (radius, _, color) in enumerate(particles):
            particle = state.particles[i]
            # Crear un círculo para la partícula
            circle = patches.Circle((particle.x, particle.y), radius, color=colors[color], fill=True)
            ax.add_patch(circle)
            # Si no es la partícula fija, dibujar una flecha de velocidad
            if particle.id != 0:
                ax.arrow(particle.x, particle.y, particle.vx * 0.01, particle.vy * 0.01, head_width=0.005, head_length=0.01, fc='black', ec='black')
        plt.pause(0.1)  # Pausa para animación
    plt.show()


# Cargar los datos
L, N, particles = read_static('output/static.txt')
states = read_dynamic('output/dynamic.txt')

# Graficar el movimiento de las partículas
plot_particles(L, N, states)
