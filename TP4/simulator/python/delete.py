import numpy as np
import matplotlib.pyplot as plt

# Parámetros
A_inicial = 1  # Amplitud inicial en metros
posicion_inicial = 1  # Posición inicial en metros
velocidad_inicial = posicion_inicial  # Velocidad inicial (igual a la posición inicial)
masa = 70  # Masa en kg
k = 10**4  # Constante del resorte en N/m
b = 100  # Coeficiente de amortiguamiento en kg/s
tf = 5  # Tiempo final en segundos
dt = 0.001  # Incremento de tiempo

# Función de aceleración derivada de la ecuación diferencial
def aceleracion(x, v, m, b, k):
    return -(b / m) * v - (k / m) * x

# Variables para almacenar tiempo, posición y velocidad
t = np.arange(0, tf, dt)
x = np.zeros_like(t)
v = np.zeros_like(t)

# Condiciones iniciales
x[0] = posicion_inicial
v[0] = velocidad_inicial

# Método de Euler para resolver la ecuación diferencial
for i in range(1, len(t)):
    a = aceleracion(x[i-1], v[i-1], masa, b, k)
    v[i] = v[i-1] + a * dt
    x[i] = x[i-1] + v[i-1] * dt

# Gráfica de posición en función del tiempo
plt.figure(figsize=(10, 6))
plt.plot(t, x, label='Posición (m)')
plt.title('Oscilación Amortiguada: Posición en función del tiempo')
plt.xlabel('Tiempo (s)')
plt.ylabel('Posición (m)')
plt.grid(True)
plt.legend()
plt.show()
