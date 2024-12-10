import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_door_flow(ct_value, p_value, dt):
    input_path = Path('outputs/probabilistic_analysis') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path = Path('plots/exits') / f't_{ct_value}_&_p_{p_value:.2f}'

    print(f"Processing ct={ct_value}, p={p_value:.2f}")
    print(f"Input exists: {input_path.exists()}")

    output_path.mkdir(parents=True, exist_ok=True)

    all_flows = []
    all_times = []

    for sim_dir in input_path.glob('sim_*'):
        dynamic_file = sim_dir / 'dynamic.txt'
        if not dynamic_file.exists():
            continue

        print(f"Processing {sim_dir.name}")

        dynamic_data = []
        with open(dynamic_file, 'r') as f:
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
            print(f"No data found in {sim_dir}")
            continue

        dynamic_data.sort(key=lambda x: x['time'])
        max_time = dynamic_data[-1]['time']
        time_windows = np.arange(0, max_time, dt)

        times = []
        flows = []

        for t in time_windows:
            states_before = [s for s in dynamic_data if s['time'] <= t]
            states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

            if not states_before or not states_after:
                continue

            state1 = states_before[-1]
            state2 = states_after[0]

            # Calcular el flujo como la tasa de partículas que salen por unidad de tiempo
            count1 = len(state1['particles'])
            count2 = len(state2['particles'])
            time_diff = state2['time'] - state1['time']

            # Evitar división por cero
            if time_diff > 0:
                flow_rate = (count1 - count2) / time_diff
            else:
                flow_rate = 0

            times.append(t)
            flows.append(flow_rate)

        if flows:
            all_flows.append(flows)
            all_times.append(times)

    if not all_flows:
        print(f"No flow data calculated for ct={ct_value}, p={p_value}")
        return None, None, None

    # Calcular estadísticas
    max_len = min(len(flow) for flow in all_flows)
    times = all_times[0][:max_len]
    avg_flows = np.mean([flow[:max_len] for flow in all_flows], axis=0)
    std_flows = np.std([flow[:max_len] for flow in all_flows], axis=0)

    # Crear y guardar el plot individual
    plt.figure(figsize=(12, 6))
    plt.plot(times, avg_flows, label='Average flow', color='blue')
    plt.fill_between(times,
                     avg_flows - std_flows,
                     avg_flows + std_flows,
                     alpha=0.2,
                     color='blue',
                     label='Standard deviation')

    plt.xlabel('Time (s)')
    plt.ylabel('Flow Rate (particles/s)')
    plt.title(f'Average Particle Flow Rate\n(ct = {ct_value}, p = {p_value:.2f}, dt = {dt})')
    plt.legend()
    plt.grid(True)

    output_file = output_path / 'door_flow_rates.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    # Guardar datos
    flow_df = pd.DataFrame({
        'Time': times,
        'Average_Flow': avg_flows,
        'Std_Flow': std_flows
    })
    csv_file = output_path / 'door_flow_rates.csv'
    flow_df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

    return times, avg_flows, std_flows

def process_multiple_parameters(ct_values, p_values, dt):
    comparison_path = Path('plots/exits/comparison')
    comparison_path.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for ct in ct_values:
        all_results[ct] = {}
        for p in p_values:
            times, avg_flows, std_flows = calculate_door_flow(ct, p, dt)
            if times is not None:
                all_results[ct][p] = {
                    'times': times,
                    'avg_flows': avg_flows,
                    'std_flows': std_flows
                }

    # Plots por ct
    for ct in ct_values:
        plt.figure(figsize=(12, 6))
        for p in p_values:
            if p in all_results[ct]:
                data = all_results[ct][p]
                plt.plot(data['times'], data['avg_flows'],
                         label=f'p={p:.2f}')
                plt.fill_between(data['times'],
                                 data['avg_flows'] - data['std_flows'],
                                 data['avg_flows'] + data['std_flows'],
                                 alpha=0.2)

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/s)')
        plt.title(f'Flow Rate Comparison for ct={ct}')
        plt.legend()
        plt.grid(True)
        plt.savefig(comparison_path / f'comparison_ct_{ct}.png', dpi=300, bbox_inches='tight')
        plt.close()

    # Plots por p
    for p in p_values:
        plt.figure(figsize=(12, 6))
        for ct in ct_values:
            if p in all_results[ct]:
                data = all_results[ct][p]
                plt.plot(data['times'], data['avg_flows'],
                         label=f'ct={ct}')
                plt.fill_between(data['times'],
                                 data['avg_flows'] - data['std_flows'],
                                 data['avg_flows'] + data['std_flows'],
                                 alpha=0.2)

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/s)')
        plt.title(f'Flow Rate Comparison for p={p:.2f}')
        plt.legend()
        plt.grid(True)
        plt.savefig(comparison_path / f'comparison_p_{p:.2f}.png', dpi=300, bbox_inches='tight')
        plt.close()

    # Plot combinado
    plt.figure(figsize=(15, 8))
    for ct in ct_values:
        for p in p_values:
            if p in all_results[ct]:
                data = all_results[ct][p]
                plt.plot(data['times'], data['avg_flows'],
                         label=f'ct={ct}, p={p:.2f}')

    plt.xlabel('Time (s)')
    plt.ylabel('Flow Rate (particles/s)')
    plt.title('Combined Flow Rate Comparison')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.savefig(comparison_path / 'comparison_all.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    dt = 1
    ct_values = [10, 20, 30]
    p_values = [0.0, 0.5, 1.0]
    process_multiple_parameters(ct_values, p_values, dt)