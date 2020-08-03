#!/usr/bin/env python
"""
    grid

    Module to handle loading general model grid information for NEMO
    Written by Dale Partridge on 03/07/2019

    **Example Usage**

    >>>> g = nt.grid('mesh_mask.nc')

"""

import netCDF4
import numpy as np
import nemotools as nt

_grid_vars = {"xn" : ["jpiglo"],
              "yn" : ["jpjglo"],
              "zn" : ["jpkglo"],
              "lon_T": ["glamt"],
              "lat_T": ["gphit"],
              "x_len_T": ["e1t"],
              "y_len_T": ["e2t"],
              "h": ["hbatt"],
              "h_idx": ["mbathy"],
              "lon_U": ["glamu"],
              "lat_U": ["gphiu"],
              "x_len_U": ["e1u"],
              "y_len_U": ["e2u"],
              "lon_V": ["glamv"],
              "lat_V": ["gphiv"],
              "x_len_V": ["e1v"],
              "y_len_V": ["e2v"]
              }
_depth_vars = {"depth0_T": ["gdept_0"],
               "depth0_W": ["gdepw_0"]
              }
_thick_vars = {"thick0_T": ["e3t_0"],
               "thick0_U": ["e3u_0"],
               "thick0_V": ["e3v_0"]
              }
_mask_vars = {"Tmask_3d": ["tmask"],
              "Umask_3d": ["umask"],
              "Vmask_3d": ["vmask"]
              }
_to_mask = ["h","h_idx"]

class grid:

    def __init__(self, filename=None, bathfile=None, bathvar=None,
                                depths=False, thicks=False, apply_mask=True):
        """
        Initialise the grid class. If file given, load the variables from it
        
        Inputs
        ------
        filename : string, optional
            Path to grid file containing variables relating to the NEMO grid
        bathfile : string, optional
            Path to bathymetry file relating to the grid
        bathvar : string, optional
            Variable name of bathymetry in bathfile. Defaults to 'Bathymetry'
        thicks : bool, optional
            If True, load the 3D initial thickness variables. Default is False
        apply_mask : bool, optional
            If True, apply mask to the relevant fields. Default is True
        """
        self.filename = filename
        self.bathfile = bathfile
        if self.bathfile is not None:
            self.h_var = bathvar if bathvar is not None else 'Bathymetry'
        self.depths = depths
        self.thicks = thicks
        self.mask_applied = apply_mask
        if self.filename is not None:
            self._initfile()
        else:
            print('No file')

    def _initfile(self):
        """
        Function to load variables for given file
        """
        self._nc = netCDF4.Dataset(self.filename)
        ncvars = {v.lower(): v for v in self._nc.variables.keys()}
       
        for v in _mask_vars:
            for ip in _mask_vars[v]:
                if ip in ncvars:
                    self.__dict__[v] = np.squeeze(self._nc.variables[ncvars[ip]][:])
                    self.__dict__[v.replace('3d','2d')] = np.squeeze(self.__dict__[v][0,:])

        for v in _grid_vars:
            for ip in _grid_vars[v]:
                if ip in ncvars:
                    self.__dict__[v] = np.squeeze(self._nc.variables[ncvars[ip]][:])
                    if v in _to_mask and self.mask_applied:
                        n_dims = len(self.__dict__[v].shape)
                        if n_dims == 2:
                            self.__dict__[v] = np.ma.masked_array(self.__dict__[v], mask = nt.mask.reverse_mask(self.Tmask_2d))
                        elif n_dims == 3:
                            self.__dict__[var] = np.ma.masked_array(self.__dict__[v], mask = nt.mask.reverse_mask(self.Tmask_3d))
                        else:
                            raise RuntimeError("Unsupported number of dimensions (={}) for "
                                           "variable `{}'.".format(n_dims, var))

        self._nc.close()

        if self.depths:
            self.load_depth()
        
        if self.thicks:
            self.load_thick()

        if self.bathfile is not None:
            self.load_bathy(self.bathfile, self.h_var)

    def load_bathy(self, filename, h='Bathymetry'):
        """
        Function to load bathymetry from separate file

        Inputs
        ------
        filename : str
            Path to bathymetry file
        h : str, optional
            Name of bathymetry variable in file. Default is 'Bathymetry'
        """
        _nc = netCDF4.Dataset(filename)
        self.__dict__['h'] = np.ma.masked_array(np.squeeze(_nc.variables[h][:]), mask = nt.mask.reverse_mask(self.Tmask_2d))
        _nc.close()
                
    def load_depth(self):
        """
        Function to load the initial depth of the cells 

        """
        self.depths = True
        self._nc = netCDF4.Dataset(self.filename)
        ncvars = {v.lower(): v for v in self._nc.variables.keys()}
        for v in _depth_vars:
            for ip in _depth_vars[v]:
                if ip in ncvars:
                    self.__dict__[v] = np.squeeze(self._nc.variables[ncvars[ip]][:])
        self._nc.close()
    
    def load_thick(self):
        """
        Function to load the initial thickness of the cells

        """
        self.thicks = True
        self._nc = netCDF4.Dataset(self.filename)
        ncvars = {v.lower(): v for v in self._nc.variables.keys()}
        for v in _thick_vars:
            for ip in _thick_vars[v]:
                if ip in ncvars:
                    self.__dict__[v] = np.squeeze(self._nc.variables[ncvars[ip]][:])
        self._nc.close()

    def area(self,grid='T'):
        """
        Function to calculate the area of each grid cell

        Inputs
        ------
        grid : string, optional
            Indicates which grid to use; T, U or V. Default = T

        Outputs
        -------
        area : array
            Returns array the same shape as input grid
        """
        return {'T': self.x_len_T * self.y_len_T,
                'U': self.x_len_U * self.y_len_U,
                'V': self.x_len_V * self.y_len_V}.get(grid, 'Invalid input grid')
