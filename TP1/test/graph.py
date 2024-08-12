import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches
import numpy as np


def read_particle_data(filename):
    particle_data = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) == 3:
                id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                particle_data.append((id, x, y))
    return particle_data


def read_interactions(filename):
    interactions = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) >= 2:
                id = int(parts[0])
                neighbors = list(map(int, parts[1:]))
                interactions[id] = neighbors
    return interactions

def belongsTo(interactions, targetID, currentID):
    if targetID not in interactions:
        return False
    particles = interactions[targetID]
    return currentID in particles

def plot_particle_interactions(particle_data, interactions, target_id, ir, pr, M, L):
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Draw grid
    for i in range(M + 1):
        ax.axhline(i * (L / M), color='gray', linewidth=0.5)
        ax.axvline(i * (L / M), color='gray', linewidth=0.5)

    # Plot particles as dots
    for (pid, px, py) in particle_data:
        if target_id == pid:
            circle = plt.Circle((px, py), pr, color='black', fill=True)

            interaction_circle = plt.Circle((px, py), ir, color='blue', alpha=0.5, fill=True)
            ax.add_patch(interaction_circle)
        elif belongsTo(interactions, target_id, pid):
            circle = plt.Circle((px, py), pr, color='green', fill=True)
        else:
            circle = plt.Circle((px, py), pr, color='gray', fill=True)
        ax.add_patch(circle)
        ax.text(px, py, str(pid), color='black', ha='center', va='center', fontsize=4)

    # Customize the plot
    plt.xlim(0, L)
    plt.ylim(0, L)
    plt.title("Particles and Neighbors")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.gca().set_aspect('equal', adjustable='box')

    # Show the plot
    plt.show()


# Leer datos desde archivos
particle_data = read_particle_data('test_positions')
interactions = read_interactions('test_interactions')

# ID de la partícula objetivo
L = 10
M = 5
N = 20
ir = 1.5
pr = 0.5
target_id = 16

# Llamar a la función para graficar
plot_particle_interactions(particle_data, interactions, target_id, ir=ir, pr=pr, M=M, L=L)
