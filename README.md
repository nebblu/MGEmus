p# MG Emulators

Emulated nonlinear power spectrum boosts for various MG and DE theories
for fast weak lensing analysis.

## Installation

To install it, just clone the repository, go to the folder and do

```bash
pip install . [--user]
```

## Requirements
Required python packages:
* numpy
* scipy

For tutorials:
* matplotlib
* emcee
* getdist

## Usage

```python
import MGEmu as mgemu


params = {
    'Omega_m'     :  [0.315],
    'As'            :  [np.exp(3.07)*1.e-10],
    'Omega_b'  :  [0.05],
    'ns'            :  [0.96],
    'H0'        :  [0.67],
    'Omega_nu' :  [0.0], 
    'fR0'  :  [0.0],
    'z'             :  [0.]}


emulator = mgemu.MG_boost(model='fr') #can select between fr, dgp, gamma - make sure parameters are appropriate! 

k_values, boost = emulator.get_boost(**params)
```


## Parameter ranges

See the [ReACTemus](https://github.com/nebblu/ReACT-emus/tree/main) for example for the various parameter ranges.

## Citation

If you use ``MGEmu`` at any point in your work please cite the relevant papers.

## License
[MIT](https://choosealicense.com/licenses/mit/)
