import scipy.stats as sps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json
import os
import tvc_benchmarker
import itertools


def standerdize(x):
    return (x-x.mean())/(x.std())


def square_axis(ax):
    """
    Makes axis square.

    **Input**

    :ax: axis object
    """
    x0,x1 = ax.get_xlim()
    y0,y1 = ax.get_ylim()
    ax.set_aspect((x1-x0)/(y1-y0))

def autocorr(x,lags=10):
    xr = np.zeros(lags+1)
    xr[0] = sps.pearsonr(x,x)[0]
    xr[1:lags+1] = [sps.pearsonr(x[l:],x[:-l])[0] for l in range(1,lags+1)]
    return xr


def panel_letters(ax,xshift=0,yshift=1):
    """
    Makes axis square.

    **Input**

    :ax: axis object
    """
    letters=list(map(chr, range(65, 65+len(ax))))
    if isinstance(xshift,int) or isinstance(xshift,float):
        xshift=np.array([xshift])
    if isinstance(yshift,int) or isinstance(yshift,float):
        yshift=np.array([yshift])
    if len(xshift)==1 and len(ax)>1:
        xshift = np.tile(xshift,len(ax))
    if len(yshift)==1 and len(ax)>1:
        yshift = np.tile(yshift,len(ax))
    for i, l in enumerate(letters):
        ax[i].text(xshift[i], yshift[i], l, transform=ax[i].transAxes,
        fontsize=12, va='top', ha='right')
    return ax


def get_discrete_colormap(cmap):

    gen_cmap = plt.cm.get_cmap(cmap)
    cmapN={ 'Accent': 	8,'Dark2': 	8,'Paired': 	12,'Pastel1': 	9,'Pastel2': 	8,'Set1': 	9,'Set2': 	8,'Set3': 	12}
    return mcolors.LinearSegmentedColormap.from_list(gen_cmap.name, gen_cmap(np.linspace(0, 1, cmapN[cmap])), cmapN[cmap])


def check_params(param_dict,head='dfc'):
    """
    param dictionary

    head = 'dfc' or 'simulation'

    """

    # TODO: add more controls for valid simulation
    # TODO: add more controls for valid stats parameter head

    # Make the parameter dictionary start params['dfc'][0], followed by params['dfc'][1] (and so on) if there are multiple dfc methods to run
    if head in param_dict:
        new_param_dict = param_dict
    elif '0' in param_dict or 0 in param_dict:
        new_param_dict = {}
        new_param_dict[head] = param_dict
    elif 'name' in param_dict:
        new_param_dict = {}
        new_param_dict[head] = {}
        new_param_dict[head][0] = param_dict
    else:
        raise ValueError('Cannot understand parameter structure. See documentation')

    # Convert stringed-integers to integers
    if '0' in new_param_dict[head]:
        new_param_dict[head] = {int(key):val for key,val in new_param_dict[head].items()}

    # Check that all method instances have name, method and params
    if head == 'dfc':
        for i in new_param_dict[head]:
            if 'name' not in new_param_dict[head][i]:
                raise ValueError('name field missing from method: ' + str(i))
            if 'method' not in new_param_dict[head][i]:
                raise ValueError('method field missing from method: ' + new_param_dict[head][i]['name'])
            if 'params' not in new_param_dict[head][i]:
                print('WARNING: params field missing from method: ' + new_param_dict[head][i]['name'] + '. Assuming no parameters are needed.')
                new_param_dict[head][i]['params'] = {}

    return new_param_dict

def multiindex_preproc(params,mi):

    # Make mi a list
    if isinstance(mi,str):
        mi = [mi]
    elif not mi:
        mi = []
    # Sort list to make mi in alphabetical order
    mi = sorted(mi)

    mi_num = []
    # Get number of arguments in each multi index
    for i in mi:
        mi_num.append(len(params[i]))

    # Number of different configurations that need to be made
    mi_parameters = list(itertools.product(*[params[i] for i in mi]))

    # This could probabaly be make better. But it takes any list input and makes it tuples for index
    mi_param_list = [params[i] for i in mi]
    for i, ind in enumerate(mi_param_list):
        for j, e in enumerate(ind):
            if isinstance(e,list):
                mi_param_list[i][j] = tuple(e)


    return mi,mi_num,mi_parameters,mi_param_list


def load_params(in_str):

    if os.path.isfile(tvc_benchmarker.__path__[0] + '/data/routine_params/' + str(in_str) + '.json'):
        params_path = tvc_benchmarker.__path__[0] + '/data/routine_params/' + str(in_str) + '.json'
    elif os.path.isfile(str(in_str)):
        params_path = str(in_str)
    else:
        raise ValueError('Cannot find routine parameter file')
    with open(params_path) as f:
        params = json.load(f)
    f.close()
    params = tvc_benchmarker.check_params(params,'simulation')
    params = tvc_benchmarker.check_params(params,'dfc')
    return params
