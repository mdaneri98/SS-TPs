import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv
from matplotlib.animation import FuncAnimation
import os
from PIL import Image  # Librería para crear el GIF

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
            time, idx, x, y, vx, vy = float(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[4]), float(
                row[5])

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


def animate_particles(static_file, dynamic_file):
    global N, L
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info)

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

    # Add a text object to display the current time
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    # Create output directory for frames if not exists
    output_dir = "outputs/fixed_solution/animation"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def update(frame):
        state = states[frame]
        for particle in state.particles:
            circle = circles[particle.id]
            circle.center = (particle.x, particle.y)

            # Update particle ID position
            text = texts[particle.id]
            text.set_position((particle.x, particle.y))

            # Update arrow position and direction
            arrow = arrows[particle.id]
            scale_factor = 1 * circle.radius  # Scale arrow length according to particle radius
            arrow.remove()  # Remove previous arrow to redraw
            new_arrow = ax.arrow(
                particle.x, particle.y,
                particle.vx * scale_factor, particle.vy * scale_factor,
                head_width=scale_factor, head_length=scale_factor, fc='blue', ec='blue'
            )
            arrows[particle.id] = new_arrow  # Update arrow in dictionary

        # Update the time text
        time_text.set_text(f'Time: {state.time:.4f}')

        # Save the first 100 frames as images
        if frame < 40:
            plt.savefig(f"{output_dir}/frame_{frame:03d}.png", dpi=300)

        return list(circles.values()) + list(texts.values()) + list(arrows.values()) + [time_text]

    # Generate animation
    ani = FuncAnimation(fig, update, frames=len(states),
                        repeat=False, blit=True)

    # Save GIF after animation is done
    ani.save("particle_animation.gif", writer='imagemagick')

    # Display the animation
    plt.show()

    # Generate GIF from saved frames
    images = []
    for i in range(40):
        filename = f"{output_dir}/frame_{i:03d}.png"
        images.append(Image.open(filename))

    # Save as GIF
    images[0].save("particle_animation_frames.gif",
                   save_all=True, append_images=images[1:], duration=100, loop=0)


# Main execution
if __name__ == "__main__":
    static_file = 'outputs/fixed_solution/static.csv'
    dynamic_file = 'outputs/fixed_solution/particles.csv'

    animate_particles(static_file, dynamic_file)
