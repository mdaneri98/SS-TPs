import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def read_doors(file_path):
    df = pd.read_csv(file_path, skiprows=1, header=None)
    return df.astype(float).values.tolist()

def calculate_door_specific_flow(ct_value, p_value, dt):
    input_path = Path('outputs/probabilistic_analysis') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path = Path('outputs/door_flows') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    all_door_flows = {}
    all_times = []

    for sim_dir in input_path.glob('sim_*'):
        print(f"Processing {sim_dir.name}")

        try:
            doors = read_doors(sim_dir / 'doors.csv')

            dynamic_data = []
            with open(sim_dir / 'dynamic.txt', 'r') as f:
                current_time = None
                particles = []
                for line in f:
                    line = line.strip()
                    if ',' not in line:
                        if particles:
                            dynamic_data.append({'time': current_time, 'particles': particles})
                        current_time = float(line)
                        particles = []
                    else:
                        particle = list(map(float, line.split(',')))
                        particles.append(particle)
                if particles:
                    dynamic_data.append({'time': current_time, 'particles': particles})

            if not dynamic_data:
                print(f"No data found for simulation {sim_dir.name}")
                continue

            dynamic_data.sort(key=lambda x: x['time'])
            max_time = dynamic_data[-1]['time']
            time_windows = np.arange(0, max_time, dt)

            door_flows = {i: [] for i in range(len(doors))}
            times = []

            def get_door_id(particle):
                # El último valor en particle es el número de puerta
                return int(particle[6])

            for t in time_windows:
                states_before = [s for s in dynamic_data if s['time'] <= t]
                states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

                if not states_before or not states_after:
                    continue

                state1 = states_before[-1]
                state2 = states_after[0]

                # Crear conjuntos de IDs de partículas para cada estado
                particles1 = set(tuple(p) for p in state1['particles'])
                particles2 = set(tuple(p) for p in state2['particles'])

                # Encontrar partículas que desaparecieron
                disappeared_particles = particles1 - particles2

                # Contar por puerta
                door_counts = {i: 0 for i in range(len(doors))}
                for particle in disappeared_particles:
                    door_id = get_door_id(particle)
                    door_counts[door_id] += 1

                # Guardar conteos
                for door_id in door_flows.keys():
                    door_flows[door_id].append(door_counts[door_id])

                times.append(t)

            # Store results for this simulation
            for door_id, flows in door_flows.items():
                if door_id not in all_door_flows:
                    all_door_flows[door_id] = []
                all_door_flows[door_id].append(flows)
            all_times.append(times)

        except Exception as e:
            print(f"Error processing simulation {sim_dir.name}: {str(e)}")
            continue

    if all_door_flows and all_times:
        min_time_len = min(len(t) for t in all_times)
        times = all_times[0][:min_time_len]

        plt.figure(figsize=(12, 6))
        flow_data = {'Time': times}

        for door_id in all_door_flows.keys():
            door_flows = [flow[:min_time_len] for flow in all_door_flows[door_id]]
            avg_flow = np.mean(door_flows, axis=0)
            std_flow = np.std(door_flows, axis=0)

            plt.plot(times, avg_flow, label=f'Door {door_id}')
            plt.fill_between(times,
                             avg_flow - std_flow,
                             avg_flow + std_flow,
                             alpha=0.2)

            flow_data[f'Door_{door_id}_Avg_Flow'] = avg_flow
            flow_data[f'Door_{door_id}_Std_Flow'] = std_flow

        plt.xlabel('Time (s)')
        plt.ylabel('Number of particles exiting per interval')
        plt.title(f'Door-Specific Exit Flow\n(ct={ct_value}, p={p_value:.2f}, dt={dt})')
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path / 'door_specific_flows.png', dpi=300, bbox_inches='tight')
        plt.close()

        flow_df = pd.DataFrame(flow_data)
        flow_df.to_csv(output_path / 'door_specific_flows.csv', index=False)

if __name__ == "__main__":
    dt = 1
    ct_value = 280  # Especifica el valor de ct que quieres analizar
    p_value = 0.5  # Especifica el valor de p que quieres analizar
    calculate_door_specific_flow(ct_value, p_value, dt)