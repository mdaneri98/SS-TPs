import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Read CSV files
df = pd.read_csv('outputs/multiple/verlet_13.000000/particle.csv')
static_df = pd.read_csv('outputs/multiple/verlet_13.000000/static.csv', header=None, skiprows=1)

# Assign column names
static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']

# Convert column values to float
n = float(static_df['n'].values[0])
k = float(static_df['k'].values[0])
mass = float(static_df['mass'].values[0])
distance = float(static_df['distance'].values[0])
amplitud = float(static_df['amplitud'].values[0])

# Define new timestep
new_timestep = 0.05

# Filter unique times
times = df['time'].unique()
times = times[(times % new_timestep) < 1e-4]

# Create figure and axis
fig, ax = plt.subplots()
ax.set_xlim(0, distance * n)
ax.set_ylim(-(1.1*amplitud), amplitud*1.1)
ax.set_xlabel('Distance (Index * distance)')
ax.set_ylabel('Position (Vertical)')

# Initialize scatter plot and line
scatter = ax.scatter([], [], s=50, c='blue')
line, = ax.plot([], [], lw=2, color='blue')

# Initialize max and min lines
max_line, = ax.plot([], [], lw=1, color='red', linestyle='--')
min_line, = ax.plot([], [], lw=1, color='green', linestyle='--')

# Initialize max and min values
global_max = -np.inf
global_min = np.inf

# Function to update animation for each frame
def update(frame):
    global global_max, global_min
    current_time = times[frame]

    # Filter data for current time
    current_data = df[df['time'] <= current_time]

    # Calculate x positions
    particle_indices = current_data['id'].unique()
    x_positions = particle_indices * distance

    # Get y positions for current time
    y_positions = current_data[current_data['time'] == current_time]['position']

    # Update global max and min
    frame_max = current_data['position'].max()
    frame_min = current_data['position'].min()
    global_max = max(global_max, frame_max)
    global_min = min(global_min, frame_min)

    # Create color array
    colors = ['red' if id == 0 else 'blue' for id in particle_indices]

    # Update scatter plot
    scatter.set_offsets(list(zip(x_positions, y_positions)))
    scatter.set_color(colors)

    # Update connecting line
    line.set_data(x_positions, y_positions)

    # Update max and min lines
    max_line.set_data([0, distance * n], [global_max, global_max])
    min_line.set_data([0, distance * n], [global_min, global_min])

    # Update title
    ax.set_title(f'Time: {current_time:.3f}')

    return scatter, line, max_line, min_line

# Create animation
anim = FuncAnimation(fig, update, frames=len(times), blit=False)

# Show animation
plt.show()