import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CloughTocher2DInterpolator

def read_data(contribution, isp):
    """
    Reads the data from the file "input_files/dsdm-{contribution}{isp}"
    and returns a NumPy array.
    """
    filename = f"input_files/dsdm-{contribution}{isp}"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")
    
    data = []
    with open(filename, 'r') as file:
        blocks = file.read().strip().split("\n\n")
        for block in blocks:
            for line in block.strip().split("\n"):
                cols = line.strip().split()
                if len(cols) == 8:
                    data.append([float(x) for x in cols])
    return np.array(data)

def get_interpolator(contribution, isp, ic):
    """
    Returns a 2D interpolator for the cross section of channel `ic`
    (ic = 1-5) as a function of (W, M). Data is read from the file.
    """
    data = read_data(contribution, isp)
    # Column indices: 1: W, 2: M, then columns 3-7 are cross sections
    W_vals = data[:, 1]
    M_vals = data[:, 2]
    dsdm_vals = data[:, ic + 2]  # ic=1 corresponds to column 3, etc.
    
    points = np.column_stack((W_vals, M_vals))
    interpolator = CloughTocher2DInterpolator(points, dsdm_vals)
    return interpolator, data

def interpolate_dsdm(contribution, isp, ic, W_query, M_query):
    """
    Returns the interpolated cross section for the given (W, M).
    """
    interpolator, _ = get_interpolator(contribution, isp, ic)
    return interpolator(W_query, M_query)

def plot_cross_section(contribution, isp, ic, parameter, fixed_value, num_points=200, save=True):
    """
    Plots a smooth curve of the cross section using 2D interpolation.
    
    - If parameter=='as_M': fixed_value is W (in GeV) and the plot shows dσ/dM vs M.
    - If parameter=='as_W': fixed_value is M (in GeV) and the plot shows dσ/dM vs W.
    
    Only the region where the interpolator returns valid (finite) values is plotted.
    The plot is saved in the folder "plots" with a filename like:
      full_isp1_ic1_VS_M_for_W=1.5.png (for as_M)
      full_isp1_ic1_VS_W_for_M=1.5.png (for as_W)
    """
    interpolator, data = get_interpolator(contribution, isp, ic)
    
    # Determine overall ranges from the data
    W_min, W_max = data[:, 1].min(), data[:, 1].max()
    M_min, M_max = data[:, 2].min(), data[:, 2].max()
    
    if parameter == 'as_M':
        # fixed_value is W
        if not (W_min <= fixed_value <= W_max):
            raise ValueError(f"Fixed W value {fixed_value} is out of range [{W_min}, {W_max}].")
        # Generate a fine grid of M values over the global M range
        M_fine = np.linspace(M_min, M_max, num_points)
        dsdm_fine = interpolator(fixed_value, M_fine)
        valid = np.isfinite(dsdm_fine)
        if not np.any(valid):
            raise ValueError(f"No valid interpolation values for fixed W = {fixed_value}")
        x = M_fine[valid]
        y = dsdm_fine[valid]
        xlabel = "Invariant Mass M [GeV]"
        title = f"{contribution}, isp={isp}, Process {ic}, W={fixed_value:g} GeV"
        fixed_label = f"for_W={fixed_value:g}"
    elif parameter == 'as_W':
        # fixed_value is M
        if not (M_min <= fixed_value <= M_max):
            raise ValueError(f"Fixed M value {fixed_value} is out of range [{M_min}, {M_max}].")
        # Generate a fine grid of W values over the global W range
        W_fine = np.linspace(W_min, W_max, num_points)
        dsdm_fine = interpolator(W_fine, fixed_value)
        valid = np.isfinite(dsdm_fine)
        if not np.any(valid):
            raise ValueError(f"No valid interpolation values for fixed M = {fixed_value}")
        x = W_fine[valid]
        y = dsdm_fine[valid]
        xlabel = "W [GeV]"
        title = f"{contribution}, isp={isp}, Process {ic}, M={fixed_value:g} GeV"
        fixed_label = f"for_M={fixed_value:g}"
    else:
        raise ValueError("Parameter must be 'as_M' or 'as_W'.")
    
    # Plot the smooth curve
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, '-', linewidth=2)
    plt.xlabel(xlabel)
    margin = 0.05 * (x.max() - x.min())
    plt.xlim(x.min() - margin, x.max() + margin)
    plt.ylabel(r'$d\sigma/dM$ [mbarn/GeV]')
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot with the desired filename convention
    if save:
        if not os.path.exists("plots_interpolated"):
            os.makedirs("plots_interpolated")
        if parameter == 'as_M':
            fname = f"plots_interpolated/{contribution}_isp{isp}_ic{ic}_VS_M_{fixed_label}.png"
        else:
            fname = f"plots_interpolated/{contribution}_isp{isp}_ic{ic}_VS_W_{fixed_label}.png"
        plt.savefig(fname, dpi=300)
        print(f"Plot saved as {fname}")
    
    plt.show()

