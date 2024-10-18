import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv
from matplotlib.animation import FuncAnimation

# Global variables
N = 0  # Number of particles
L = 0  # Graph size

class Particle:
    def __init__(self, id, mass, radius, x, y, vx, vy):
        self.id = id
        self.mass = mass
        self.radius = radius
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class State:
    def __init__(self, time, particles):
        self.time = time
        self.particles = particles

def read_static_file(filename):
    global N, L
    particles_info = {}
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            idx, mass, radius = int(row[0]), float(row[1]), float(row[2])
            particles_info[idx] = (mass, radius)
    return N, L, particles_info

def read_dynamic_file(filename, particles_info):
    states = []
    current_time = None
    current_particles = []

    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            time, idx, x, y, vx, vy = float(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])

            if current_time is not None and time != current_time:
                states.append(State(current_time, current_particles))
                current_particles = []

            current_time = time
            mass, radius = particles_info[idx]
            particle = Particle(idx, mass, radius, x, y, vx, vy)
            current_particles.append(particle)

    # Add the last state if it's complete
    if len(current_particles) == N:
        states.append(State(current_time, current_particles))

    return states

def update(frame, circles, states):
    state = states[frame]
    for particle in state.particles:
        circle = circles[particle.id]
        circle.center = (particle.x, particle.y)
    return circles.values()

def animate_particles(static_file, dynamic_file):
    global N, L
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    circles = {}
    for idx, (mass, radius) in particles_info.items():
        color = 'orange' if idx == 0 else 'black'
        circle = patches.Circle((0, 0), radius=radius, color=color, fill=True)
        ax.add_patch(circle)
        circles[idx] = circle

    ani = FuncAnimation(fig, update, frames=len(states), fargs=(circles, states),
                        repeat=False, blit=True)
    plt.show()

def plot_specific_frame(static_file, dynamic_file, frame_number):
    global N, L
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info)

    if frame_number < 0 or frame_number >= len(states):
        print(f"Frame {frame_number} out of range.")
        return

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    state = states[frame_number]

    for particle in state.particles:
        color = 'orange' if particle.id == 0 else 'black'
        circle = patches.Circle((particle.x, particle.y), radius=particle.radius, color=color, fill=True)
        ax.add_patch(circle)
        ax.text(particle.x, particle.y, str(particle.id), color='green', fontsize=12, ha='center', va='center')

    plt.title(f"Frame {frame_number}, Time: {state.time:.6f}")
    plt.show()

# Main execution
if __name__ == "__main__":
    static_file = 'outputs/fixed_solution/static.csv'
    dynamic_file = 'outputs/fixed_solution/particles.csv'

    #animate_particles(static_file, dynamic_file)

    #Uncomment the following lines to plot specific frames
    plot_specific_frame(static_file, dynamic_file, 1)
    plot_specific_frame(static_file, dynamic_file, 2)
    plot_specific_frame(static_file, dynamic_file, 3)