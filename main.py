from functions import interpolate_dsdm, plot_cross_section

def main():
    print("Choose action: 'calc' to calculate cross section or 'plot' to plot cross section.")
    action = input("Action [calc/plot]: ").strip().lower()

    contribution = input("Contribution (full/piDonly/rhoNonly/sigNonly/Tdironly): ").strip()
    isp = int(input("Spectator (isp=1,2,3): "))
    ic = int(input("Process number (1-5): "))

    if action == 'calc':
        W = float(input("Enter W value [GeV]: "))
        M = float(input("Enter Invariant Mass value [GeV]: "))
        dsdm = interpolate_dsdm(contribution, isp, ic, W, M)
        if dsdm is None or (hasattr(dsdm, 'dtype') and dsdm != dsdm):  # check for NaN
            print("Interpolation returned NaN. Check input values and data range.")
        else:
            print(f"Interpolated dσ/dM at W={W:.5f} GeV, M={M:.5f} GeV: {dsdm:.6e} mbarn/GeV")
    
    elif action == 'plot':
        parameter = input("Plot as function of 'as_W' or 'as_M': ").strip()
        fixed_val = float(input("Enter fixed value (W [GeV] if as_M, or M [GeV] if as_W): "))
        try:
            plot_cross_section(contribution, isp, ic, parameter, fixed_val)
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Invalid action. Choose 'calc' or 'plot'.")

if __name__ == "__main__":
    main()
