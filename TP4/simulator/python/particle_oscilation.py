import pandas as pd
import matplotlib.pyplot as plt


# Leer los datos del archivo CSV
df = pd.read_csv('python/outputs/analitic/particle.csv', delimiter=',')

# Visualizar la posición de la partícula a lo largo del tiempo
plt.figure(figsize=(10, 6))
plt.plot(df['time'], df['position'], marker='o', linestyle='-', color='b')
plt.title('Oscilación de la Partícula')
plt.xlabel('Tiempo (s)')
plt.ylabel('Posición (m)')
plt.grid()
plt.xlim(df['time'].min(), df['time'].max())
plt.ylim(df['position'].min() - 10, df['position'].max() + 10)
plt.axhline(0, color='grey', linewidth=0.5, linestyle='--')
plt.show()
