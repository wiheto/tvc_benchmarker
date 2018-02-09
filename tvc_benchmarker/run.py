import tvc_benchmarker
import os
import json
import pandas as pd
import numpy as np

# TODO add usesaved for stats

def run_simulations(routine_version=1.0,usesaved='yes',new_method=None,params_new_method=None,output_dir=None):

    """

    :params_new_method: a dictionary parameter file or path to json file containing parameter file.
        :params['dfc'][method_index]: where method_index is a stringed integer. So the first method is always params['dfc']['0']
        e.g.
            :params['dfc']['0']: = {}
        Within each method's subdictionary requires a 'name' (str), 'method' (str), and 'params' (dict). e.g.
            :params['dfc']['0']['method']: = 'new_method'
            :params['dfc']['0']['name']: = 'new_method_params_2'
            :params['dfc']['0']['params']: = {}

        'method' should be the name of the method. 'name' should be the specific instance (such as a parameter configuration).
        'name' has to be unique across simulations while method can be used in multiple instances. If there is only one instance than 'name' can equal 'method'.

        Within the params :params['dfc']['0']['params']: dicitonary, all used parameters in new_method function should be specified. If new_method(x,y,window=20,distribution='Gaussian'), then
            :params['dfc']['0']['params']['window']: = 20
            :params['dfc']['0']['params']['distribution']: = 'Gaussian'

        If only one method is used, the ['dfc']['0'] can be dropped.


    """


    # Load parameters for the simulation routine for specified version
    loaded = 0
    if os.path.isfile(tvc_benchmarker.__path__[0] + '/data/routine_params/' + str(routine_version) + '.json'):
        params_path = tvc_benchmarker.__path__[0] + '/data/routine_params/' + str(routine_version) + '.json'
    elif os.path.isfile(str(routine_version)):
        params_path = str(routine_version)
    elif isinstance(routine_version,dict):
        params = routine_version
        loaded = 1
    else:
        raise ValueError('Cannot find routine parameter file')
    if loaded == 0:
        with open(params_path) as f:
            params = json.load(f)
        f.close()
    params = tvc_benchmarker.check_params(params,'dfc')
    params = tvc_benchmarker.check_params(params,'simulation')

    # Load new method parameter file, if params_new_method is a valid path
    if params_new_method:
        if isinstance(params_new_method,dict):
            pass
        elif os.path.isfile(params_new_method):
            params_path = str(params_new_method)
            params_new_method = []
            with open(params_path) as f:
                params_new_method = json.load(f)
            f.close()
        else:
            raise ValueError('params_new_method is specified but does not seem to be dicitonary or valid path to json file containing dictionary')
        params_new_method = tvc_benchmarker.check_params(params_new_method,'dfc')

    # If only one new_method is given (i.e. as function). Convert to list
    if new_method and not isinstance(new_method,list):
        new_method = [new_method]

    # Specify output_dir if none given
    if output_dir == None:
        output_dir = './tvc_benchmarker/simulation/' + str(routine_version) + '/'
        os.makedirs(output_dir,exist_ok=True)

    # Create output directories
    fig_dir = output_dir + '/figures/'
    table_dir = output_dir + '/tables/'
    dat_dir = output_dir + '/data/'
    stat_dir = output_dir + '/stats/'

    os.makedirs(fig_dir,exist_ok=True)
    os.makedirs(table_dir,exist_ok=True)
    os.makedirs(dat_dir,exist_ok=True)
    os.makedirs(stat_dir,exist_ok=True)


    for sim_i in range(0,len(params['simulation'])):

        sim = params['simulation'][sim_i]
        sim['multi_index'] = sorted(sim['multi_index'])

        print("----- RUNNING SIMULATION: " + sim['name'] + "-----")

        # Load saved data or calculate again
        if usesaved == 'yes':
            data = tvc_benchmarker.load_data(sim['name'],len(sim['multi_index'])+1)
            dfc = tvc_benchmarker.dfc_calc(sim['name'],colind=len(sim['multi_index'])+1)
        else:
            multi_index = list([sim['params'][n] for n in sim['multi_index']])
            multi_index_labels = list(sim['multi_index'])
            #ind = pd.MultiIndex.from_product((multi_index) + [np.arange(0,sim['params']['n_samples'])], names=multi_index_labels + ['time'])
            data = tvc_benchmarker.gen_data(sim)
            dfc = pd.DataFrame(index=data.index)
            for dfc_i in range(0,len(params['dfc'])):
                calcdfc = tvc_benchmarker.dfc_calc(data,methods=params['dfc'][dfc_i]['method'],**params['dfc'][dfc_i]['params'],mi=multi_index_labels)
                dfc[params['dfc'][dfc_i]['name']]  = calcdfc.values


        # Run the newly entered method(s)
        if new_method:
            for i,nm in enumerate(new_method):
                dfc_new = tvc_benchmarker.calc_new_method(data,nm,params_new_method['dfc'][i])
                dfc[params_new_method['dfc'][i]['name']] = dfc_new
        # Save dfc estimates
        dfc.to_csv(dat_dir + sim['name'] + '_dfc.csv')
        data.to_csv(dat_dir + sim['name'] + '_data.csv')

        # Stats and plotting
        if sim['name'] == 'sim-1':

            tvc_benchmarker.plot_timeseries(data,plot_autocorr='yes',mi=[],fig_dir=fig_dir,fig_prefix=sim['name'])
            tvc_benchmarker.plot_dfc_timeseries(dfc,mi=[],fig_dir=fig_dir,fig_prefix=sim['name'])
            tvc_benchmarker.plot_method_correlation(dfc,mi=[],fig_dir=fig_dir,fig_prefix=sim['name'])

        elif sim['name'] == 'sim-2' or sim['name'] == 'sim-3' or sim['name'] == 'sim-4':


            tvc_benchmarker.plot_timeseries(data,plot_autocorr='no',fig_dir=fig_dir,fig_prefix=sim['name'],mi=sim['multi_index'])
            tvc_benchmarker.plot_fluctuating_covariance(data,fig_dir=fig_dir,fig_prefix=sim['name'],mi=sim['multi_index'])
            dfc=dfc.dropna()
            tvc_benchmarker.model_dfc(data,dfc,stat_dir,sim['name'],mi=sim['multi_index'],model_params=params['stats']['trace'])
            tvc_benchmarker.calc_waic(dfc,model_dir=stat_dir,save_dir=table_dir,file_prefix=sim['name'],burn=params['stats']['burn'],mi=sim['multi_index'])

            tvc_benchmarker.plot_betadfc_distribution(dfc,dat_dir=stat_dir,fig_dir=fig_dir,model_prefix=sim['name'],burn=params['stats']['burn'],mi=sim['multi_index'])
