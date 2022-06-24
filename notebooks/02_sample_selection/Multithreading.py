import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import lightkurve as lk
from sklearn.utils import resample
from tqdm import tqdm
import time
import concurrent.futures

names = ['EPIC','Campaign','Teff','log g','Prot','ΔProt','hpeak','Rvar','Kp','MG']

df = pd.read_csv('../../data/Reinhold_Hekker2020/table2.dat', delim_whitespace=True, names=names, na_values='---')

criterion1 = (df.Prot > 1) & (df.Prot < 10)
criterion2 = (df.Rvar > 0.5) & (df.Rvar < 20)
criterion3 = (df.Teff > 4000) & (df.Teff < 4500)
criteria = criterion1 & criterion2 & criterion3

df_subset = df[criteria].reset_index(drop=True)

df_subset['N_EVEREST'] = np.NaN
df_subset['N_TESS_SPOC'] = np.NaN
df_subset['Period_TESS'] = 0
df_subset['Amplitude_TESS'] = 0
df_subset['Period_K2'] = 0
df_subset['Amplitude_K2'] = 0
df_subset['Sector'] = np.NaN

df_tiny = df_subset.head(15)
df_subset = df_tiny

n_sources = len(df_subset)

def add_data(mission, idx, sr, num):
    lc = sr[num].download()
    # remove NaNs and normalize the data
    lc = lc.remove_nans().normalize()
    # find the amplitude percentage
    vector = lc.flux.value
    lo, hi = np.percentile(vector, (5, 95))
    peak_to_valley = hi-lo
    # add the data to the table
    df_subset.loc[idx, f'Amplitude_{mission}'] = peak_to_valley
    # change the lightcurve into a periodogram and find its period
    period = float(lc.to_periodogram().period_at_max_power.to_value())
    # add the period to the data table
    df_subset.loc[idx, f'Period_{mission}'] = period
    if mission == "TESS":
        # find the sector number and add it to the data table
        df_subset.loc[idx, 'Sector'] = lc.sector

# def download(name, mission, idx):
#     if mission == 'TESS':
#         sr = lk.search_lightcurve(name, mission=mission)
#         df_subset.loc[idx, 'N_TESS_SPOC'] = len(sr)
#     elif mission == 'K2':
#         sr = lk.search_lightcurve(name, mission=mission, author='EVEREST')
#         df_subset.loc[idx, 'N_EVEREST'] = len(sr)

def download_TESS(name):
    sr = lk.search_lightcurve(name, mission='TESS')
    return sr

def download_K2(name):
    sr = lk.search_lightcurve(name, author='EVEREST')
    return sr

    # if len(sr) > 0:
    #     try:
    #         # download the data for the lightcurve
    #         add_data(mission, idx, sr, 0)
    #     except:
    #         add_data(mission, idx, sr, 1)
            
def main():
    # start = time.time()
    # for i in tqdm(range(n_sources)):
    #     # find the name of the star
    #     name = 'EPIC ' + df_subset.iloc[i].EPIC.astype(int).astype(str)
    #     download(name, 'TESS', i)
    #     download(name, 'K2', i)
    # end = time.time()
    start = time.time()

    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        names = []
        for i in range(n_sources):
            # find the name of the star
            names.append('EPIC ' + df_subset.iloc[i].EPIC.astype(int).astype(str))
            # args1 = [names, 'TESS', df_subset.index]
            # args2 = [names, 'K2', df_subset.index]

        e1 = executor.map(download_TESS, names)
        e2 = executor.map(download_K2, names)

        TESS_search_results = list(e1)
        K2_search_results = list(e2)
        

        for i in range(n_sources):
            df_subset.loc[i, 'N_TESS_SPOC'] = TESS_search_results[i]
            df_subset.loc[i, 'N_EVEREST'] = K2_search_results[i]

    

            
        
    # print(df_subset)
    end = time.time()
    # print(end-start)
    
if __name__ == "__main__":
    main()