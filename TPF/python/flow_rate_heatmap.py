import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re

def extract_params_from_dirname(dirname):
    """
    Extrae los valores de ct y p del nombre del directorio usando expresiones regulares.
    """
    # Buscar patrones t_X_&_p_Y.ZZ
    match = re.match(r't_(\d+)_&_p_(\d*\.?\d+)', dirname)
    if match:
        ct = int(match.group(1))
        p = float(match.group(2))
        return ct, p
    return None, None

def analyze_flow_metrics(base_dir='outputs/probabilistic_analysis'):
    """
    Analiza las métricas de flujo para todas las combinaciones de ct y p encontradas.
    """
    base_path = Path(base_dir)

    # Almacenar datos para el análisis
    data = {
        'ct': [],
        'p': [],
        'peak_flow': [],
        'avg_flow': [],
        'time_to_peak': [],
        'total_time': [],
        'early_flow': []
    }

    # Procesar cada directorio de simulación
    for combo_dir in base_path.glob('t_*_&_p_*'):
        try:
            # Extraer ct y p del nombre del directorio usando el nuevo método
            ct, p = extract_params_from_dirname(combo_dir.name)
            if ct is None or p is None:
                print(f"No se pudieron extraer parámetros del directorio: {combo_dir.name}")
                continue

            print(f"Procesando ct={ct}, p={p:.2f}")

            # Procesar cada simulación en el directorio
            flow_metrics = []
            for sim_dir in combo_dir.glob('sim_*'):
                try:
                    # Leer datos de partículas
                    dynamic_file = sim_dir / 'dynamic.txt'
                    if not dynamic_file.exists():
                        continue

                    # Leer y procesar el archivo
                    times = []
                    particles = []
                    current_time = None

                    with open(dynamic_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                # Intentar convertir a timestamp
                                t = float(line)
                                if current_time is not None:
                                    times.append(current_time)
                                    particles.append(len(current_particles))
                                current_time = t
                                current_particles = []
                            except ValueError:
                                # Es una línea de partícula
                                if current_time is not None:
                                    current_particles.append(line)

                        # Añadir el último conjunto de datos
                        if current_time is not None and current_particles:
                            times.append(current_time)
                            particles.append(len(current_particles))

                    if not times or not particles:
                        print(f"No se encontraron datos válidos en {sim_dir.name}")
                        continue

                    # Convertir a arrays de numpy
                    times = np.array(times)
                    particles = np.array(particles)

                    # Calcular métricas de flujo
                    if len(times) > 1:  # Asegurar que hay suficientes puntos para calcular flujos
                        flows = -np.diff(particles) / np.diff(times)  # Negativo para obtener flujo de salida
                        if len(flows) > 0:
                            peak_flow = np.max(flows)
                            avg_flow = np.mean(flows)
                            time_to_peak = times[:-1][np.argmax(flows)]
                            total_time = times[-1]

                            # Calcular flujo temprano (primeros 60s)
                            early_mask = times[:-1] <= 60
                            early_flow = np.sum(flows[early_mask]) if any(early_mask) else 0

                            flow_metrics.append({
                                'peak_flow': peak_flow,
                                'avg_flow': avg_flow,
                                'time_to_peak': time_to_peak,
                                'total_time': total_time,
                                'early_flow': early_flow
                            })

                except Exception as e:
                    print(f"Error procesando simulación {sim_dir.name}: {str(e)}")
                    continue

            # Si tenemos métricas válidas, calcular promedios y guardar
            if flow_metrics:
                data['ct'].append(ct)
                data['p'].append(p)
                data['peak_flow'].append(np.mean([m['peak_flow'] for m in flow_metrics]))
                data['avg_flow'].append(np.mean([m['avg_flow'] for m in flow_metrics]))
                data['time_to_peak'].append(np.mean([m['time_to_peak'] for m in flow_metrics]))
                data['total_time'].append(np.mean([m['total_time'] for m in flow_metrics]))
                data['early_flow'].append(np.mean([m['early_flow'] for m in flow_metrics]))
            else:
                print(f"No se encontraron métricas válidas para ct={ct}, p={p:.2f}")

        except Exception as e:
            print(f"Error procesando directorio {combo_dir.name}: {str(e)}")
            continue

    # Verificar si tenemos datos
    if not data['ct']:
        print("No se encontraron datos válidos para analizar")
        return None

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Crear gráficos
    metrics = ['peak_flow', 'avg_flow', 'time_to_peak', 'total_time', 'early_flow']
    titles = {
        'peak_flow': 'Flujo Máximo (part/s)',
        'avg_flow': 'Flujo Promedio (part/s)',
        'time_to_peak': 'Tiempo hasta Flujo Máximo (s)',
        'total_time': 'Tiempo Total de Evacuación (s)',
        'early_flow': 'Flujo Acumulado 60s (part)'
    }

    # Crear subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, metric in enumerate(metrics):
        if idx >= len(axes):
            break

        # Crear pivot table para el heatmap
        pivot_data = df.pivot(index='ct', columns='p', values=metric)

        # Verificar si hay datos válidos
        if pivot_data.empty or pivot_data.isnull().all().all():
            print(f"No hay datos válidos para el heatmap de {metric}")
            continue

        # Crear heatmap
        sns.heatmap(pivot_data,
                    ax=axes[idx],
                    cmap='viridis' if 'time' not in metric else 'viridis_r',
                    annot=True,
                    fmt='.1f',
                    cbar_kws={'label': metric})

        axes[idx].set_title(titles[metric])
        axes[idx].set_xlabel('Probabilidad (p)')
        axes[idx].set_ylabel('Tiempo de contacto (ct)')

    # Eliminar subplot extra si existe
    if len(metrics) < len(axes):
        fig.delaxes(axes[-1])

    plt.tight_layout()
    plt.savefig('flow_metrics_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Guardar datos en CSV
    df.to_csv('flow_metrics.csv', index=False)

    return df

if __name__ == "__main__":
    metrics_df = analyze_flow_metrics()