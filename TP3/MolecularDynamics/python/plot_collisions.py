import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de estilo para los gráficos
plt.style.use('default')
sns.set_palette("husl")

def plot_collisions(base_directory, velocities):
    # Crear directorios si no existen
    plots_dir = os.path.join('outputs', base_directory, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Crear una figura con subplots para cada velocidad
    fig, axes = plt.subplots(len(velocities), 2, figsize=(15, 6*len(velocities)))

    # Para cada velocidad
    for idx, velocity in enumerate(velocities):
        vel_dir = f"v_{velocity:.2f}"
        count_path = os.path.join('outputs', base_directory, vel_dir, 'count.csv')

        if not os.path.exists(count_path):
            print(f"Error: No se encontró el archivo en {count_path}")
            continue

        # Leer el archivo count.csv
        df = pd.read_csv(count_path)

        # Gráfico de paredes
        ax1 = axes[idx, 0]
        ax1.plot(df['time'], df['bottom'], label='Bottom Wall', marker='o', markersize=4)
        ax1.plot(df['time'], df['right'], label='Right Wall', marker='s', markersize=4)
        ax1.plot(df['time'], df['top'], label='Top Wall', marker='^', markersize=4)
        ax1.plot(df['time'], df['left'], label='Left Wall', marker='D', markersize=4)

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Number of Collisions')
        ax1.set_title(f'Wall Collisions Over Time (v = {velocity} m/s)')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()

        # Gráfico de partícula estática
        ax2 = axes[idx, 1]
        ax2.plot(df['time'], df['static'], label='Static Particle',
                 color='red', marker='o', markersize=4)

        ax2.set_xlabel('Time')
        ax2.set_ylabel('Number of Collisions')
        ax2.set_title(f'Static Particle Collisions Over Time (v = {velocity} m/s)')
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend()

        # Imprimir estadísticas básicas
        print(f"\nCollision Statistics for v = {velocity} m/s:")
        print("=" * 40)
        print(f"Total wall collisions: {df[['bottom', 'right', 'top', 'left']].sum().sum()}")
        print(f"Total static particle collisions: {df['static'].sum()}")
        print("\nCollisions per wall:")
        for wall in ['bottom', 'right', 'top', 'left']:
            print(f"{wall.title()} wall: {df[wall].sum()}")

    # Ajustar el layout
    plt.tight_layout()

    # Guardar la figura
    plt.savefig(os.path.join(plots_dir, 'collisions_all_velocities.png'))
    plt.close()

if __name__ == "__main__":
    velocities = [1, 3.6, 10.0]  # m/s
    plot_collisions('fixed_solution', velocities)