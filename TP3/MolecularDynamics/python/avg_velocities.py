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
   
   # Leer el archivo particles.csv
   df = pd.read_csv(input_path)
   
   # Calcular la velocidad absoluta para cada partícula
   df['velocity'] = np.sqrt(df['vx']**2 + df['vy']**2)
   
   # Agrupar por tiempo y calcular el promedio de velocidades
   velocity_avg = df.groupby('time')['velocity'].mean().reset_index()
   velocity_std = df.groupby('time')['velocity'].std().reset_index()
   
   # Crear la figura
   plt.figure(figsize=(12, 6))
   
   # Plotear velocidad promedio con desviación estándar
   plt.plot(velocity_avg['time'], velocity_avg['velocity'], 'b-', label='Average Velocity')
   plt.fill_between(velocity_avg['time'], 
                   velocity_avg['velocity'] - velocity_std['velocity'],
                   velocity_avg['velocity'] + velocity_std['velocity'],
                   alpha=0.2, color='b')
   
   plt.xlabel('Time')
   plt.ylabel('Average Velocity')
   plt.title('Average Particle Velocity Over Time')
   plt.grid(True, linestyle='--', alpha=0.7)
   plt.legend()

   # Agregar línea horizontal en la velocidad inicial
   initial_velocity = velocity_avg['velocity'].iloc[0]
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
   print(f"Final average velocity: {velocity_avg['velocity'].iloc[-1]:.3f}")
   print(f"Mean velocity throughout simulation: {velocity_avg['velocity'].mean():.3f}")
   print(f"Velocity standard deviation: {velocity_avg['velocity'].std():.3f}")
   print(f"Maximum average velocity: {velocity_avg['velocity'].max():.3f}")
   print(f"Minimum average velocity: {velocity_avg['velocity'].min():.3f}")

if __name__ == "__main__":
   plot_average_velocity('fixed_solution')