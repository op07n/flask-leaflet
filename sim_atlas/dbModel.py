import json
import numpy as np

from typing import List


class NHMFault:
    """Contains the information for a single fault from a NHM file
    Attributes
    ----------
    name : str
    tectonic_type : str
    fault_type : str
    length : float, (km)
    length_sigma : float (km)
    dip : float  (deg)
    dip_sigma : float (deg)
    dip_dir : float
    rake : float
    dbottom : float (km)
    dbottom_sigma : float (km)
    dtop_mean : float (km)
    dtop_min : float (km)
    dtop_max : float (km)
    slip_rate : float (mm/yr)
    slip_rate_sigma : float (mm/yr)
    coupling_coeff : float (mm/yr)
    coupling_coeff_sigma : float (mm/yr)
    mw : float
    recur_int_median : float (yr)
    trace: np.ndarray
        fault surface trace (lon, lat)
    """

    def __init__(self, entry: List[str]):
        """Creates an NHMFault instance from the given NHM text.
        Parameters
        ----------
        entry : List of str
            The rows of an NHM file of one fault.
            Format:
                Row 1: FaultName
                Row 2: TectonicType , FaultType
                Row 3: LengthMean , LengthSigma (km)
                Row 4: DipMean , DipSigma (deg)
                Row 5: DipDir
                Row 6: Rake (deg)
                Row 7: RupDepthMean , RupDepthSigma (km)
                Row 8: RupTopMean, RupTopMin RupTopMax  (km)
                Row 9: SlipRateMean , SlipRateSigma (mm/yr)
                Row 10: CouplingCoeff , CouplingCoeffSigma (mm/yr)
                Row 11: MwMedian , RecurIntMedian  (yr)
                Row 12: Num Locations on Fault Surface
                Row 13+: Location Coordinates (Long, Lat)
        """
        rows = list(map(str.strip, entry.split("\n")))

        def str2floats(line):
            return list(map(float, line.split()))

        self.name = rows[0]
        self.tectonic_type, self.fault_type = rows[1].split()
        self.length, self.length_sigma = str2floats(rows[2])
        self.dip, self.dip_sigma = str2floats(rows[3])
        self.dip_dir = float(rows[4])
        self.rake = float(rows[5])
        self.dbottom, self.dbottom_sigma = str2floats(rows[6])
        self.dtop, self.dtop_min, self.dtop_max = str2floats(rows[7])
        self.slip_rate, self.slip_rate_sigma = str2floats(rows[8])
        self.coupling_coeff, self.coupling_coeff_sigma = str2floats(rows[9])
        self.mw, self.recur_int_median = str2floats(rows[10])
        self.trace = np.array(list(map(float, " ".join(rows[12:]).split()))).reshape((-1, 2))
        # TODO: add x y z fault plane data as in SRF info
        # TODO: add leonard mw function


def load_nhm(nhm_path: str, skiprows: int=15):
    """Reads the nhm_path and returns a dictionary of NHMFault by fault name.
    Parameters
    ----------
    nhm_path: str
        NHM file to load
    skiprows: int
        Skip the first skiprows lines; default: 15.
    Returns
    -------
    dict of NHMFault by name
    """
    with open(nhm_path, "r") as f:
        rows = "".join(f.readlines()[skiprows:])

    faults = {}
    for entry in rows.split("\n\n"):
        nhm_fault = NHMFault(entry)
        faults[nhm_fault.name] = nhm_fault

    return faults


def dump_json(faults_dict, output_json, faults_selected=None):
    if not faults_selected:
        faults_selected = faults_dict.keys()
    fd_list = []
    for f in faults_selected:
        fd = {}
        fd['name'] = f
        traces = faults_dict[f].trace.tolist()
        traces = [[lat, lon] for [lon, lat] in traces]
        fd['traces'] = traces
        fd['video'] = 'https://www.youtube.com/watch?v=qZkOTI4x_cc'
        fd['slip_rate'] = faults_dict[f].slip_rate
        fd['magnitude'] = faults_dict[f].mw
        fd['recurrence_interval'] = faults_dict[f].recur_int_median
        fd_list.append(fd)

    with open(output_json, 'w') as ff:
        json.dump(fd_list, ff)

# faults = load_nhm('/home/melody/flask-leaflet/sim_atlas/static/data/NZ_FLTmodel_2010_v18p6.txt')
# dump_json(faults, '/home/melody/flask-leaflet/sim_atlas/static/data/fault_traces.json')
# dump_json(faults, '/home/melody/flask-leaflet/sim_atlas/static/data/fault_traces3.json', ["AlpineF2K","Albury",'Kelly','Hollyford','BooBooEAST'])


# with open('traces.sql', 'w') as f:
#     count = 0
#     for fault in faults.keys():
#         traces = faults[fault].trace.tolist()
#         for i in range(len(traces)):
#             long, lat = traces[i]
#             f.write("(" + str(count)+ ",'"+fault+"',"+str(lat)+","+str(long)+"),")
#             count +=1

# with open('video.sql', 'w') as f:
#     for fault in faults.keys():
#         f.write("('"+fault+"',"+"'https://www.youtube.com/watch?v=qZkOTI4x_cc'"+"),")
#

# import os
# import glob
# from qcore import srf
# dir = '/nesi/nobackup/nesi00213/RunFolder/Cybershake/v18p6_rerun/Data/Sources'
# f_list = []
# for f in os.listdir(dir):
#     f_dict = {}
#     f_dir = os.path.join(dir, f, 'Srf')
#     print(f_dir)
#     if os.path.isdir(f_dir):
#         srf_file = glob.glob1(f_dir, '*HYP01-*.srf')[0]
#         bounds = srf.get_bounds(os.path.join(f_dir, srf_file))
#         f_dict["name"] = f
#         f_dict["bounds"] = bounds
#         f_list.append(f_dict)
# with open("data/v18p6_rerun_all_faults_bounds.json", 'w') as ff:
#     json.dump(f_list, ff)

# fd = []
#
# with open("/home/melody/flask-leaflet/sim_atlas/static/data/v18p6_rerun_all_faults_bounds.json", 'r') as ff:
#     f_dicts = json.load(ff)
#     for f in f_dicts:
#         bounds = f['bounds']
#         d=[]
#         for plane in bounds:
#             s=[]
#             for lon,lat in plane:
#                 s.append([lat,lon])
#             d.append(s)
#         f['bounds'] = d
#         fd.append(f)
#
# with open("/home/melody/flask-leaflet/sim_atlas/static/data/v18p6_rerun_all_faults_bounds.json", 'w') as ff2:
#     json.dump(fd,ff2)
faults = load_nhm('/home/melody/flask-leaflet/sim_atlas/static/data/NZ_FLTmodel_2010_v18p6.txt')
with open("/home/melody/flask-leaflet/sim_atlas/static/data/v18p6_rerun_all_faults_bounds.json", 'r') as ff:
    f_dicts = json.load(ff)
    for fd in f_dicts:
        fault = faults[fd['name']]
        fd['video'] = 'https://www.youtube.com/watch?v=qZkOTI4x_cc'
        fd['slip_rate'] = fault.slip_rate
        fd['magnitude'] = fault.mw
        fd['recurrence_interval'] = fault.recur_int_median
