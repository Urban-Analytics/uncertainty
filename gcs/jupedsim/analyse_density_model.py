import numpy as np
import pandas as pd

fp1 = 'report_results/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_1.dat'
fp2 = 'report_results/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_2.dat'

def get_zone(fp):
    zone = pd.read_csv(fp, sep='\t', skiprows=2)
    zone.pop('Voronoi velocity(m/s)')
    zone.columns = ['frame', 'density', 'velocity']
    return np.mean(zone['density']), np.var(zone['density'], ddof=1)

zone1 = get_zone(fp1)
zone2 = get_zone(fp2)
print(zone1)
print(zone2)
