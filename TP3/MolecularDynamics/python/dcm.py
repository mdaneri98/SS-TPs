import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_msd_and_diffusion(base_dir, velocity=1.0, steady_state_time=None):
    """
    Calcula el DCM (Desplazamiento Cuadrático Medio) y el coeficiente de difusión
    para la partícula estática (id = 0).
    """
    # Leer archivo de partículas
    path = os.path.join('outputs', base_dir, f"v_{velocity:.2f}", "static_particle.csv")
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo en {path}")
        return

    # Leer datos de la partícula estática
    df_static = pd.read_csv(path)

    # Ordenar por tiempo y resetear índice
    df_static = df_static.sort_values('time').reset_index(drop=True)

    # Si se especifica tiempo de estado estacionario, filtrar datos
    if steady_state_time is not None:
        df_static = df_static[df_static['time'] >= steady_state_time].reset_index(drop=True)

    print("\nEstadísticas de la partícula estática:")
    print(df_static[['x', 'y']].describe())

    # Calcular desplazamientos consecutivos
    displacements = np.sqrt(np.diff(df_static['x'])**2 + np.diff(df_static['y'])**2)
    print("\nEstadísticas de desplazamientos consecutivos:")
    print("Media:", displacements.mean())
    print("Std:", displacements.std())
    print("Max:", displacements.max())

    # Visualizar la trayectoria
    plt.figure(figsize=(10, 10))
    plt.plot(df_static['x'], df_static['y'], 'b.-', alpha=0.5, label='Trayectoria')
    plt.plot(df_static['x'].iloc[0], df_static['y'].iloc[0], 'go', label='Inicio')
    plt.plot(df_static['x'].iloc[-1], df_static['y'].iloc[-1], 'ro', label='Fin')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('Trayectoria de la partícula estática')
    plt.grid(True)
    plt.legend()
    plt.axis('equal')

    # Crear directorio para guardar análisis
    output_dir = os.path.join('outputs', base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Guardar el gráfico de trayectoria
    plt.savefig(os.path.join(output_dir, "trajectory.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # Graficar posición vs tiempo
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(df_static['time'], df_static['x'], 'b.-', label='X')
    plt.ylabel('X (m)')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(df_static['time'], df_static['y'], 'r.-', label='Y')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Y (m)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "position_vs_time.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # Calcular DCM para diferentes intervalos de tiempo
    times = df_static['time'].values
    positions = np.column_stack((df_static['x'], df_static['y']))

    # Lista para almacenar resultados
    msd_results = []

    # Calcular DCM para diferentes deltas de tiempo
    max_delta_t = (times[-1] - times[0]) / 4  # Usamos hasta 1/4 del tiempo total
    n_points = min(20, len(times) // 2)  # Número de puntos para el DCM

    for i in range(1, n_points):
        # Tomar puntos separados por i intervalos
        dx = positions[i:] - positions[:-i]
        squared_displacement = np.sum(dx * dx, axis=1)
        delta_t = times[i] - times[0]

        if delta_t > max_delta_t:
            break

        msd = np.mean(squared_displacement)
        msd_std = np.std(squared_displacement)

        msd_results.append({
            'delta_t': delta_t,
            'msd': msd,
            'std': msd_std
        })

    # Convertir resultados a arrays para el ajuste
    delta_t = np.array([r['delta_t'] for r in msd_results])
    msd = np.array([r['msd'] for r in msd_results])
    msd_std = np.array([r['std'] for r in msd_results])

    # Ajuste lineal
    p = np.polyfit(delta_t, msd, 1)
    msd_fit = np.polyval(p, delta_t)

    # Coeficiente de difusión y R²
    D = p[0] / 4  # En 2D, D = pendiente/4
    residuals = msd - msd_fit
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((msd - np.mean(msd)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0

    # Graficar DCM vs tiempo
    plt.figure(figsize=(10, 6))
    plt.errorbar(delta_t, msd, yerr=msd_std, fmt='o', capsize=5, label='Datos', color='b')
    plt.plot(delta_t, msd_fit, 'r-', label=f'Ajuste lineal\nD = {D:.2e} m²/s')
    plt.xlabel('Δt (s)')
    plt.ylabel('DCM (m²)')
    plt.title('Desplazamiento Cuadrático Medio vs Tiempo')
    plt.grid(True)
    plt.legend()

    plt.savefig(os.path.join(output_dir, "msd_analysis.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print("\nResultados del análisis de difusión:")
    print(f"Coeficiente de difusión (D): {D:.2e} m²/s")
    print(f"R² del ajuste: {r_squared:.3f}")
    print(f"Ordenada al origen: {p[1]:.2e} m²")

if __name__ == "__main__":
    steady_state_time = 0  # Especifica aquí el tiempo de estado estacionario
    calculate_msd_and_diffusion("common_solution", velocity=1.0, steady_state_time=steady_state_time)