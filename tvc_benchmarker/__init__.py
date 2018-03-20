# #!/usr/bin/env python3
#
"""tvc_benchmarker is a package that compares different dynamic functoinal connectivity methods against eachother."""
#
__author__ = "William Hedley Thompson (wiheto)"
__version__ = "0.1" #Peer reviewed version becomes version 1.0
#
from tvc_benchmarker.get_data import gen_data_sim1,gen_data_sim2,gen_data_sim3,gen_data_sim4, load_data, gen_data
from tvc_benchmarker.dfc_calc import dfc_calc
from tvc_benchmarker.dfc_evaluate import bayes_model,save_bayes_model,load_bayes_model,calc_waic, model_dfc, trace_plot
from tvc_benchmarker.misc import check_params,standerdize, square_axis, autocorr, panel_letters, get_discrete_colormap, multiindex_preproc, load_params
from tvc_benchmarker.plot import plot_betadfc_distribution, plot_fluctuating_covariance, plot_method_correlation, plot_dfc_timeseries,plot_timeseries
from tvc_benchmarker.add_method import calc_new_method
from tvc_benchmarker.run import run_simulations
from tvc_benchmarker.send_method import send_method
import __main__
