from __future__ import annotations
from typing import TYPE_CHECKING
import os

import numpy as np

import nibabel as nib
import nilearn.image as nimg

from nipype.interfaces.mixins import reporting
from nipype.interfaces.base import File, Directory
import niworkflows.interfaces.report_base as nrc

from ..node_factory import register_interface
from niviz.interfaces.mixins import (ParcellationRC, _ParcellationInputSpecRPT,
                                     IdentityRPT)

if TYPE_CHECKING:
    from nipype.interfaces.base.support import Bunch


class _FSInputSpecRPT(nrc._SVGReportCapableInputSpec):
    bg_nii = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Background NIFTI for SVG, will use T1.mgz if not '
                  'specified',
                  mandatory=False)

    fs_dir = Directory(exists=True,
                       usedefault=False,
                       resolve=True,
                       desc='Subject freesurfer directory',
                       mandatory=True)


class _IFSCoregInputSpecRPT(_FSInputSpecRPT):
    fg_nii = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Foreground NIFTI for SVG',
                  mandatory=True)


class _IFSCoregOutputSpecRPT(reporting.ReportCapableOutputSpec):
    pass


class IFSCoregRPT(IdentityRPT, nrc.RegistrationRC):

    input_spec = _IFSCoregInputSpecRPT
    output_spec = _IFSCoregOutputSpecRPT

    def _post_run_hook(self, runtime: Bunch) -> Bunch:
        """Side-effect function of IFSCoregRPT.

        Generates Freesurfer-based EPI2T1 coregistration report
        Args:
            runtime: Nipype runtime object

        Returns:
            runtime: Resultant runtime object propogated through ReportCapable
            interfaces

        """

        self._fixed_image = self.inputs.bg_nii
        self._moving_image = self.inputs.fg_nii
        self._contour = os.path.join(self.inputs.fs_dir, 'mri', 'ribbon.mgz')

        return super(IFSCoregRPT, self)._post_run_hook(runtime)


class _IFreesurferVolParcellationInputSpecRPT(_ParcellationInputSpecRPT,
                                              _FSInputSpecRPT):
    mask_nii = File(exists=True,
                    usedefault=False,
                    resolve=True,
                    desc='Mask file to use on background nifti',
                    mandatory=False)
    pass


class _IFreesurferVolParcellationOutputSpecRPT(
        reporting.ReportCapableOutputSpec):
    pass


class IFreesurferVolParcellationRPT(ParcellationRC):
    '''
    Freesurfer-based Parcellation Report.

    Uses FreeSurferColorLUT table to map colors to integer values
    found in NIFTI file
    '''

    input_spec = _IFreesurferVolParcellationInputSpecRPT
    output_spec = _IFreesurferVolParcellationOutputSpecRPT

    def _post_run_hook(self, runtime: Bunch) -> Bunch:

        if not self.inputs.bg_nii:
            self._bg_nii = nib.load(
                os.path.join(self.inputs.fs_dir, "mri", "T1.mgz"))
        else:
            self._bg_nii = nib.load(self.inputs.bg_nii)

        self._mask_nii = self.inputs.mask_nii or None

        # TODO: ENUM this to the available freesurfer parcellations
        parcellation = nib.load(self.inputs.parcellation)
        d_parcellation = parcellation.get_fdata().astype(int)

        # Re-normalize the ROI values by rank
        # Then extract colors from full colortable using rank ordering
        unique_v, u_id = np.unique(d_parcellation.flatten(),
                                   return_inverse=True)
        colormap = _parse_freesurfer_LUT(self.inputs.colortable)

        # Remap parcellation to rank ordering
        d_parcellation = u_id.reshape(d_parcellation.shape)
        parcellation = nimg.new_img_like(parcellation,
                                         d_parcellation,
                                         copy_header=True)

        # Resample to background resolution
        self._parcellation = nimg.resample_to_img(parcellation,
                                                  self._bg_nii,
                                                  interpolation='nearest')

        # Get segmentation colors
        self._colors = [colormap[i] for i in unique_v]

        # Now we need to call the parent process
        return super(IFreesurferVolParcellationRPT,
                     self)._post_run_hook(runtime)


def _parse_freesurfer_LUT(colortable: str) -> dict:
    '''
    Parse Freesurfer-style colortable into a
    matplotlib compatible categorical colormap

    Args:
        Path to Freesurfer colormap table

    Returns:
        Matplotlib colormap object encoding Freesurfer colors
    '''
    color_mapping = {}
    with open(colortable, 'r') as ct:
        for line in ct:
            if "#" in line or not line.strip().strip("\n"):
                continue
            roi, _, r, g, b, _ = [
                entry for entry in line.strip("\n").split(" ") if entry
            ]
            color_mapping[int(roi)] = [
                int(r) / 255, int(g) / 255,
                int(b) / 255
            ]

    return color_mapping


def _run_imports() -> None:
    register_interface(IFSCoregRPT, 'freesurfer_coreg')
    register_interface(IFreesurferVolParcellationRPT,
                       'freesurfer_parcellation')
