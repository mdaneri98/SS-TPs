import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def read_doors(file_path):
    df = pd.read_csv(file_path, skiprows=1, header=None)
    return df.astype(float).values.tolist()

def calculate_door_specific_flow(p_value, dt):
    input_path = Path('outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('door_flows') / f'p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    doors = read_doors(input_path / 'doors.csv')

    try:
        dynamic_data = []
        with open(input_path / 'dynamic.txt', 'r') as f:
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
            print(f"No data found for p={p_value}")
            return

        dynamic_data.sort(key=lambda x: x['time'])
        max_time = dynamic_data[-1]['time']
        time_windows = np.arange(0, max_time, dt)

        door_flows = {i: [] for i in range(len(doors))}
        times = []

        def closest_door(particle_pos):
            distances = []
            for i, door in enumerate(doors):
                door_mid_x = (door[0] + door[2]) / 2
                door_mid_y = (door[1] + door[3]) / 2
                dist = np.sqrt((door_mid_x - particle_pos[0])**2 +
                               (door_mid_y - particle_pos[1])**2)
                distances.append(dist)
            return np.argmin(distances)

        for t in time_windows:
            states_before = [s for s in dynamic_data if s['time'] <= t]
            states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

            if not states_before or not states_after:
                continue

            state1 = states_before[-1]
            state2 = states_after[0]

            current_particles = {tuple(p[1:3]): closest_door(p[1:3])
                                 for p in state1['particles']}
            next_particles = {tuple(p[1:3]): closest_door(p[1:3])
                              for p in state2['particles']}

            for door_id in door_flows.keys():
                current_count = sum(1 for d in current_particles.values() if d == door_id)
                next_count = sum(1 for d in next_particles.values() if d == door_id)
                door_flows[door_id].append(current_count - next_count)

            times.append(t)

        plt.figure(figsize=(12, 6))
        for door_id, flows in door_flows.items():
            plt.plot(times, flows, label=f'Door {door_id+1}')

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/interval)')
        plt.title(f'Door-Specific Flow Rates (p={p_value}, dt={dt})')
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path / 'door_specific_flows.png')
        plt.close()

        flow_data = {'Time': times}
        for door_id, flows in door_flows.items():
            flow_data[f'Door_{door_id+1}_Flow'] = flows

        flow_df = pd.DataFrame(flow_data)
        flow_df.to_csv(output_path / 'door_specific_flows.csv', index=False)

    except Exception as e:
        print(f"Error processing p={p_value}: {str(e)}")

if __name__ == "__main__":
    dt = 1
    p_values = np.arange(0, 1.1, 0.1)
    for p in p_values:
        calculate_door_specific_flow(p, dt)