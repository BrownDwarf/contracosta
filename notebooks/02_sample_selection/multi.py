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

# df_subset = df_tiny

n_sources = len(df_subset)

def add_data(data):
    # data = [mission, index, search result]
    mission, idx, sr = data
    def add_data_helper(mission, idx, sr, num):
        lc = sr[num].download()
        # remove NaNs and normalize the data
        lc = lc.remove_nans().remove_outliers()#.normalize()
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
        if mission == 'TESS':
            # find the sector number and add it to the data table
            df_subset.loc[idx, 'Sector'] = lc.sector

    if len(sr) > 0:
        try:
            add_data_helper(mission, idx, sr, 0)
        except:
            add_data_helper(mission, idx, sr, 1)
        finally:
            return
            
            
def download(data):
    name, index, mission = data
    if mission == 0:
        sr = lk.search_lightcurve(name, mission='TESS')
        df_subset.loc[index, 'N_TESS_SPOC'] = len(sr)
    elif mission == 1:
        sr = lk.search_lightcurve(name, author='EVEREST')
        df_subset.loc[index, 'N_EVEREST'] = len(sr)
    return sr

def main():
    start = time.time()

    TESS_download = []
    K2_download = []
    for i in range(n_sources):
        # find the name of the star
        name = 'EPIC ' + df_subset.iloc[i].EPIC.astype(int).astype(str)
        TESS_download.append([name, i, 0])
        # K2_download.append([name, i, 1])


    TESS_data = []
    K2_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        TESS_sr = executor.map(download, TESS_download)
        # K2_sr = executor.map(download, K2_download)

        for result in TESS_sr:
            TESS_data.append(['TESS', i, result])
        # for result in K2_sr:
        #     K2_data.append(['K2', i, result])


    # with concurrent.futures.ThreadPoolExecutor() as executor:

    #     executor.map(add_data, TESS_data)
#         executor.map(add_data, K2_data)
    for i in range(n_sources):
        add_data(TESS_data[i])
    #     add_data(K2_data[i])
    
    end = time.time()
    
    sorted_df = df_subset.sort_values(by='EPIC')
    print(sorted_df)
    print(end-start)
    
if __name__ == '__main__':
    main()