import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def get_k_folders(base_path='outputs/multiple'):
    return sorted([f for f in os.listdir(base_path) if f.startswith('k_')],
                  key=lambda x: float(x.split('_')[1]))

def get_verlet_folders(k_folder_path):
    return sorted([f for f in os.listdir(k_folder_path) if f.startswith('verlet_')],
                  key=lambda x: float(x.split('_')[1]))

def extract_value(folder_name, prefix):
    return float(folder_name.split(prefix)[1])

def analyze_data(base_path='outputs/multiple'):
    k_folders = get_k_folders(base_path)
    all_data = {}

    for k_folder in k_folders:
        k_value = extract_value(k_folder, 'k_')
        k_path = os.path.join(base_path, k_folder)
        verlet_folders = get_verlet_folders(k_path)

        w_values = []
        max_amplitudes = []

        for verlet_folder in verlet_folders:
            verlet_path = os.path.join(k_path, verlet_folder)
            static_df = pd.read_csv(os.path.join(verlet_path, 'static.csv'), header=None, skiprows=1)
            particle_df = pd.read_csv(os.path.join(verlet_path, 'particle.csv'))

            static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']
            wf = float(static_df['wf'].values[0])
            max_amplitude = particle_df['position'].abs().max()

            w_values.append(wf)
            max_amplitudes.append(max_amplitude)

        all_data[k_value] = {'w': np.array(w_values), 'amp': np.array(max_amplitudes)}

    return all_data

def plot_results(all_data):
    colors = plt.cm.viridis(np.linspace(0, 1, len(all_data)))

    for i, (k, data) in enumerate(all_data.items()):
        sorted_indices = np.argsort(data['w'])
        w_sorted = data['w'][sorted_indices]
        amp_sorted = data['amp'][sorted_indices]

        # Crear un gráfico separado para cada valor de k
        plt.figure(figsize=(8, 6))
        plt.plot(w_sorted, amp_sorted, marker='o', linestyle='-', color=colors[i], label=f'k = {k:.2f}')
        plt.title(f'k = {k:.2f}')
        plt.ylabel('Amplitud máxima')
        plt.xlabel('Frecuencia angular externa (w)')
        plt.grid(True)
        plt.legend()

        # Añadir anotación con el valor máximo de amplitud
        max_amp_index = np.argmax(amp_sorted)
        plt.annotate(f'Max: {amp_sorted[max_amp_index]:.2f} at w={w_sorted[max_amp_index]:.2f}',
                     xy=(w_sorted[max_amp_index], amp_sorted[max_amp_index]),
                     xytext=(5, 5), textcoords='offset points')

        # Guardar cada gráfico en un archivo separado
        plt.tight_layout()
        plt.savefig(f'outputs/multiple/amplitud_vs_w_k_{k:.2f}.jpg', format='jpg', dpi=300)
        plt.close()

if __name__ == "__main__":
    all_data = analyze_data()
    plot_results(all_data)
    print("Análisis completado. Gráficos guardados en archivos separados.")
