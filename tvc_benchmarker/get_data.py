import numpy as np
import tvc_benchmarker
import os
import pandas as pd

def load_data(data,colind = None):
    """
    *Input*

    data: "sim-1", "sim-2", "sim-3"

    *Returns*

    Dataframe of precomputed data (made using default parameters).

    """
    if not colind:
        if data == 'sim-1':
            colind = 1
        elif data == 'sim-2' or data == 'sim-3' or data == 'sim-4':
            colind = 2
        else:
            raise ValueError('unknown simulation. Input must be  "sim-1", "sim-2" or "sim-3"')

    return pd.read_csv(tvc_benchmarker.__path__[0] + '/data/data/' + data + '_data.csv',index_col=np.arange(0,colind))


def gen_data_sim1(params,mi=None):

    """
    *INPUT*

    params is a dictionary which must contain the following:

    :n_samples: length of time series. Default=10,000
    :alpha: auto-correlation of time series. Can be single integer or np.array with length of mu
    :mu: Mean of auto-correlated time-series sampled from a multivariate Gaussian distribution. Must be of length 2 or greater.
    :sigma: Covariance matrix for multivariate Gaussian distribution. Array or list with shape of (len(mu),len(mu)).
    :randomseed: set random seed

    *LIMITATIONS*

    Mean and sigma must always stay the same.
    n_samples cannot be multiindex

    *RETURNS*

    :df: pandas dataframe with timeseries_1, timeseries_2.

    """

    np.random.seed(params['randomseed'])
    # generate data

    # Check multiindex and get number of each multiindex
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    x=np.zeros([2, params['n_samples']] + mi_num)
    x = x.reshape([2,int(np.prod(x.shape)/2)])

    for sim_it, mi_params in enumerate(mi_parameters):

        d = dict(params)
        for i in range(0,len(mi)):
            d[mi[i]] = mi_params[i]

        x_start = d['n_samples'] * sim_it
        x_end = d['n_samples'] * (sim_it + 1)
        w=np.random.multivariate_normal(d['mu'],d['sigma'],d['n_samples']).transpose()
        x[:,x_start:x_end] = np.array(w)
        for t in range(1,d['n_samples']):
            x[:,(d['n_samples']*sim_it)+t]=d['alpha']*x[:,(d['n_samples']*sim_it)+t-1]+w[:,t]

    multi_ind = pd.MultiIndex.from_product((mi_param_list) + [np.arange(0,d['n_samples'])], names=mi + ['time'])
    df = pd.DataFrame(data={'timeseries_1': x[0,:],'timeseries_2':x[1,:]}, index=multi_ind)
    return df


def gen_data_sim2(params,mi='alpha'):

    """
    *INPUT*

    Params is a dictionary which contains the following

    :n_samples: length of time series. Default=10,000
    :alpha: auto-correlation of time series. Can be single integer or np.array with length of mu
    :mu: Mean of auto-correlated time-series sampled from a multivariate Gaussian distribution. Must be a array/list of length 2 or 2xn_samples.
    :var: Variance of the time series. Integer or np.array with length of mu
    :covar_mu: Mean of the covariance of the time series.
    :covar_sigma: Variance of the covariance of the time series.
    :randomseed: set random seed

    Additionally, if there is a multi_index variable, this should be specified differently

    :mi: multi_index. list of variable names which have multiple parameters. These parameters should be in a list. E.g. if mi='mu', then mu becomes a list surrounding its contents. e.g. mu=[[0,0],[1,1]]

    *LIMITATIONS*

    As the parameters stand, only 2 time series can be generated (some minor modifications are needed to generate more).
    Input `var` must be integer and cannot vary between the time series.

    *RETURNS*

    :df: pandas dataframe with timeseries_1, timeseries_2, covariance_parameter. Table is multiindexed with alpha and time as the two indexes.

    """
    # Random seed
    np.random.seed(params['randomseed'])

    # Check multiindex and get number of each multiindex
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    # Pre allocate output
    x=np.zeros([2,params['n_samples']] + mi_num)
    fluct_cv = np.zeros([params['n_samples']] + mi_num)

    x = x.reshape([2,int(np.prod(x.shape)/2)])
    fluct_cv = fluct_cv.flatten()

    # Set preliminary arguments
    for sim_it, mi_params in enumerate(mi_parameters):

        d = dict(params)
        for i in range(0,len(mi)):
            d[mi[i]] = mi_params[i]

        # extend mu through timeseries if it is (list of) integers
        d['mu']=np.array(d['mu'],ndmin=2)
        if d['mu'].shape[-1]!=d['n_samples']:
            d['mu']=np.tile(d['mu'].transpose(),d['n_samples'])

        # extend covar_mu through timeseries if is integer
        d['covar_mu']=np.array(d['covar_mu'],ndmin=1)
        if d['covar_mu'].shape[-1]!=d['n_samples']:
            d['covar_mu']=np.tile(d['covar_mu'].transpose(),d['n_samples'])

        for t in range(0,d['n_samples']):
            # At first time point, no autocorrelation of covariance
            if t==0:
                covar = np.random.normal(d['covar_mu'][t],d['covar_sigma'])
            else:
                covar = np.random.normal(d['covar_mu'][t],d['covar_sigma'])+d['alpha']*fluct_cv[(d['n_samples']*sim_it)+t-1]
            x[:,(d['n_samples']*sim_it)+t]=np.random.multivariate_normal(d['mu'][:,t], [[d['var'], covar], [covar, d['var']]], 1)
            fluct_cv[(d['n_samples']*sim_it)+t]=covar

    #x=np.reshape(x,[x.shape[0],np.prod(x.shape[1:])],order='F')
    #fluct_cv=np.reshape(fluct_cv,[np.prod(fluct_cv.shape)],order='F')

    if any(np.abs(fluct_cv)>1): 
        print('TVC BENCHMARKER WARNING: some value(s) of r_t>1 or r_t<-1. Consider changing parameters.')

    multi_ind = pd.MultiIndex.from_product((mi_param_list) + [np.arange(0,d['n_samples'])], names=mi + ['time'])
    df = pd.DataFrame(data={'timeseries_1': x[0,:],'timeseries_2':x[1,:],'covariance_parameter':fluct_cv}, index=multi_ind)
    return df




def gen_data_sim3(params,mi='alpha'):

    """
    *INPUT*

    No input runs the default simulation.

    :n_samples: length of time series. Default=10,000
    :alpha: auto-correlation of time series. Can be single integer or np.array with length of mu
    :hrf_path: Path to a 2xn_samples numpy array with specified HRF. Or "default" to use one ready-made.
    :hrf_zeropad: add additional zeros to HRF function (periods of rest)
    :hrf_scale: make the hrf bigger/smaller compared to the rest of the signal.
    :var: Variance of the time series. Integer or np.array with length of mu
    :covar_mu: Mean of the covariance of the time series.
    :covar_sigma: Variance of the covariance of the time series.
    :randomseed: set random seed

    *LIMITATIONS*

    As the parameters stand, only 2 time series can be generated (some minor modifications are needed to generate more).
    Input `var` must be integer and cannot vary between the time series.

    *RETURNS*

    :df: pandas dataframe with timeseries_1, timeseries_2, covariance_parameter. Table is multiindexed with alpha and time as the two indexes.

    """

    # Commented out stuff is if HRF scale is to be made multi-indexable (not complete though as mi must be changed from hrf_scale to mu prior to going into simulation two. And (for useability) that index should then be changed back to hrf_scale after simulation 2)
    #if isinstance(params['hrf_scale'],int):
    #    params['hrf_scale'] = [params['hrf_scale']]

    if params['hrf_path'] == 'hrf_TR2':
        hrf_saved = np.load(tvc_benchmarker.__path__[0] + '/data/hrf/hrf_TR2.npy')
        hrf = np.zeros([2,len(hrf_saved)+params['hrf_zeropad']])
        hrf[:,0:len(hrf_saved)]=np.vstack([hrf_saved,hrf_saved])
        #hrf_ts = [np.tile(hrf, int(params['n_samples'] / hrf.shape[-1])) for n in params['hrf_scale']]
        hrf_ts = np.tile(hrf, int(params['n_samples'] / hrf.shape[-1])) * params['hrf_scale']
    elif os.path.isfile(params['hrf_path']):
        hrf_ts=np.load(params['hrf_path'])
    else:
        hrf_ts=params['hrf_path']

    params['mu'] = hrf_ts


    df=gen_data_sim2(params,mi=mi)

    return df





def gen_data_sim4(params,mi=None):

    """
    *INPUT*

    No input runs the default simulation.

    :n_samples: length of time series. Default=10,000
    :mu: Mean of auto-correlated time-series sampled from a multivariate Gaussian distribution. Must be a array/list of length 2 or 2xn_samples.
    :var: Variance of the time series. Integer or np.array with length of mu
    :covar_range: list of possible covariance
    :state_length: List of lists of possible times before covariance changes.
    :state_length_name: Name of each stat
    :randomseed: set random seed

    *LIMITATIONS*

    As the parameters stand, only 2 time series can be generated (some minor modifications are needed to generate more).
    Input `var` must be integer and cannot vary between the time series.

    *RETURNS*

    :df: pandas dataframe with timeseries_1, timeseries_2, covariance_parameter. Table is multiindexed with alpha and time as the two indexes.

    """

    # Random seed
    np.random.seed(params['randomseed'])

    # Check multiindex and get number of each multiindex
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    # Pre allocate output
    x=np.zeros([2,params['n_samples']] + mi_num)
    x = x.reshape([2,int(np.prod(x.shape)/2)])

    fluct_cv = np.zeros([params['n_samples']*len(mi_parameters)])
    fluct_cv_state= np.zeros([params['n_samples']*len(mi_parameters)])

    # Set preliminary arguments
    for sim_it, mi_params in enumerate(mi_parameters):

        d = dict(params)
        for i in range(0,len(mi)):
            d[mi[i]] = mi_params[i]



        # extend mu through timeseries if it is (list of) integers
        d['mu']=np.array(d['mu'],ndmin=2)
        if d['mu'].shape[-1]!=d['n_samples']:
            d['mu']=np.tile(d['mu'].transpose(),d['n_samples'])

        covar_mu=np.array([])
        while len(covar_mu)<d['n_samples']:
            new_covariance = np.random.permutation(d['covar_range'])[0]
            covariance_length = np.random.permutation(d['state_length'])[0]
            covar_mu = np.hstack([covar_mu,np.tile(new_covariance,covariance_length)])

        covar_mu=covar_mu[:d['n_samples']]
        fluct_cv_state[(d['n_samples']*sim_it):(d['n_samples']*(sim_it+1))]=covar_mu
        for t in range(0,d['n_samples']):
            covar = np.random.normal(covar_mu[t],d['covar_sigma'])
            x[:,(d['n_samples']*sim_it)+t]=np.random.multivariate_normal(d['mu'][:,t],[[d['var'],covar],[covar,d['var']]],1)
            fluct_cv[(d['n_samples']*sim_it)+t]=covar

    # Reshape for pandas dataframe
    x=np.reshape(x,[x.shape[0],np.prod(x.shape[1:])],order='F')
    fluct_cv=np.reshape(fluct_cv,[np.prod(fluct_cv.shape)],order='F')
    fluct_cv_state=np.reshape(fluct_cv_state,[np.prod(fluct_cv_state.shape)],order='F')
    multi_ind = pd.MultiIndex.from_product((mi_param_list + [np.arange(0,d['n_samples'])]), names=mi + ['time'])
    df = pd.DataFrame(data={'timeseries_1': x[0,:],'timeseries_2':x[1,:],'covariance_parameter':fluct_cv,'covariance_mean':fluct_cv_state}, index=multi_ind)

    return df


def gen_data(simparams):
    """
    gen_data calls gen_data_sim1, gen_data_sim2, gen_data_sim3, or gen_data_sim4 given a dictionary of parameter inputs.
    See documentation add ...add link here... to get the documentation of correct dicitonary structure.
    """


    simulations={'sim-1':tvc_benchmarker.gen_data_sim1,'sim-2':tvc_benchmarker.gen_data_sim2,'sim-3':tvc_benchmarker.gen_data_sim3,'sim-4':tvc_benchmarker.gen_data_sim4}
    df = simulations[simparams['name']](simparams['params'],mi=simparams['multi_index'])
    return df
