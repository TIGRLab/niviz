'''
Module containing common Mixin classes
'''

from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

import nilearn.image as nimg
from nipype.interfaces.mixins import reporting
from nipype.interfaces.base import File
import niworkflows.interfaces.report_base as nrc

if TYPE_CHECKING:
    from nipype.interfaces.base.support import Bunch


class IdentityRPT(reporting.ReportCapableInterface):
    '''
    Simple mixin class to implement an Identity node
    '''
    def _run_interface(self, runtime: Bunch) -> Bunch:
        """Instantiation of abstract method, does nothing

        Args:
            runtime: Nipype runtime object

        Returns:
            runtime: Resultant runtime object (unchanged)

        """
        return runtime


class _ParcellationInputSpecRPT(nrc._SVGReportCapableInputSpec):
    """
    General base input to constrain any parcellation-based
    visualization depending on ParcellationRC
    """
    parcellation = File(exists=True,
                        usedefault=False,
                        resolve=True,
                        desc="Parcellated NIFTI file",
                        mandatory=True)
    colortable = File(exists=True,
                      usedefault=False,
                      resolve=True,
                      desc="Lookup color table for parcellation")


class ParcellationRC(reporting.ReportCapableInterface):
    '''Abstract mixin for Parcellation visualization'''
    def _generate_report(self):
        '''
        Construct a parcellation overlay image
        '''
        import niworkflows.viz.utils as nwviz
        from ..patches.niworkflows import _3d_in_file, _plot_anat_with_contours
        '''
        MONKEY PATCH:
        _3d_in_file in niworkflows.viz.utils cannot accept Nifti1Images
        as inputs.

        This is a small patch that will stop it from failing when this is
        the case
        '''

        # _3d_in_file more robust to accepting a Nifti1Image
        nwviz._3d_in_file = _3d_in_file

        # plot_anat_with_contours accepts filled
        nwviz._plot_anat_with_contours = _plot_anat_with_contours

        segs = _parcel2segs(self._parcellation)
        nwviz.compose_view(
            nwviz.plot_segs(
                image_nii=self._bg_nii,
                seg_niis=segs,
                bbox_nii=self._mask_nii,
                out_file=None,  # this arg doesn't matter
                colors=self._colors,
                filled=True,
                alpha=0.3),
            fg_svgs=None,
            out_file=self._out_report)


# TODO: Move plotting/helper utilities into own module
# https://stackoverflow.com/questions/1376438/how-to-make-a-repeating-generator-in-python
def multigen(gen_func):
    class _multigen(object):
        def __init__(self, *args, **kwargs):
            self.__args = args
            self.__kwargs = kwargs

        def __iter__(self):
            return gen_func(*self.__args, **self.__kwargs)

    return _multigen


@multigen
def _parcel2segs(parcellation):
    d_parcellation = parcellation.get_fdata().astype(int)
    for i in np.unique(d_parcellation):
        yield nimg.new_img_like(parcellation, d_parcellation == i)
