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
                return int(particle[6])

            cumulative_counts = {i: 0 for i in range(len(doors))}

            for t in time_windows:
                states_before = [s for s in dynamic_data if s['time'] <= t]
                states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

                if not states_before or not states_after:
                    continue

                state1 = states_before[-1]
                state2 = states_after[0]

                particles1 = set(tuple(p) for p in state1['particles'])
                particles2 = set(tuple(p) for p in state2['particles'])

                disappeared_particles = particles1 - particles2

                for particle in disappeared_particles:
                    door_id = get_door_id(particle)
                    cumulative_counts[door_id] += 1

                for door_id in door_flows.keys():
                    door_flows[door_id].append(cumulative_counts[door_id])

                times.append(t)

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

            flow_data[f'Door_{door_id}_Cumulative_Avg'] = avg_flow
            flow_data[f'Door_{door_id}_Cumulative_Std'] = std_flow

        plt.xlabel('Time (s)')
        plt.ylabel('Cumulative number of particles exited')
        plt.title(f'Cumulative Door-Specific Exit Flow\n(ct={ct_value}, p={p_value:.2f}, dt={dt})')
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path / 'cumulative_door_flows.png', dpi=300, bbox_inches='tight')
        plt.close()

        flow_df = pd.DataFrame(flow_data)
        flow_df.to_csv(output_path / 'cumulative_door_flows.csv', index=False)

    return output_path

def process_multiple_parameters(ct_values, p_values, dt):
    # Create a figure for comparing all combinations
    plt.figure(figsize=(15, 10))

    line_styles = ['-', '--', ':', '-.']
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for ct in ct_values:
        for p in p_values:
            output_path = calculate_door_specific_flow(ct, p, dt)

            # Read the data for this combination
            data = pd.read_csv(output_path / 'cumulative_door_flows.csv')

            # Plot only the average values for each door
            door_columns = [col for col in data.columns if 'Avg' in col]
            for i, col in enumerate(door_columns):
                door_id = col.split('_')[1]
                style_idx = ct_values.index(ct) % len(line_styles)
                color_idx = p_values.index(p) % len(colors)

                plt.plot(data['Time'], data[col],
                         linestyle=line_styles[style_idx],
                         color=colors[color_idx],
                         label=f'Door {door_id} (ct={ct}, p={p:.2f})')

    plt.xlabel('Time (s)')
    plt.ylabel('Cumulative number of particles exited')
    plt.title('Comparison of Cumulative Door-Specific Exit Flows\nfor Different Parameters')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)

    comparison_path = Path('outputs/door_flows/parameter_comparison')
    comparison_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(comparison_path / 'combined_flows_comparison.png',
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    dt = 1
    ct_values = [10, 20, 30, 40, 50, 60]  # Lista de valores de ct para analizar
    p_values = [0.0, 0.5, 1.0]  # Lista de valores de p para analizar
    process_multiple_parameters(ct_values, p_values, dt)