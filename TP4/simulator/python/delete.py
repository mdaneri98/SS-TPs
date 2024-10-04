import numpy as np
import matplotlib.pyplot as plt

# Parámetros
b = 100.0  # Constante de amortiguamiento
k = 100000.0  # Constante del resorte
mass = 70.0  # Masa
max_time = 5.0  # Tiempo máximo
timestep = 1.0E-5  # Paso de tiempo
initial_amplitude = 1.0  # Amplitud inicial
initial_position = 1.0  # Posición inicial
initial_velocity = -0.7142857142857143  # Velocidad inicial

# Calcular la frecuencia angular amortiguada
omega_d = np.sqrt(k / mass - (b / (2 * mass)) ** 2)

# Tiempo
times = np.arange(0, max_time, timestep)

# Cálculo de la posición x(t)
# Fase inicial (phi) calculada a partir de la posición y velocidad iniciales
phi = np.arctan((initial_velocity + (b / (2 * mass)) * initial_position) / (omega_d * initial_amplitude))
positions = initial_amplitude * np.exp(-b / (2 * mass) * times) * np.cos(omega_d * times + phi)

# Crear el gráfico
plt.figure(figsize=(12, 6))
plt.plot(times, positions, label='Oscilador Armónico Amortiguado', color='blue')
plt.title('Movimiento de un Oscilador Armónico Amortiguado')
plt.xlabel('Tiempo (s)')
plt.ylabel('Posición (m)')
plt.xlim(0, max_time)
plt.ylim(min(positions) * 1.1, max(positions) * 1.1)
plt.grid()
plt.legend()
plt.show()
