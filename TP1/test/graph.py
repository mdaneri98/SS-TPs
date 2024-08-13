import matplotlib.pyplot as plt


def read_particles_data(static_filename, dynamic_filename):
    static_data = []
    particle_data = []

    # Datos estáticos
    with open(static_filename, 'r') as file:
        N = int(file.readline())
        L = int(file.readline())
        idx = 0
        for line in file:
            parts = line.split()
            radius = float(parts[0])
            color = float(parts[1])
            static_data.append((id, radius, color))
            idx += 1

    # Datos dinámicos.
    with open(dynamic_filename, 'r') as file:
        file.readline()
        for line in file:
            parts = line.split()
            if len(parts) == 3:
                idx = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                particle_data.append((idx, x, y, static_data[idx][1], static_data[idx][2]))

    return {'N': N, 'L': L, 'particle_data': particle_data}


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

def plot_particle_interactions(particle_data, interactions, target_id, ir, M, L):
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Draw grid
    for i in range(M + 1):
        ax.axhline(i * (L / M), color='gray', linewidth=0.5)
        ax.axvline(i * (L / M), color='gray', linewidth=0.5)

    # Plot particles as dots
    for (pid, px, py, pr, color) in particle_data:
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


# Leer datos desde archivos -> {'N', 'L', 'particle_data'=(id, x, y, radio, color)}
data = read_particles_data('test_static', 'test_dynamic')

interactions = read_interactions('test_interactions')

# ID de la partícula objetivo
ir = 12
M = 5
target_id = 81

# Llamar a la función para graficar
plot_particle_interactions(data['particle_data'], interactions, target_id, ir=ir, M=M, L=data['L'])
