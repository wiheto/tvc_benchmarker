import numpy as np
import tvc_benchmarker

def calc_new_method(x,new_method,params_new_method=None,mi='alpha'):


    if params_new_method['name'] == None:
        params_new_method['name'] = new_method.__name__

    mi = list(x.index.names)
    if len(x.index.names)>1:
        mi.remove('time')
    elif len(x.index.names) == 1 and x.index.names == [None]:
        x.index.names = ['time']
    if x.index.names == ['time']:
        mi = []

    params = {}
    for m in mi:
        params[m] = np.unique(x.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)


    dfc_estimate=[]

    for sim_it, mi_params in enumerate(mi_parameters):

        if mi_params == ():
            mi_params = np.arange(0,len(x))

        time_points = int(len(x.index.get_level_values('time'))/len(mi_parameters))

        tmp=np.array(new_method(np.array([x['timeseries_1'][mi_params],x['timeseries_2'][mi_params]]),**params_new_method['params']))
        # Fix the output in case it is no node,node,time (for full entire timeseries)
        if len(tmp)!=time_points:
            window=int((time_points-len(tmp))/2)
            tmp=np.lib.pad(tmp,window,mode='constant',constant_values=np.nan)
        if len(tmp)==time_points-1:
            tmp=np.hstack([np.nan,tmp])
        if len(tmp.shape)==3:
            connectivity = tmp[0,1,:]
        else:
            connectivity = tmp

        dfc_estimate.append(connectivity)


    dfc_estimate = np.concatenate(dfc_estimate)

    return dfc_estimate
