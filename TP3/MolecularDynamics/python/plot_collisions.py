import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de estilo para los gráficos
plt.style.use('default')
sns.set_palette("husl")

def plot_collisions(directory):
    # Leer el archivo count.csv
    df = pd.read_csv(os.path.join('outputs', directory, 'count.csv'))
    
    # Crear una figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de paredes
    ax1.plot(df['time'], df['bottom'], label='Bottom Wall', marker='o', markersize=4)
    ax1.plot(df['time'], df['right'], label='Right Wall', marker='s', markersize=4)
    ax1.plot(df['time'], df['top'], label='Top Wall', marker='^', markersize=4)
    ax1.plot(df['time'], df['left'], label='Left Wall', marker='D', markersize=4)
    
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Number of Collisions')
    ax1.set_title('Wall Collisions Over Time')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Gráfico de partícula estática
    ax2.plot(df['time'], df['static'], label='Static Particle', 
            color='red', marker='o', markersize=4)
    
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Number of Collisions')
    ax2.set_title('Static Particle Collisions Over Time')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()

    # Ajustar el layout
    plt.tight_layout()
    
    # Guardar la figura
    plt.savefig(os.path.join('outputs', directory, 'collisions.png'))
    plt.close()

    # Imprimir estadísticas básicas
    print("\nCollision Statistics:")
    print("===================")
    print(f"Total wall collisions: {df[['bottom', 'right', 'top', 'left']].sum().sum()}")
    print(f"Total static particle collisions: {df['static'].sum()}")
    print("\nCollisions per wall:")
    for wall in ['bottom', 'right', 'top', 'left']:
        print(f"{wall.title()} wall: {df[wall].sum()}")

if __name__ == "__main__":
    plot_collisions('fixed_solution')