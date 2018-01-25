import matplotlib.pyplot as plt
import tvc_benchmarker
import numpy as np
import scipy.stats as sps
from matplotlib.ticker import LinearLocator
import seaborn as sns
import os
plt.style.use('seaborn-whitegrid')



def plot_timeseries(x,plot_autocorr='no',fig_dir=None,fig_prefix=None,cm='Set2',limitaxis=100,mi='alpha'):


    if isinstance(mi,str):
        mi = [mi]

    if fig_prefix:
        fig_prefix += '_'
    else:
        fig_prefix = ''

    if not fig_dir:
        fig_dir = './'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir,exist_ok=True)

    params = {}
    for m in mi:
        params[m] = np.unique(x.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    colormap=tvc_benchmarker.get_discrete_colormap(cm)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        if param_sname:
            param_sname = '_' + param_sname.replace(' ','')

        param_title = [p[0] + '=' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_title = ','.join(param_title)
        param_title = param_title.replace(' ','').replace(',',', ')

        if mi_params == ():
            mi_params = np.arange(0,len(x))

        if plot_autocorr == 'no':

            fig,ax=plt.subplots(1)
            ax.plot(np.arange(1,limitaxis+1),x['timeseries_1'][mi_params][:limitaxis],color=colormap(0),alpha=0.9,linewidth=2)
            ax.plot(np.arange(1,limitaxis+1),x['timeseries_2'][mi_params][:limitaxis],color=colormap(1),alpha=0.9,linewidth=2)
            ax.set_xlim(1,limitaxis)
            ax.set_ylabel('Signal Amplitude')
            ax.set_xlabel('Time')

        else:

            autocorrelation = np.array([tvc_benchmarker.autocorr(x[ts][mi_params]) for ts in ['timeseries_1','timeseries_2']])

            fig=plt.figure()
            ax=[]
            ax.append(plt.subplot2grid((2,3),(0,0),colspan=3))
            for n in range(0,3):
                ax.append(plt.subplot2grid((2,3),(1,n)))

            # Plot 1: raw time series
            ax[0].plot(np.arange(1,limitaxis+1),x['timeseries_1'][mi_params][:limitaxis],color=colormap(0),alpha=0.9,linewidth=2)
            ax[0].plot(np.arange(1,limitaxis+1),x['timeseries_2'][mi_params][:limitaxis],color=colormap(1),alpha=.9,linewidth=2)
            ax[0].set_xlim(1,limitaxis)
            ax[0].set_ylabel('Signal Amplitude')
            ax[0].set_xlabel('Time')

            # Plot 2 and 3: autocorrelation of timeseries 1 and 2
            for p in range(1,3):
                ax[p].plot(np.arange(0,autocorrelation.shape[1]),autocorrelation[p-1,:],color=colormap(p-1),alpha=0.9,linewidth=2)
                ax[p].set_ylabel('Correlation (r)')
                ax[p].set_xlabel('Lag')
                ax[p].axis([0,autocorrelation.shape[1]-1,0,1])
                ax[p].set_yticks(np.arange(0,1.05,0.25))
                ax[p].set_xticks(np.arange(0,autocorrelation.shape[1],2))

            # Plot 4: correlation of timeseries 1 and 2
            cmap = sns.cubehelix_palette(start=1/3, light=1, as_cmap=True)
            ax[3] = sns.kdeplot(x['timeseries_1'][mi_params], x['timeseries_2'][mi_params], shade=True,cmap=cmap)
            ax[3].set_xlabel('Signal 1 amplitude')
            ax[3].set_ylabel('Signal 2 amplitude')

            [tvc_benchmarker.square_axis(ax[n]) for n in [1,2,3]]

        plt.suptitle(param_title,fontsize=11)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(fig_dir + '/' + fig_prefix + 'raw-timeseries' + param_sname + '.pdf',r=600)

    plt.close('all')

def plot_method_correlation(dfc, cmap='RdBu_r', fig_dir=None, fig_prefix=None, mi=[]):


    if isinstance(mi,str):
        mi = [mi]

    if fig_prefix:
        fig_prefix += '_'
    else:
        fig_prefix = ''

    if not fig_dir:
        fig_dir = './'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir,exist_ok=True)

    params = {}
    for m in mi:
        params[m] = np.unique(dfc.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        if param_sname:
            param_sname = '_' + param_sname.replace(' ','')

        param_title = [p[0] + '=' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_title = ','.join(param_title)
        param_title = param_title.replace(' ','').replace(',',', ')

        if mi_params == ():
            mi_params = np.arange(0,len(dfc))

        R=np.zeros([len(dfc.columns),len(dfc.columns)])
        for i,m1 in enumerate(sorted(dfc.columns)):
            for j,m2 in enumerate(sorted(dfc.columns)):
                notnan = np.intersect1d(np.where(np.isnan(dfc[m1][mi_params])==0),np.where(np.isnan(dfc[m2][mi_params])==0))
                R[i,j]= sps.spearmanr(dfc[m1][mi_params][notnan],dfc[m2][mi_params][notnan])[0]


        fig,ax=plt.subplots(1)

        pax=ax.pcolormesh(R,vmin=-1,vmax=1,cmap=cmap)
        tvc_benchmarker.square_axis(ax)

        ax.set_xticks(np.arange(0.5,len(dfc.columns)-0.49,1))
        ax.set_xticklabels(sorted(dfc.columns))
        ax.set_yticks(np.arange(0.5,len(dfc.columns)-0.49,1))
        ax.set_yticklabels(sorted(dfc.columns))
        ax.axis([0,len(dfc.columns),len(dfc.columns),0])

        plt.suptitle(param_title,fontsize=11)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        fig.colorbar(pax)
        plt.savefig(fig_dir + '/' + fig_prefix + 'dfc-method-correlation' + param_sname + '.pdf',r=600)

    plt.close('all')



def plot_dfc_timeseries(dfc, limitaxis=500, cm='Set2', fig_dir = None, fig_prefix=None,mi=[]):

    if isinstance(mi,str):
        mi = [mi]

    if fig_prefix:
        fig_prefix += '_'
    else:
        fig_prefix = ''

    if not fig_dir:
        fig_dir = './'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir,exist_ok=True)

    params = {}
    for m in mi:
        params[m] = np.unique(dfc.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    colormap=tvc_benchmarker.get_discrete_colormap(cm)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        if param_sname:
            param_sname = '_' + param_sname.replace(' ','')

        param_title = [p[0] + '=' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_title = ','.join(param_title)
        param_title = param_title.replace(' ','').replace(',',', ')

        if mi_params == ():
            mi_params = np.arange(0,len(dfc))

        fig,ax=plt.subplots(len(dfc.columns), 1, sharex=True,figsize=(5,len(dfc.columns)*2))

        for i,dfc_method in enumerate(sorted(dfc.columns)):

            ax[i].plot(dfc[dfc_method][mi_params][:limitaxis].values,color=colormap(i),alpha=0.5,linewidth=2)
            ax[i].set_ylabel('DFC ('+ dfc_method + ')')
            ax[i].get_yaxis().set_major_locator(LinearLocator(numticks=5))
            ax[i].set_xlim(1,limitaxis)

        ax[-1].set_xlabel('time')

        plt.suptitle(param_title,fontsize=11)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        plt.savefig(fig_dir + '/' + fig_prefix + 'dfc-timeseries' + param_sname + '.pdf',r=600)

    plt.close('all')



def plot_betadfc_distribution(dfc, dat_dir, fig_dir = None, model_prefix=None, burn=1000, mi='alpha', cm='Set2'):

    if isinstance(mi,str):
        mi = [mi]

    if model_prefix:
        model_prefix += '_'

    if not fig_dir:
        fig_dir = './'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir,exist_ok=True)

    params = {}
    for m in mi:
        params[m] = np.unique(dfc.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    colormap=tvc_benchmarker.get_discrete_colormap(cm)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        if param_sname:
            param_sname = '_' + param_sname.replace(' ','')

        param_title = [p[0] + '=' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_title = ','.join(param_title)
        param_title = param_title.replace(' ','').replace(',',', ')

        if mi_params == ():
            mi_params = np.arange(0,len(dfc))

        fig,ax=plt.subplots(len(dfc.columns),sharex=True,sharey=True,figsize=(5,len(dfc.columns)))

        beta_col = []
        lines = []
        for i,method in enumerate(sorted(dfc.columns)):
            beta_dfc=tvc_benchmarker.load_bayes_model(dat_dir,model_prefix + 'method-' + method + param_sname)[0][burn:].get_values('beta')
            #Plot
            ltmp = ax[i].hist(beta_dfc,np.arange(-1,1,0.001),histtype='stepfilled',color=colormap(i),normed=True,alpha=0.4, linewidth=2,label=method)
            lines.append(ltmp)
            ax[i].set_yticklabels([])
            ax[i].set_ylabel(method)
            beta_col.append(beta_dfc)
            #ax[i].set_ylabel('Posterior Frequency (' + method + ')')

        beta_col = np.vstack(beta_col)

        xmin = beta_col.min()
        xmax = beta_col.max()
        ax[0].get_yaxis().set_major_locator(LinearLocator(numticks=4))
        ax[0].set_xlim([np.around(xmin-0.005,2),np.around(xmax+0.005,2)])

        ax[-1].set_xlabel('Posterior (' + r'$β$' + ')')

        fig.suptitle(param_title,fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        plt.savefig(fig_dir + '/' + model_prefix + 'beta-posterior' + param_sname + '.pdf',r=600)

    plt.close('all')



def plot_fluctuating_covariance(x, fig_dir = None, lags=10,limitaxis=500,cm = 'Set2',mi='alpha', fig_prefix=None):

#    if labels == None:
#        labels=np.unique(x.index.get_level_values(mi))

    if isinstance(mi,str):
        mi = [mi]

    if not fig_dir:
        fig_dir = './'

    if fig_prefix:
        fig_prefix += '_'
    else:
        fig_prefix = ''

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir,exist_ok=True)

    params = {}
    for m in mi:
        params[m] = np.unique(x.index.get_level_values(m))
    mi,mi_num,mi_parameters,mi_param_list = tvc_benchmarker.multiindex_preproc(params,mi)

    colormap=tvc_benchmarker.get_discrete_colormap(cm)

    for sim_it, mi_params in enumerate(mi_parameters):

        param_sname = [p[0] + '-' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_sname = '_'.join(param_sname)
        if param_sname:
            param_sname = '_' + param_sname.replace(' ','')

        param_title = [p[0] + '=' + str(p[1]) for p in list(zip(mi,mi_params))]
        param_title = ','.join(param_title)
        param_title = param_title.replace(' ','').replace(',',', ')

        if mi_params == ():
            mi_params = np.arange(0,len(x))

        covariance_autocorrelation = tvc_benchmarker.autocorr(x['covariance_parameter'][mi_params],lags=lags)

        # Create grid
        fig = plt.figure()
        ax = []
        ax.append(plt.subplot2grid((2,2),(0,0),colspan=2))
        ax.append(plt.subplot2grid((2,2),(1,0)))
        ax.append(plt.subplot2grid((2,2),(1,1)))

        ax[0].plot(np.arange(1,limitaxis+1),x['covariance_parameter'][mi_params][:limitaxis],color=colormap(0),alpha=0.5,linewidth=2)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel(r'Covariance ($r_t$)')

        ymin = x['covariance_parameter'][mi_params][:limitaxis].min()
        ymax = x['covariance_parameter'][mi_params][:limitaxis].max()
        ax[0].axis([1,limitaxis+1,np.around(ymin-0.05,1),np.around(ymax+0.05,1)])


        ax[1].hist(x['covariance_parameter'][mi_params],np.arange(-.1,1,0.02),color=colormap(1),alpha=0.9,linewidth=0,histtype='stepfilled',normed='true')
        ax[1].set_xlabel('Covariance')
        ax[1].set_ylabel('Frequency')
        xmin = x['covariance_parameter'][mi_params].min()
        xmax = x['covariance_parameter'][mi_params].max()
        ax[1].axis([np.around(xmin-0.05,1),np.around(xmax+0.05,1),0,np.ceil(ax[1].get_ylim()[-1])])

        tvc_benchmarker.square_axis(ax[1])

        ax[2].plot(np.arange(0,11),covariance_autocorrelation,color=colormap(2),alpha=0.9,linewidth=2)
        ax[2].set_ylabel('Correlation (r)')
        ax[2].set_xlabel('Lag')
        ymin = covariance_autocorrelation.min()
        ymax = 1
        ax[2].axis([0,10,np.around(ymin-0.05,1),np.around(ymax+0.05,1)])

        tvc_benchmarker.square_axis(ax[2])
        plt.suptitle(param_title,fontsize=11)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        plt.savefig(fig_dir + '/' + fig_prefix + 'fluctuating-covariance' + param_sname + '.pdf',r=600)

    plt.close('all')
