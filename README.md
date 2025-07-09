# MG Emulators

Emulated nonlinear power spectrum boosts for various MG and DE theories
for fast weak lensing analysis. All emulators are based on the [Cosmopower](https://github.com/alessiospuriomancini/cosmopower) platform. 

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

If you use ``MGEmu`` at any point in your work please cite the relevant papers 

``` 
@article{SpurioMancini:2021ppk,
    author = "Spurio Mancini, Alessio and Piras, Davide and Alsing, Justin and Joachimi, Benjamin and Hobson, Michael P.",
    title = "{CosmoPower: emulating cosmological power spectra for accelerated Bayesian inference from next-generation surveys}",
    eprint = "2106.03846",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.CO",
    doi = "10.1093/mnras/stac064",
    journal = "Mon. Not. Roy. Astron. Soc.",
    volume = "511",
    number = "2",
    pages = "1771--1788",
    year = "2022"
}

@article{Cataneo:2018cic,
    author = "Cataneo, Matteo and Lombriser, Lucas and Heymans, Catherine and Mead, Alexander and Barreira, Alexandre and Bose, Sownak and Li, Baojiu",
    title = "{On the road to percent accuracy: non-linear reaction of the matter power spectrum to dark energy and modified gravity}",
    eprint = "1812.05594",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.CO",
    doi = "10.1093/mnras/stz1836",
    journal = "Mon. Not. Roy. Astron. Soc.",
    volume = "488",
    number = "2",
    pages = "2121--2142",
    year = "2019"
}

```


## License
[MIT](https://choosealicense.com/licenses/mit/)
