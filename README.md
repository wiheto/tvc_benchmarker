# tvc_benchmarker

Simulations for testing covariance tracking. Accompanies the article by Thompson et al (2018) [A simulation and comparison of time-varying functional connectivity methods](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006196)

Have any ideas for improvements to the next version of tvc_benchmarker? [Please leave a comment here](https://github.com/wiheto/tvc_benchmarker/issues/1)

## Contents

- Install tvc_benchmarker

- What you can do with tvc_benchmarker

- What you cannot do with tvc_benchmarker

- Run all simulations with default parameters

- Add new method

- Send the method

- Custom parameter dictionary

## Install

tvc_benchmarker is written in Python 3. So a python version > 3.5 is needed.  

You can install tvc_benchmarker through [pip](http://www.pythonforbeginners.com/basics/how-to-use-pip-and-pypi/) and [conda](https://conda.io/docs/), simply type:

```bash
conda install theano pygpu
pip install tvc_benchmarker
```

This should install all the requirements. If you do not want to use conda, see the Theano documentation below to install without conda. 

It is however possible that some errors will occur due to theano failing to install. To check if theano has been installed correctly you can either (1) Test if it has been successfully installed with the above by typing `nosetests theano` in a terminal window (this takes around 1-2 hours to run) (2) Run `import pymc3` and see if an error is raised (quicker). Check that the error seems to relate to Theano. If an error is rasied, some additional tweaks/settings may be required to successfully get thaeno running but it is unlikely noone will have had that error before and you will find the solution on stackoverflow. ([see Theano installation instructions](http://theano.readthedocs.io/en/latest/install.html) for more details). 

If any warning are raised when importing tvc_benchmarker (e.g. futurewarnings or failed to import the duecredit module) and tvc_benchmarker still imports successfully, these warnings can be ignored. 

There is also a docker container that can be built in ./Dockerfile/ (see README there for more details). When running the docker image, it reruns the entire code within the docker image. (Flags for adding new methods within the Docker file are planned but not currently present).  

## What you can do with tvc_benchmarker

- Rerun the entire code that is included in the paper.
- Add new methods that get benchmarked in the same way as the other methods.
- Send the new method within tvc_benchmarker so it gets added in future reports.
- Change the parameters of different simulations. Multiple parameters can be specified for (nearly) all parameters.

## What you cannot do with tvc_benchmarker

- Make new simulation scenarios within tvc_benchmarker  (i.e. the structure of the 4 simulations cannot be changed, just the parameters within each simulation)
- Test methods that rely on frequency-specific properties (e.g. phase correlations).

## Run all simulations with default parameters

To run all simulations, used `tvc_benchmarker.run_simulations()`

```python
import tvc_benchmarker
tvc_benchmarker.run_simulations()
```

The default will take the latest simulation routine and it uses the precalculated data included with the package (both simulations and DFC estimates). The statistics gets recalculated each time (this may be included in a later version).

If you want to calculate everything from the start.

```python
tvc_benchmarker.run_simulations(usesaved=False)
```

Alternatively the above can be done from the commandline:

```bash 
python -m tvc_benchmarker 
```

When there are additional routines (e.g. additional simulations) you can specify the version number to specify which version you want to run:

```python
tvc_benchmarker.run_simulations(routine_version=1.0,usesaved=False)
```

The default will be the latest simulation routine.

`rountine_version` can also be a path to a json file that contains a custom parameter file (see below).

```python
tvc_benchmarker.run_simulations(routine_version='./my/simulation/parameter.json',usesaved=False)
```

Note: DFC estimates are calculated with teneto (Requirement says v0.2.1). At the moment (although it shouldn't) it writes a ./report file which contains a html report of DFC derivation (and overwrites this for each method) --- This directory can be ignored. Teneto v0.2.2 and above will fix this.

## Add new method

tvc_benchmarker tests 5 different methods.

Let us say that, for some reason a think $(x_1 + x_2)^3$ is a good estimate for the relationship between $x_1$ and $x_2$. This will be the method we benchmark against everything else.

```python
import numpy as np
def add_then_power(x,power):
  return np.power(x[0,:]+x[1,:],power)
```

A parameter dictionary is also needed. This dictionary contains a `params` dictionary (containing arguments for the method function above, excluding the x), a name and a method name. The specified `name` will be used in figures and  tables.

Here is an example:  

```python
params = {
      'name': 'AP-3',
      'method': 'add_then_power',
      'params': {
        'power': 3
      }
    }
```

Multiple parameter configurations of new method can be easily added (see *Custom parameter dictionary*).

Then to run the new method, simply run:

```
tvc_benchmarker.run_simulations('1.0',output_dir='./with_new_method/',new_method=my_new_method,params_new_method=params)
```

The figures exported into "./with_new_method" will include both the bundled methods and newly specified method. This means that this new method can be compared to the 5 original methods in tvc_benchmarker.

## Send method

Once a method has been tested, it is good for it to be shared with others.

```
tvc_benchmarker.send_method(method_code=add_then_power,param_code=params)
```

Where `add_then_power` and `params` are defined in the previous section.

There are then a couple of questions that you will then be prompted with when running this function, such as email address, name, DOIs/pmids of relevant publications which should be cited when reporting the method etc.  Then there are a number of questions to approve (e.g. everything is sent via a Google form). If you do not want to approve of things going via Google, you can just send it to me over Github/email (see article). You also have to approve that tvc_benchmarker can use the code in future version. You can also decide if you will also allow for your code to be included in [teneto](github.com/wiheto/teneto) (which is my python package for temporal network/dynamic connectivity --- not all code will necessary be chosen to be included in teneto).  

Once I've looked at the code, I will send you an email and confirm it works. If I've not sent an email after 1-2 weeks, please let me know (just in case something may break with the Google form method).

## Custom parameter dictionary

The parameters for each simulation are driven by a parameter dictionary.

### Parameter dictionary for a single simulation.

To do this there are two ways. Either using `gen_data` or using the simulation specific functions (`gen_data_sim1()`, `gen_data_sim2()`, `gen_data_sim3()`, `gen_data_sim4()`).

Say we want to generate data from simulation 2, we can do the following.

```python
sim_2_params = {
    "covar_mu": 0.2,
    "var": 1,
    "n_samples": 1000,
    "mu": [0, 0],
    "alpha": 0.2,
    "covar_sigma": 0.1,
    "randomseed": 2017
}
```

The entire pipeline can be grouped together.

`sim2_data = tvc_benchmarker.gen_data_sim2(sim_2_params,mi=None)`

The `mi`parameter is for which parameters should be looped over (see below).  

This type of parameter dictionary works with `gen_data_sim1()`, `gen_data_sim2()`, `gen_data_sim3()`, `gen_data_sim4()` --- see each function's documentation for their respective parameters needed.

There is a higher level way to generate data using the function `gen_data()`. Using this function the above simulation specific. This allows for the mi property to be included in the parameter file. This dictionary must include three items, `name` (a string), `multi_index` (a list), and

```python
gen_sim_2_params = {
    'name': 'sim-2',
    'multi_index': [],
    'params': sim_2_params
}
```

Where `sim_2_params` is equal to the dictionary already defined above. Then to run this, `tvc_benchmarker.gen_data` can be run.  

`sim2_data = tvc_benchmarker.gen_data(gen_data_params)`

### Parameter dictionary for multiple simulations.

`tvc_benchmarker.run_simulations()` runs the entire simulation procedure: generates data, calculates the DFC and performs the statistics, and plots the output. Calling the function as is, or with an integer, uses a predefined parameter dictionary, but you can make one yourself.

Here we pass a dictionary like for a single simulation, but now contains additional levels in the dictionary.

The highest level of the parameter dictionary must include the following three items:

```python
pipeline_params = {
    'simulation':{},
    'dfc':{},
    'stats':{}
}
```

The next level of the `simulation` and ` dfc` dictionaries state the simulation or method. Start at 0 and work your way up.

Let us say we want to perform only a single simulation this way, and a single DFC method.

```python
pipeline_params = {
    'simulation':{0:{}},
    'dfc':{0:{}},
    'stats': {}
}
```

If we wanted to add multiple 3 simulations and 3 methods, simply type:

```python
pipeline_params_3 = {
    'simulation':{0:{},1:{},2:{}},
    'dfc':{0:{},1:{},2:{}},
    'stats': {}
}
```

Each simulation index can be defined as previous for single simulations:

```python
pipeline_params['simulation'][0] = gen_sim_2_params
```

In the `dfc` dictionary this consists of three items:

```python
pipeline_params['dfc'][0] = {
    'name': ''
    'method': ''
    'params': {}
}
```

The `method` is either; 'SW', 'TSW', 'TD', 'JC', or 'SD' (See section on adding a new method below, if you want to add a new method).

The `name` can whatever you want (used in plotting and table creation). So let us say you have a sliding window with window size 20, and another 120, you may want the names to be 'SW-20' and 'SW-120'.

The 'params' are the parameters required for each method. See documentation of tvc_benchmarker.dfc_calc. An example of the `dfc` dictionary can then be:

```python
pipeline_params['dfc'][0] = {
    'name': 'SD',
    'method': 'SD',
    'params': {
        'sd_distance': 'euclidean'
    }
}
```

The final pipeline dictionary alongside the `simulation` and `dfc` dictionaries is the `stats` dictionary. Here you can specify of how many samples should be generated from the MCMC (to be included in the posterior + the number discarded). Burn is the number discarded.

```python
pipeline_params['stats'] = {
    "burn": 500,
    "trace": {"samples": 5500}
}
```

These numbers can be changed if the MCMC chains are not converging (see trace plots that are generated in the stats folder). There may be some additional parameters implemented in the future if, for example, different distributions of the DFC estimates are used in the stats model.

This can then be run with `dfc.run_simulations()`

```python
tvc_benchmarker.run_simulations(pipeline_params,usesaved=False,output_dir='my_pipeline')
```

Here we also specify which directory the output should be (this is good to do when not using a default routine version.)

Lets put it all together. Here we will define 2 simulations and 3 DFC methods in one dictionary at once:

```python
pipeline_params_3 = {
    'simulation':{
        0:{
            'name': 'sim-1',
            'multi_index': ['alpha'],
            'params': {
                "mu": [0,0],
                "sigma": [[1,0.5],[0.5,1]],
                "n_samples": 10000,
                "alpha": [0.2,0.8],
                "randomseed": 2017  
            }
        },
        1:{
            'name': 'sim-2',
            'multi_index': ['alpha'],
            'params': {
                "covar_mu": 0.2,
                "var": 1,
                "n_samples": 10000,
                "mu": [0,0],
                "alpha": [0.2,0.8],
                "covar_sigma": 0.1,
                "randomseed": 2017        
            }
        },
    },
    'dfc':{
        0:{
            'name': 'SW-25',
            'method': 'SW',
            'params': {
                'sw_window': 25
    }
        },
        1:{    
            'name': 'SW-125',
            'method': 'SW',
            'params': {
                'sw_window': 125
    }},
        2:{
            'name': 'JC',
            'method': 'JC',
            'params': {}
        }
    },
    'stats':{
        "burn": 500,
        "trace": {
            "samples": 5500}
    }
}
```

The above can also be saved as a json.

What the above code will do is generate data for 2 simulations (sim 1 and sim 2 both loop over the parameter `alpha`) and uses 3 DFC methods (SW with 20 window size, SW with 120 as window size and Jackknife correlation).

To run the simulations with the above parameters run:

`tvc_benchmarker.run_simulations(pipeline_params, usesaved=False, output_dir='test-simulations')`

Should run both these simulations, perform the statistics and create plots for each simulation in ./test-simulations/

## Problems/comments/something unclear?

Leave an issue here.

_Note: V1 of the older named "dfcbenchmarker" does not equal V1 of tvc_benchmarker.


## Changes since article release

- Updated requirements to pymc3 3.4.1.
- Fixed a bug when loading stats results from pymc 3.4.1 and onward. Removes burn from calc_waic.   
