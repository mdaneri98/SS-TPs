import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_door_flow(p_value, dt):
    input_path = Path('outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('exits') / f'p_{p_value:.2f}'

    print(f"Checking paths...")
    print(f"Input exists: {input_path.exists()}")
    print(f"Input dynamic.txt exists: {(input_path / 'dynamic.txt').exists()}")
    print(f"Output path: {output_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    # Read data
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

    # Sort by time to ensure order
    dynamic_data.sort(key=lambda x: x['time'])

    # Create time windows
    max_time = dynamic_data[-1]['time']
    time_windows = np.arange(0, max_time, dt)

    times = []
    flows = []

    # Calculate flow for each window
    for t in time_windows:
        # Find closest states before and after t
        states_before = [s for s in dynamic_data if s['time'] <= t]
        states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

        if not states_before or not states_after:
            continue

        state1 = states_before[-1]
        state2 = states_after[0]

        count1 = len(state1['particles'])
        count2 = len(state2['particles'])

        times.append(t)
        flows.append(count1 - count2)

    print(f"P={p_value}: Found {len(flows)} intervals with flow data")

    if flows:
        plt.figure(figsize=(10, 6))
        plt.plot(times, flows, label='Total flow')
        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/interval)')
        plt.title(f'Particle Flow Rate (p = {p_value}, dt = {dt})')
        plt.legend()
        plt.grid(True)

        output_file = output_path / 'door_flow_rates.png'
        print(f"Saving plot to: {output_file}")
        plt.savefig(output_file)
        plt.close()

        flow_df = pd.DataFrame({'Time': times, 'Flow': flows})
        csv_file = output_path / 'door_flow_rates.csv'
        print(f"Saving CSV to: {csv_file}")
        flow_df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    dt = 1
    p_values = np.arange(0, 1.1, 0.1)
    for p in p_values:
        calculate_door_flow(p, dt)