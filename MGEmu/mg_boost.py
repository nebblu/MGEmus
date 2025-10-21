from scipy import interpolate
import numpy as np
import copy
import os
import cosmopower as cp
from cosmopower import cosmopower_NN
__all__ = ["MG_boost"]

version = "_v3"
class MG_boost(object):
    """
    A class to load and call the MG emulator for the nonlinear power spectrum boost.

    :param verbose: whether to activate the verbose mode, defaults to True
    :type verbose: boolean, optional

    """

    def __init__(self, verbose=True, model='fr'):

        self.verbose = verbose
        self.model = model

        self.emulator = {}

        self.emulator['nonlinear'] = load_nonlinear_emu(verbose=verbose,model=model)

    def _get_parameters(self, coordinates):
        """
        Function that returns a dictionary of cosmological and beyond-LCDM parameters
        and checking the relevant boundaries.
        :param coordinates: a set of coordinates in parameter space
        :type coordinates: dict
        :param which_model: kind of gravity/dark energy model: options are 'fr', 'dgp', 'gamma'
        :type which_emu: str
        :return: coordinates with derived parameters
        :rtype: dict
        """
        coordinates = {key: np.atleast_1d(coordinates[key]) for key in
                       set(list(coordinates.keys()))
                       - set(['k'])}
        # parameters currently available
        avail_pars = [coo for coo in coordinates.keys() if coordinates[coo][0]
                      is not None]
        # parameters strictly needed to evaluate the emulator
        eva_pars = self.emulator['nonlinear']['keys']
        # parameters needed for a computation
        comp_pars = list(set(eva_pars)-set(avail_pars))
        miss_pars = list(set(comp_pars))

        if miss_pars:
            print(f"  Please add the parameter(s) {miss_pars}"
                  f" to your coordinates!")
            raise KeyError(f"emulator: coordinates need the"
                           f" following parameters: ", miss_pars)

        
        pp = [coordinates[p] for p in eva_pars]

        # for i, par in enumerate(eva_pars):
        #     val = pp[i]
        #     message = 'Param {}={} out of bounds [{}, {}]'.format(
        #         par, val, self.emulator['bounds'][par][0],
        #         self.emulator['bounds'][par][1])
        #     assert (np.all(val >= self.emulator['bounds'][par][0])
        #             & np.all(val <= self.emulator['bounds'][par][1])
        #             ), message
        pp_dict = {key: np.atleast_1d(coordinates[key]) for key in
                       eva_pars}    

        return pp_dict
    
    
    def _evaluate_nonlinear(self, **kwargs):
        """Evaluate the given emulator at a set of coordinates in parameter \
            space.

        The coordinates in arrays must be specified as a dictionary with the following
        keywords:

        #. 'Omega_m'
        #. 'Omega_b'
        #. 'H0'
        #. 'ns'
        #. 'Omega_nu'
        #. 'As'
        #. 'extra parameters'
        #. 'z'
        #. 'k' : a vector of wavemodes in h/Mpc at which the nonlinear boost
                 will be computed, if None the default wavemodes of the
                 nonlinear emulator will be used, defaults to None
        """
        k = kwargs['k'] if 'k' in kwargs.keys() else None
        emulator = self.emulator['nonlinear']
        pp = self._get_parameters(kwargs)
        model = 'model_tot'
        boost_nonlin = emulator[model].predictions_np(pp)
        zbins = len(pp['z'])
        if k is not None:
            if (max(k) > max(emulator['k'])) | (min(k) < min(emulator['k'])):
                raise ValueError(f"""
                    A minimum k > {min(emulator['k'])} h/Mpc and a
                    maximum k < {max(emulator['k'])} h/Mpc
                    are required for the nonlinear emulator:
                    the current values are {min(k)} h/Mpc and {max(k)} h/Mpc
                    """)
            else:
                boost_interp = [interpolate.interp1d(emulator['k'],
                                                    boost_nonlin_i,
                                                    kind='linear'
                                                    ) for boost_nonlin_i in boost_nonlin]
                boost_nonlin = np.array([boost_interp[i](k) for i in range(zbins)])
        else:
            k = emulator['k']

        return k, boost_nonlin
    
    
    def get_nonlinear_boost(self, Omega_m=None, 
                         Omega_b=None,
                         H0=None, ns=None, Omega_nu=None, As=None,
                         fR0=None, omegarc=None, gamma=None,
                         mu0=None, lam=None, c2=None, 
                         q1=None, q2=None, q3=None,
                         w0=None, wa=None, xi=None,
                         z=None, k=None, 
                         **kwargs):
        """Compute the prediction of the nonlinear power spectrum boost.
        :param k: a vector of wavemodes in h/Mpc at which the nonlinear boost
                  will be computed, if None the default wavemodes of the
                  emulator will be used, defaults to None
        :type k: array_like, optional
        :return: k and the nonlinear boost
        :rtype: tuple
        """
        _kwargs = locals()
        kwargs = {key: _kwargs[key]
                  for key in set(list(_kwargs.keys())) - set(['self'])}

        k, boost_nl = self._evaluate_nonlinear(**kwargs)

        return k, boost_nl



def load_nonlinear_emu(verbose=True, model='fr'):
    """Loads in memory the nonlinear boost emulator computed with  
    ReACT and trained with cosmopower.
    
     Defaults to f(R) emulator

    :return: a dictionary containing the emulator object
    :rtype: dict
    """

    if verbose:
        print('Loading nonlinear emulator...')

    basefold = os.path.dirname(os.path.abspath(__file__))    
    emulator_tot_name = (basefold+"/models"+version+"/"+model)
    emulator = {}
    emulator['model_tot'] = cosmopower_NN(restore=True, 
                      restore_filename=emulator_tot_name,
                      )
    emulator['k'] = emulator['model_tot'].modes
    emulator['keys'] = emulator['model_tot'].parameters
    if verbose:
        print('Nonlinear emulator loaded in memory.')

    return emulator    

