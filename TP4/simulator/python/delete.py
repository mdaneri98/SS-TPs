import numpy as np
import matplotlib.pyplot as plt

# Parámetros
n = 1000
k = 100
mass = 1
distance = 10e-3
amplitud = 10e-2

# Simulación de tiempo
t = np.linspace(0, 10, 1000)  # tiempo de 0 a 10 segundos
frecuencia = np.sqrt(k / mass) / (2 * np.pi)
force = amplitud * np.cos(frecuencia * t)

# Inicializar posiciones
positions = np.zeros((n, len(t)))

# Calcular las posiciones para cada partícula
for i in range(n):
    positions[i] = force * (1 - (i / n))  # Disminuye la amplitud para partículas más lejanas

# Graficar
plt.figure(figsize=(10, 6))
for i in range(0, n, 100):  # graficar cada 100 partículas
    plt.plot(t, positions[i], label=f'Partícula {i}')
plt.title('Oscilaciones de Partículas en un Sistema Acoplado')
plt.xlabel('Tiempo (s)')
plt.ylabel('Posición (m)')
plt.ylim(-0.02, 0.02)
plt.grid()
plt.legend()
plt.show()
