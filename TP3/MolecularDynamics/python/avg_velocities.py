import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Configuración de estilo para los gráficos
plt.style.use('default')
sns.set_palette("husl")

def plot_average_velocity(directory):
    # Corregir la ruta de lectura
    input_path = os.path.join('outputs', directory, 'particles.csv')
    output_path = os.path.join('outputs', directory, 'velocities.png')
    
    # Verificar que el archivo existe
    if not os.path.exists(input_path):
        print(f"Error: No se encuentra el archivo en {input_path}")
        return
        
    # Crear el directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Leer el archivo particles.csv especificando tipos de datos
    df = pd.read_csv(input_path, dtype={
        'time': float,
        'id': int,
        'x': float,
        'y': float,
        'vx': float,
        'vy': float
    })
    
    # Primero calculamos el módulo de la velocidad para cada partícula
    df['velocity_module'] = np.sqrt(df['vx'].astype(float)**2 + df['vy'].astype(float)**2)
    
    # Luego promediamos los módulos por tiempo
    avg_velocities = df.groupby('time')['velocity_module'].mean().reset_index()
    
    # Crear la figura
    plt.figure(figsize=(12, 6))
    
    # Plotear promedio de los módulos de velocidad
    plt.plot(avg_velocities['time'], avg_velocities['velocity_module'], 'b-', label='<|v(t)|>')
    
    plt.xlabel('Time')
    plt.ylabel('<|v(t)|>')
    plt.title('Average of Velocity Modules Over Time')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Agregar línea horizontal en la velocidad inicial
    initial_velocity = avg_velocities['velocity_module'].iloc[0]
    plt.axhline(y=initial_velocity, color='r', linestyle='--', 
                label=f'Initial Velocity ({initial_velocity:.3f})')
    
    # Ajustar el layout
    plt.tight_layout()
    
    # Guardar la figura
    plt.savefig(output_path)
    print(f"Gráfico guardado en: {output_path}")
    plt.close()

    # Imprimir estadísticas
    print("\nVelocity Statistics:")
    print("===================")
    print(f"Initial average velocity: {initial_velocity:.3f}")
    print(f"Final average velocity: {avg_velocities['velocity_module'].iloc[-1]:.3f}")
    print(f"Mean velocity: {avg_velocities['velocity_module'].mean():.3f}")
    print(f"Maximum average velocity: {avg_velocities['velocity_module'].max():.3f}")
    print(f"Minimum average velocity: {avg_velocities['velocity_module'].min():.3f}")

if __name__ == "__main__":
    plot_average_velocity('fixed_solution')