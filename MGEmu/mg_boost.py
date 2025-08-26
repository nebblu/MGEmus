from scipy import interpolate
import numpy as np
import copy
import os
import cosmopower as cp
from cosmopower import cosmopower_NN
__all__ = ["MG_boost"]

version = "_v2"
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
        if model=='musigma-de':
            self.load_musigma_emu(verbose=verbose,model=model)
        else:    
            self.load_nonlinear_emu(verbose=verbose,model=model)

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
        eva_pars = self.emulator['keys']
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
    
    def _compute_ps_nonlin_musigma(self, pp, zbins):
        emu_model_nl_boost = 'model_nl_boost'
        emu_model_lin_ps = 'model_lin_ps'
        nl_boost_nonlin = self.emulator[emu_model_nl_boost].predictions_np(pp)
        ps_lin = self.emulator[emu_model_lin_ps].ten_to_predictions_np(pp)
        ps_lin_interp = [interpolate.interp1d(self.emulator['k_lin_ps'],
                                                ps_lin_i,
                                                kind='linear'
                                                ) for ps_lin_i in ps_lin]
        
        pnl = nl_boost_nonlin*np.array([ps_lin_interp[i](self.emulator['k_nl_boost']) for i in range(zbins)])
        return pnl
    
    
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
        emulator = self.emulator
        pp = self._get_parameters(kwargs)
        zbins = len(pp['z'])
        if self.model=='musigma-de':
            ps_nonlin = self._compute_ps_nonlin_musigma(pp, zbins) 
            pp_lcdm = copy.deepcopy(pp)
            pp_lcdm['mu0'] = np.zeros_like(pp['mu0'])
            pp_lcdm['sigma0'] = np.zeros_like(pp['sigma0'])
            ps_nonlin_lcdm = self._compute_ps_nonlin_musigma(pp_lcdm, zbins)

            boost_nonlin = ps_nonlin/ps_nonlin_lcdm
        else:    
            emu_model = 'model_tot'
            boost_nonlin = emulator[emu_model].predictions_np(pp)
    
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
                         fR0=None, omegarc = None, gamma = None, q1 = None,
                         mu0=None, sigma0=None,
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
    
    def get_linear_musigma_ps(self, Omega_m=None, 
                         Omega_b=None,
                         H0=None, ns=None, Omega_nu=None, As=None,
                         fR0=None, omegarc = None, gamma = None, q1 = None,
                         mu0=None, sigma0=None,
                         z=None, k=None, 
                         **kwargs):
        """Compute the prediction of the linear power spectrum in musigma-de.
        :param k: a vector of wavemodes in h/Mpc at which the nonlinear boost
                  will be computed, if None the default wavemodes of the
                  emulator will be used, defaults to None
        :type k: array_like, optional
        :return: k and the nonlinear boost
        :rtype: tuple
        """
        if self.model!='musigma-de':
            raise ValueError("This method is only available for the musigma-de model")
        _kwargs = locals()
        kwargs = {key: _kwargs[key]
                  for key in set(list(_kwargs.keys())) - set(['self'])}

        k = kwargs['k'] if 'k' in kwargs.keys() else None
        emulator = self.emulator
        pp = self._get_parameters(kwargs)
        zbins = len(pp['z'])
        ps_lin = self.emulator['model_lin_ps'].ten_to_predictions_np(pp)
        if k is not None:
            if (max(k) > max(emulator['k'])) | (min(k) < min(emulator['k'])):
                raise ValueError(f"""
                    A minimum k > {min(emulator['k_lin_ps'])} h/Mpc and a
                    maximum k < {max(emulator['k_lin_ps'])} h/Mpc
                    are required for the nonlinear emulator:
                    the current values are {min(k)} h/Mpc and {max(k)} h/Mpc
                    """)
            else:
                ps_lin_interp = [interpolate.interp1d(emulator['k_lin_ps'],
                                                    ps_lin_i,
                                                    kind='linear'
                                                    ) for ps_lin_i in ps_lin]
                ps_lin = np.array([ps_lin_interp[i](k) for i in range(zbins)])
        else:
            k = emulator['k']

        return k, ps_lin





    def load_nonlinear_emu(self, verbose=True, model='fr'):
        """Loads in memory the nonlinear boost emulator computed with  
        ReACT and trained with cosmopower.
        
        Defaults to f(R) emulator

        """

        if verbose:
            print('Loading nonlinear emulator...')

        basefold = os.path.dirname(os.path.abspath(__file__))    
        emulator_tot_name = (basefold+"/models"+version+"/"+model) 

        self.emulator['model_tot'] = cosmopower_NN(restore=True, 
                        restore_filename=emulator_tot_name,
                        )
        self.emulator['k'] = self.emulator['model_tot'].modes
        self.emulator['keys'] = self.emulator['model_tot'].parameters
        if verbose:
            print('Nonlinear emulator loaded in memory.')
            print('parameters used in emulator training: ', self.emulator['keys'])

    def load_musigma_emu(self, verbose=True, model='musigma-de'):
        """Loads in memory the nonlinear boost emulator, Pnl/Pl, instead of 
         Pnl/Pnl_lcdm, and the linear power spectrum emulator Pl 
         -- both trained with cosmopower.


        :return: a dictionary containing the emulator object
        :rtype: dict
        """
        if verbose:
            print('Loading nonlinear boost and linear emulators...')

        basefold = os.path.dirname(os.path.abspath(__file__))    
        emulator_lin_ps_name = (basefold+"/models"+version+"/musigma_linear_log10ps") 
        emulator_nl_boost_name = (basefold+"/models"+version+"/musigma_nonlinearboost")

        self.emulator['model_nl_boost'] = cosmopower_NN(restore=True, 
                        restore_filename=emulator_nl_boost_name,
                        )
        self.emulator['model_lin_ps'] = cosmopower_NN(restore=True, 
                        restore_filename=emulator_lin_ps_name,
                        )
        self.emulator['k_nl_boost'] = self.emulator['model_nl_boost'].modes
        self.emulator['k_lin_ps'] = self.emulator['model_lin_ps'].modes
        self.emulator['keys'] = self.emulator['model_nl_boost'].parameters+['sigma0']
        self.emulator['k'] = self.emulator['k_nl_boost']
        if verbose:
            print('Nonlinear and linear emulators loaded in memory.')
            print('parameters used in emulator training: ', self.emulator['keys'])





