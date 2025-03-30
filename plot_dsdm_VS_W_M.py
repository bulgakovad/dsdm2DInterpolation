import numpy as np
import matplotlib.pyplot as plt
import os


def read_data(filepath):
    data = []
    with open(filepath, 'r') as file:
        content = file.read().strip()
        blocks = content.split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            for line in lines:
                if line.strip():  # Skip empty lines
                    columns = [float(x) for x in line.strip().split()]
                    if len(columns) == 8:  # Ensure correct number of columns
                        data.append(columns)
    return data


def plot_dsdm(contribution, isp, ic, parameter, fixed_value):
    filename = f"input_files/dsdm-{contribution}{isp}"
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    data = read_data(filename)

    isp_col, W_col, M_col = 0, 1, 2
    dsdm_col = 2 + ic  # ic from 1-5

    tol = 1e-3
    if parameter == 'as_M':
        filtered = [row for row in data if abs(row[W_col] - fixed_value) < 1e-5]
        if not filtered:
            print(f"No data found for W = {fixed_value}")
            return
        filtered = sorted(filtered, key=lambda x: x[M_col])
        x_values = [row[M_col] for row in filtered]
        y_values = [row[dsdm_col] for row in filtered]
        xlabel = 'M, GeV'
        title = f'{contribution}, Process {ic}, isp={isp}, W={fixed_value} GeV'

    elif parameter == 'as_W':
        filtered = [row for row in data if abs(row[M_col] - fixed_value) < tol]
        if not filtered:
            print(f"No data found for M = {fixed_value}")
            return
        filtered = sorted(filtered, key=lambda x: x[W_col])
        x_values = [row[W_col] for row in filtered]
        y_values = [row[dsdm_col] for row in filtered]
        xlabel = 'W, GeV'
        title = f'{contribution}, Process {ic}, isp={isp}, M={fixed_value} $\pm${tol} GeV'
    else:
        print("Parameter must be 'as_M' or 'as_W'")
        return

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, 'o-', linewidth=2)
    plt.xlabel(xlabel)
    plt.ylabel(r'$d\sigma/dM$, mbarn/GeV')
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    # Create 'plots' directory if it does not exist
    plots_dir = "plots"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    plot_filename = f"{plots_dir}/{contribution}_isp={isp}_ic={ic}_{parameter}_for_W_or_M={fixed_value}.png"
    plt.savefig(plot_filename)
    print(f"Plot saved as {plot_filename}")
    plt.show()


# === USER PARAMETERS ===
contribution = 'sigNonly'     # full, piDonly, rhoNonly, sigNonly, Tdironly
isp = 1                   # 1, 2, 3
ic = 3                    # process (1 to 5)
parameter = 'as_M'        # 'as_M' or 'as_W' -  to plot cross sections function of M or W
fixed_value = 1.6   # Specify your W or M here based on 'parameter'

# Run the plotting function
plot_dsdm(contribution, isp, ic, parameter, fixed_value=fixed_value)
