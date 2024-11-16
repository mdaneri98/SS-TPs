import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv
from matplotlib.animation import FuncAnimation
import os
from PIL import Image
import numpy as np

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

def read_dynamic_file(filename, particles_info, frame_step):
    states = []
    current_time = None
    current_particles = []
    state_count = 0

    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            time, idx, x, y, vx, vy = float(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])

            if current_time is not None and time != current_time:
                if state_count % frame_step == 0:  # Solo guarda cada frame_step estados
                    states.append(State(current_time, current_particles))
                state_count += 1
                current_particles = []

            current_time = time
            mass, radius = particles_info[idx]
            particle = Particle(idx, mass, radius, x, y, vx, vy)
            current_particles.append(particle)

    # Add the last state if it's complete and corresponds to frame_step
    if len(current_particles) == N and state_count % frame_step == 0:
        states.append(State(current_time, current_particles))

    return states

def animate_particles(static_file, dynamic_file, output_folder, save_frames=False, frame_step=10):
    global N, L
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info, frame_step)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    circles = {}
    texts = {}
    arrows = {}
    for idx, (mass, radius) in particles_info.items():
        color = 'orange' if idx == 0 else 'black'
        circle = patches.Circle((0, 0), radius=radius, color=color, fill=True)
        ax.add_patch(circle)
        circles[idx] = circle

        # Add a text for each particle ID
        text = ax.text(0, 0, str(idx), color="green", fontsize=8, ha='center', va='center')
        texts[idx] = text

        # Initialize arrows for each particle
        arrow = ax.arrow(0, 0, 0, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
        arrows[idx] = arrow

    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    os.makedirs(output_folder, exist_ok=True)

    def update(frame):
        state = states[frame]
        for particle in state.particles:
            circle = circles[particle.id]
            circle.center = (particle.x, particle.y)

            text = texts[particle.id]
            text.set_position((particle.x, particle.y))

            arrow = arrows[particle.id]
            scale_factor = 1 * circle.radius
            arrow.remove()
            new_arrow = ax.arrow(
                particle.x, particle.y,
                particle.vx * scale_factor, particle.vy * scale_factor,
                head_width=scale_factor, head_length=scale_factor, fc='blue', ec='blue'
            )
            arrows[particle.id] = new_arrow

        time_text.set_text(f'Time: {state.time:.4f}')

        if save_frames and frame < 20:  # Reducido a 20 frames
            plt.savefig(f"{output_folder}/frame_{frame:03d}.png", dpi=300)

        return list(circles.values()) + list(texts.values()) + list(arrows.values()) + [time_text]

    ani = FuncAnimation(fig, update, frames=min(len(states), 100),  # Limitado a 100 frames
                        interval=50,  # Intervalo más corto entre frames
                        repeat=False, blit=True)

    ani.save(os.path.join(output_folder, "particle_animation.gif"),
             writer='pillow',  # Usar pillow en lugar de imagemagick
             fps=10)  # Frames por segundo reducidos

    plt.close()

    if save_frames:
        images = []
        for i in range(min(20, len(states))):  # Reducido a 20 frames
            filename = f"{output_folder}/frame_{i:03d}.png"
            images.append(Image.open(filename))

        images[0].save(os.path.join(output_folder, "particle_animation_frames.gif"),
                       save_all=True, append_images=images[1:], duration=100, loop=0)

# Main execution
if __name__ == "__main__":
    velocities = [1.0, 3.6, 10.0]
    base_dirs = ["common_solution", "fixed_solution"]
    save_frames = False
    frame_step = 50  # Procesar 1 de cada 10 estados

    for base_dir in base_dirs:
        for velocity in velocities:
            print(f"\nProcesando {base_dir} con velocidad {velocity}")

            vel_dir = f"v_{velocity:.2f}"
            solution_dir = os.path.join("outputs", base_dir, vel_dir)

            if not os.path.exists(solution_dir):
                print(f"Directorio no encontrado: {solution_dir}")
                continue

            static_file = os.path.join(solution_dir, "static.csv")
            dynamic_file = os.path.join(solution_dir, "particles.csv")

            if not os.path.exists(static_file) or not os.path.exists(dynamic_file):
                print(f"Archivos no encontrados en {solution_dir}")
                continue

            output_folder = os.path.join(solution_dir, "animation")

            try:
                animate_particles(static_file, dynamic_file, output_folder, save_frames, frame_step)
                print(f"Animación generada exitosamente para {base_dir}/{vel_dir}")
            except Exception as e:
                print(f"Error procesando {base_dir}/{vel_dir}: {str(e)}")