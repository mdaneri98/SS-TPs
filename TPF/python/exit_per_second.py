import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def read_dynamic_file(file_path):
    """
    Lee el archivo dynamic.txt y devuelve una lista de estados temporales
    Cada estado contiene el tiempo y un diccionario de partículas con sus propiedades
    """
    states = []
    current_time = None
    current_particles = {}

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if ',' not in line:  # Es una línea de tiempo
                if current_time is not None:
                    states.append({
                        'time': current_time,
                        'particles': current_particles
                    })
                current_time = float(line)
                current_particles = {}
            else:  # Es una línea de partícula
                data = line.split(',')
                particle_id = int(data[0])
                current_particles[particle_id] = {
                    'x': float(data[1]),
                    'y': float(data[2]),
                    'vx': float(data[3]),
                    'vy': float(data[4]),
                    'radius': float(data[5]),
                    'target_door': int(data[6])
                }

    # Agregar el último estado
    if current_time is not None:
        states.append({
            'time': current_time,
            'particles': current_particles
        })

    return states

def calculate_door_flow(ct_value, p_value, dt):
    input_path = Path('outputs/probabilistic_analysis') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path = Path('plots/exits') / f't_{ct_value}_&_p_{p_value:.2f}'

    print(f"Processing ct={ct_value}, p={p_value:.2f}")
    print(f"Input path: {input_path}")
    print(f"Input exists: {input_path.exists()}")

    output_path.mkdir(parents=True, exist_ok=True)

    all_flows_by_door = {}
    all_times_by_door = {}

    for sim_dir in input_path.glob('sim*'):
        dynamic_file = sim_dir / 'dynamic.txt'
        if not dynamic_file.exists():
            continue

        print(f"Processing {sim_dir.name}")

        # Leer todos los estados
        states = read_dynamic_file(dynamic_file)
        if not states:
            continue

        # Ordenar estados por tiempo
        states.sort(key=lambda x: x['time'])
        max_time = states[-1]['time']
        time_windows = np.arange(0, max_time, dt)

        # Inicializar contadores para esta simulación
        times_by_door = {}
        flows_by_door = {}

        # Analizar estados consecutivos
        for i in range(len(states) - 1):
            state1 = states[i]
            state2 = states[i + 1]

            # Encontrar partículas que desaparecieron
            disappeared = set(state1['particles'].keys()) - set(state2['particles'].keys())

            # Registrar por qué puerta salió cada partícula
            exits_by_door = {}
            for particle_id in disappeared:
                target_door = state1['particles'][particle_id]['target_door']
                exits_by_door[target_door] = exits_by_door.get(target_door, 0) + 1

            # Asignar las salidas al tiempo correspondiente
            current_time = state1['time']
            time_window = current_time - (current_time % dt)

            # Calcular flujos
            time_diff = state2['time'] - state1['time']
            if time_diff > 0:
                for door_id, count in exits_by_door.items():
                    if door_id not in times_by_door:
                        times_by_door[door_id] = []
                        flows_by_door[door_id] = []

                    times_by_door[door_id].append(time_window)
                    flows_by_door[door_id].append(count / time_diff)

        # Agregar los flujos de esta simulación al conjunto total
        for door_id in flows_by_door:
            if flows_by_door[door_id]:  # Solo si hay datos para esta puerta
                if door_id not in all_flows_by_door:
                    all_flows_by_door[door_id] = []
                    all_times_by_door[door_id] = []
                all_flows_by_door[door_id].append(flows_by_door[door_id])
                all_times_by_door[door_id].append(times_by_door[door_id])

    # Procesar y graficar resultados
    plt.figure(figsize=(12, 6))
    results = {}

    for door_id in all_flows_by_door:
        if not all_flows_by_door[door_id]:
            print(f"No flow data for door {door_id}")
            continue

        # Alinear los tiempos y flujos para promediar
        min_time = min(min(times) for times in all_times_by_door[door_id])
        max_time = max(max(times) for times in all_times_by_door[door_id])
        time_grid = np.arange(min_time, max_time + dt, dt)

        # Interpolar los flujos en la grilla de tiempo común
        aligned_flows = []
        for times, flows in zip(all_times_by_door[door_id], all_flows_by_door[door_id]):
            interpolated = np.interp(time_grid, times, flows, left=0, right=0)
            aligned_flows.append(interpolated)

        # Calcular estadísticas
        avg_flows = np.mean(aligned_flows, axis=0)
        std_flows = np.std(aligned_flows, axis=0)

        # Graficar
        plt.plot(time_grid, avg_flows, label=f'Door {door_id}')
        plt.fill_between(time_grid,
                         avg_flows - std_flows,
                         avg_flows + std_flows,
                         alpha=0.2)

        results[door_id] = {
            'times': time_grid,
            'avg_flows': avg_flows,
            'std_flows': std_flows
        }

    plt.xlabel('Time (s)')
    plt.ylabel('Flow Rate (particles/s)')
    plt.title(f'Door Flow Rates\n(ct = {ct_value}, p = {p_value:.2f}, dt = {dt})')
    plt.legend()
    plt.grid(True)

    output_file = output_path / 'door_flow_rates.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    # Guardar datos en CSV
    for door_id, data in results.items():
        flow_df = pd.DataFrame({
            'Time': data['times'],
            'Average_Flow': data['avg_flows'],
            'Std_Flow': data['std_flows']
        })
        csv_file = output_path / f'door_{door_id}_flow_rates.csv'
        flow_df.to_csv(csv_file, index=False)
        print(f"Data saved to {csv_file}")

    return results

def process_multiple_parameters(ct_values, p_values, dt):
    # Crear carpeta para gráficos específicos
    specific_plots_path = Path('plots/exits/specific_combinations')
    specific_plots_path.mkdir(parents=True, exist_ok=True)

    # Crear carpeta para comparaciones
    comparison_path = Path('plots/exits/comparison')
    comparison_path.mkdir(parents=True, exist_ok=True)

    all_results = {}

    # Procesar cada combinación de ct y p
    for ct in ct_values:
        all_results[ct] = {}
        for p in p_values:
            results = calculate_door_flow(ct, p, dt)
            if results:
                all_results[ct][p] = results

                # Crear gráfico específico para esta combinación de ct y p
                plt.figure(figsize=(12, 6))
                for door_id, data in results.items():
                    plt.plot(data['times'], data['avg_flows'],
                             label=f'Door {door_id}')
                    plt.fill_between(data['times'],
                                     data['avg_flows'] - data['std_flows'],
                                     data['avg_flows'] + data['std_flows'],
                                     alpha=0.2)

                plt.xlabel('Time (s)')
                plt.ylabel('Flow Rate (particles/s)')
                plt.title(f'Door Flow Rates (ct={ct}, p={p:.2f})')
                plt.legend()
                plt.grid(True)

                # Guardar en la carpeta specific_combinations
                plt.savefig(specific_plots_path / f'flow_ct{ct}_p{p:.2f}.png',
                            dpi=300, bbox_inches='tight')
                plt.close()

    # Plots por ct (comparación)
    for ct in ct_values:
        plt.figure(figsize=(12, 6))
        for p in p_values:
            if p in all_results[ct]:
                for door_id, data in all_results[ct][p].items():
                    plt.plot(data['times'], data['avg_flows'],
                             label=f'Door {door_id}, p={p:.2f}')
                    plt.fill_between(data['times'],
                                     data['avg_flows'] - data['std_flows'],
                                     data['avg_flows'] + data['std_flows'],
                                     alpha=0.2)

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/s)')
        plt.title(f'Flow Rate Comparison for ct={ct}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.savefig(comparison_path / f'comparison_ct{ct}.png',
                    dpi=300, bbox_inches='tight')
        plt.close()

    # Plots por p (comparación)
    for p in p_values:
        plt.figure(figsize=(12, 6))
        for ct in ct_values:
            if p in all_results[ct]:
                for door_id, data in all_results[ct][p].items():
                    plt.plot(data['times'], data['avg_flows'],
                             label=f'Door {door_id}, ct={ct}')
                    plt.fill_between(data['times'],
                                     data['avg_flows'] - data['std_flows'],
                                     data['avg_flows'] + data['std_flows'],
                                     alpha=0.2)

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/s)')
        plt.title(f'Flow Rate Comparison for p={p:.2f}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.savefig(comparison_path / f'comparison_p{p:.2f}.png',
                    dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    dt = 1
    ct_values = [20]
    p_values = [0.0, 0.5, 1.0]
    process_multiple_parameters(ct_values, p_values, dt)