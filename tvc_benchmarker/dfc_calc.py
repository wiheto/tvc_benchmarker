import teneto
import tvc_benchmarker
import numpy as np
import pandas as pd
def dfc_calc(data,methods=['SW','TSW','SD','JC','TD'],sw_window=63,taper_name='norm',taper_properties=[0,10],sd_distance='euclidean',mtd_window=7,mi='alpha',colind=None):
    """
    Required parameters for the various differnet methods:

    If method == 'SW'
        sw_window = [Integer]
            Length of sliding window

    If method == 'TSW'
        sw_window = [Integer]
            Length of sliding window
        taper_name = [string]
            Name of scipy.stats distribution used (see teneto.derive.derive for more information)
        taper_properties = [list]
            List of the different scipy.stats.[taper_name] properties. E.g. if taper_name = 'norm'; taper_properties = [0,10] with me the mean and standard deviation of the distribution.
    If method == 'SD'
        sd_distance = [string]
            Distance funciton used to calculate the similarity between time-points. Can be any of the distances functions in scipy.spatial.distance.
    if method == 'JC'
        There are no parmaeters, have empty dictionary as parameter input.
    if method == 'MTD'
        mtd_window= [Integer]
            Length of window

    # mi='alpha'
    """

    # If data is a string, load precalcuated data
    if isinstance(data, str):

        if data == 'sim-1' and not colind:
            colind = 1
        elif (data == 'sim-2' or data == 'sim-3' or data == 'sim-4') and not colind:
            colind = 2
        elif colind:
            pass
        else:
            raise ValueError('unknown simulation. Input must be  "sim-1", "sim-2", "sim-3" or "sim-4"')
        df = pd.read_csv(tvc_benchmarker.__path__[0] + '/data/dfc/' + data + '_dfc.csv',index_col=np.arange(0,colind))
        # Get methods
        requested_methods = list(set(methods).intersection(df.columns))
        df[requested_methods]

    #Otherwise calculate
    else:

        # Make methods variable a list if single string is given
        if isinstance(methods,str):
            methods = [methods]

        if isinstance(mi,str):
            mi = [mi]

        dfc={}
        params = {}
        for m in mi:
            params[m] = np.unique(data.index.get_level_values(m))
        mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)


        #Sliding window
        if 'SW' in methods:

            dfc['SW'] = []

            dfc_params={}
            dfc_params['windowsize']=sw_window
            dfc_params['method'] = 'slidingwindow'
            dfc_params['dimord'] = 'node,time'
            dfc_params['postpro'] = 'fisher'
            dfc_params['report'] = 'no'

            if mi_parameters[0]:
                # Do this if there are multiple mi parameters
                for sim_it, mi_params in enumerate(mi_parameters):
                    ts1 = data['timeseries_1'][mi_params]
                    ts2 = data['timeseries_2'][mi_params]
                    connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                    dfc['SW'].append(np.lib.pad(connectivity,int((sw_window-1)/2),mode='constant',constant_values=np.nan))
            # Otherwise do this
            else:
                ts1 = data['timeseries_1']
                ts2 = data['timeseries_2']
                connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                dfc['SW'].append(np.lib.pad(connectivity,int((sw_window-1)/2),mode='constant',constant_values=np.nan))
            # Line up all appened arrays
            dfc['SW'] = np.concatenate(dfc['SW'])


        #Tapered sliding window
        if 'TSW' in methods:

            dfc['TSW'] = []

            dfc_params={}
            dfc_params['windowsize']=sw_window
            dfc_params['distribution']=taper_name
            dfc_params['distribution_params']=taper_properties
            dfc_params['method'] = 'taperedslidingwindow'
            dfc_params['dimord'] = 'node,time'
            dfc_params['postpro'] = 'fisher'
            dfc_params['report'] = 'no'

            if mi_parameters[0]:
                # Do this if there are multiple mi parameters
                for sim_it, mi_params in enumerate(mi_parameters):
                    ts1 = data['timeseries_1'][mi_params]
                    ts2 = data['timeseries_2'][mi_params]
                    connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                    dfc['TSW'].append(np.lib.pad(connectivity,int((sw_window-1)/2),mode='constant',constant_values=np.nan))
            # Otherwise do this
            else:
                ts1 = data['timeseries_1']
                ts2 = data['timeseries_2']
                connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                dfc['TSW'].append(np.lib.pad(connectivity,int((sw_window-1)/2),mode='constant',constant_values=np.nan))
            # Line up all appened arrays
            dfc['TSW'] = np.concatenate(dfc['TSW'])

        #Spatial distance
        if 'SD' in methods:

            dfc['SD'] = []

            dfc_params={}
            dfc_params['distance']='euclidean'
            dfc_params['method'] = 'spatialdistance'
            dfc_params['dimord'] = 'node,time'
            dfc_params['postpro'] = 'fisher'
            dfc_params['report'] = 'no'

            if mi_parameters[0]:
                # Do this if there are multiple mi parameters
                for sim_it, mi_params in enumerate(mi_parameters):
                    ts1 = data['timeseries_1'][mi_params]
                    ts2 = data['timeseries_2'][mi_params]
                    connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                    dfc['SD'].append(connectivity)
            # Otherwise do this
            else:
                ts1 = data['timeseries_1']
                ts2 = data['timeseries_2']
                connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                dfc['SD'].append(connectivity)
            # Line up all appened arrays
            dfc['SD'] = np.concatenate(dfc['SD'])


        #Jackknife
        if 'JC' in methods:

            dfc['JC'] = []

            dfc_params={}
            dfc_params['method'] = 'jackknife'
            dfc_params['dimord'] = 'node,time'
            dfc_params['postpro'] = 'fisher'
            dfc_params['report'] = 'no'

            if mi_parameters[0]:
                # Do this if there are multiple mi parameters
                for sim_it, mi_params in enumerate(mi_parameters):
                    ts1 = data['timeseries_1'][mi_params]
                    ts2 = data['timeseries_2'][mi_params]
                    connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                    dfc['JC'].append(connectivity)
            # Otherwise do this
            else:
                ts1 = data['timeseries_1']
                ts2 = data['timeseries_2']
                connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                dfc['JC'].append(connectivity)
            # Line up all appened arrays
            dfc['JC'] = np.concatenate(dfc['JC'])


        #Temporal derivative
        if 'MTD' in methods:

            dfc['TD'] = []

            dfc_params={}
            dfc_params['method'] = 'mtd'
            dfc_params['dimord'] = 'node,time'
            dfc_params['postpro'] = 'no'
            dfc_params['windowsize'] = mtd_window
            dfc_params['report'] = 'no'

            if mi_parameters[0]:
                # Do this if there are multiple mi parameters
                for sim_it, mi_params in enumerate(mi_parameters):
                    ts1 = data['timeseries_1'][mi_params]
                    ts2 = data['timeseries_2'][mi_params]
                    connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                    dfc['TD'].append(np.lib.pad(np.hstack([np.nan,connectivity]),int((mtd_window-1)/2),mode='constant',constant_values=np.nan))
            # Otherwise do this
            else:
                ts1 = data['timeseries_1']
                ts2 = data['timeseries_2']
                connectivity = teneto.derive.derive(np.array([ts1,ts2]),dfc_params)[0,1,:]
                dfc['TD'].append(np.lib.pad(np.hstack([np.nan,connectivity]),int((mtd_window-1)/2),mode='constant',constant_values=np.nan))
            # Line up all appened arrays
            dfc['TD'] = np.concatenate(dfc['TD'])




        df = pd.DataFrame(data=dfc, index=data.index)
    return df
