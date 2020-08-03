#!/usr/bin/env python
"""
    mask

    Module containing functions related to masking
    Written by Dale Partridge on 15/07/2019

"""

import netCDF4
import numpy as np

def reverse_mask(arr):
    """ 
        Function to 'reverse' a mask, by converting zeros to ones and vice versa
    """
    return np.abs(arr-1)

def mask_from_array(in_arr, flags=None, inc=False):
    """
        Function to create mask from an array of flags, usually arising as 
        zone indicators

        Inputs
        ------
        in_arr : array 
            Input array the size of the desired mask. 
            Integer values represent different areas
        flags : array, optional  
            Array indicating the values to mask/keep. Default masks where arr=0
        inc : bool, optional
            If True, flags indicates values to keep instead of mask. Default=False  

        Outputs
        -------
        mask : array, bool
            Returns a mask the same shape as arr
    """

    return np.ma.masked_where(np.isin(in_arr,flags,invert=inc),in_arr).mask

