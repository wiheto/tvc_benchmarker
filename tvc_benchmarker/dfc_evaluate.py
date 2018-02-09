import pymc3 as pm
import pickle
import tvc_benchmarker
import numpy as np
import tabulate
import matplotlib.pyplot as plt

def model_dfc(x,dfc,dat_dir,model_prefix,bayes_model='bayes_model',mi='alpha',model_params={}):
    """
    General stats functions that calls the bayes_model, saves the output.

    **Input**

    :x: raw time series (DF)
    :dfc: dynamic connectivity estimates (DF)
    :dat_dir: Place to save the stats data.
    :model_predix: Prefix name for saved file
    :model_params: string of parameters for bayes_model function
    """
    if model_params == None:
        model_params = ''

    if isinstance(mi,str):
        mi = [mi]

    params = {}
    for m in mi:
        params[m] = np.unique(dfc.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    for sim_it, mi_params in enumerate(mi_parameters):
        for method in dfc.columns:
            plt.close('all')
            X=dfc[method][mi_params]
            Y=x['covariance_parameter'][mi_params][X.index]
            trace_and_model = tvc_benchmarker.bayes_model(X,Y,**model_params)
            #Save data
            param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
            param_sname = '_'.join(param_sname)
            param_sname = '_' + param_sname.replace(' ','')
            file_name = model_prefix + '_' + 'method-' + method + param_sname
            tvc_benchmarker.trace_plot(dat_dir,file_name,trace_and_model[0])
            tvc_benchmarker.save_bayes_model(dat_dir,file_name,trace_and_model)


def trace_plot(dat_dir,file_name,trace):

    fig,ax = plt.subplots(3,2)
    pm.traceplot(trace,ax=ax)
    fig.savefig(dat_dir + '/' +  file_name + '_traceplot.png',r=300)

def bayes_model(x,y,samples=6000,alpha_mu=0,beta_mu=0,alpha_sd=1,beta_sd=1,sigma_sd=1,n_init=200000):
    """
    Simple linear Bayes regression through pymc3.

    **Input**

    :x: x in: y=bx+a
    :y: y in: y=bx+a
    :samples: number of samples
    :alha_mu: prior: mean of intercept
    :beta_mu: prior: mean of beta
    :alpha_sd: prior: sd of intercept
    :beta_sd: prior: sd of beta
    :sigma_sd: prior: sd of likelihood.
    :n_init: ADVI iterations at initizaliation


    **Output**

    :model,trace: model object and trace object of pyMC3

    """
    model = pm.Model()
    x = tvc_benchmarker.standerdize(x)
    y = tvc_benchmarker.standerdize(y)
    with model:

        # Priors for unknown model parameters
        alpha = pm.Normal('alpha', mu=alpha_mu, sd=alpha_sd)
        beta = pm.Normal('beta', mu=beta_mu, sd=beta_sd)
        sigma = pm.HalfNormal('sigma', sd=sigma_sd)
        # Expected value of outcome
        mu = alpha + beta*x
        # Likelihood (sampling distribution) of observations
        Y_obs = pm.Normal('Y_obs', mu=mu, sd=sigma, observed=y)
        trace = pm.sample(samples,n_init=n_init)

    return trace,model




def calc_waic(dfc,model_dir,save_dir,file_prefix=None,mi='alpha',burn=1000):
    """
    Calculates WAIC of a bayes model, saves table


    **Input**

    :dfc: dfc dataframe
    :model_dir: where the bayesian models are saved
    :save_dir: where to save the tables
    :file_prefix: appended model name
    :mi: Loop over multiple models of this multiindex
    :burn: how many from start of trace to discard.

    **Returns**

    :waic: (numpy array)
    """
    if file_prefix:
        file_prefix += '_'

    if isinstance(mi,str):
        mi = [mi]

    params = {}
    for m in mi:
        params[m] = np.unique(dfc.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        param_sname = '_' + param_sname.replace(' ','')

        waic = np.zeros([len(dfc.columns),3])
        for i,method in enumerate(dfc.columns):
            file_name = file_prefix + 'method-' + method + param_sname
            tm=tvc_benchmarker.load_bayes_model(model_dir,file_name)
            waic[i,:] = np.array(pm.stats.waic(tm[0][burn:],tm[1]))

        odr=np.argsort(waic[:,0])
        delta_waic = waic[:,0]-waic[odr[0],0]

        #Create table for tabulate
        tablelst=[["Model","WAIC","WAIC SE","$\Delta$ WAIC"]]
        for i in odr:
            tablelst.append([dfc.columns[i],waic[i,0],waic[i,1],delta_waic[i]])
        #Make markdown table and save
        mdtable = tabulate.tabulate(tablelst,headers="firstrow",tablefmt='simple')
        with open(save_dir + '/' + file_prefix + 'waictable' + param_sname + '.md','w') as f:
            f.write(mdtable)
        f.close()
        print(mdtable)

    return waic


def save_bayes_model(path,file_name,tm):

    """
    Saves output from model_dfc


    **Input**

    :Path: path to save.
    :Filename: filename
    :tm: model and trace (output of model_dfc)

    **Returns**
    None
    """

    if file_name.endswith('.pkl') == False:
        file_name += '.pkl'
    with open(path + '/' + file_name, 'wb') as h:
        pickle.dump(tm,h)
    h.close()

def load_bayes_model(path,file_name):

    """
    loads saved output from model_dfc


    **Input**

    :Path: path to save.
    :Filename: filename

    **Returns**

    :tm: model and trace (output of model_dfc)
    """

    if file_name.endswith('.pkl') == False:
        file_name += '.pkl'
    with open(path + '/' + file_name, 'rb') as h:
        tm=pickle.load(h)
    h.close()

    return tm
