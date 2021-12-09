from __future__ import annotations
from typing import TYPE_CHECKING
from collections import namedtuple

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

import nibabel as nib
import nilearn.image as nimg
import nilearn.plotting as nplot
from nipype.interfaces.mixins import reporting
from traits.trait_types import BaseInt
from nipype.interfaces.base import File, traits
import niworkflows.interfaces.report_base as nrc
from niworkflows.viz.utils import cuts_from_bbox

from niviz.node_factory import register_interface
from niviz.interfaces.mixins import IdentityRPT
import niviz.surface

if TYPE_CHECKING:
    from nipype.interfaces.base.support import Bunch


class _ISurfMapInputSpecRPT(nrc._SVGReportCapableInputSpec):

    left_surf = File(exists=True,
                     usedefault=False,
                     resolve=True,
                     desc="Left surface mesh",
                     mandatory=True)

    right_surf = File(exists=True,
                      usedefault=False,
                      resolve=True,
                      desc="Right surface mesh",
                      mandatory=True)

    bg_map = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc="Cifti file containing background map data "
                  "(usually sulci depth)",
                  mandatory=False)

    cifti_map = File(exists=True,
                     usedefault=False,
                     resolve=True,
                     desc="Cifti file containing surface map data",
                     mandatory=False)

    colormap = traits.String("magma",
                             usedefault=True,
                             desc="Colormap to use to plot mapping",
                             mandatory=False)

    views = traits.List(
        [{
            "view": "lateral",
            "hemi": "left"
        }, {
            "view": "medial",
            "hemi": "left"
        }, {
            "view": "lateral",
            "hemi": "right"
        }, {
            "view": "medial",
            "hemi": "right"
        }],
        usedefault=True,
        desc="List of dictionaries describing views "
        " to display per map",
        inner_traits=traits.Dict(
            key_trait=traits.Enum(values=["view", "hemi"]),
            value_trait=traits.Enum(
                values=["lateral", "medial", "dorsal", "ventral"])))

    darkness = traits.Float(
        0.3,
        usedefault=True,
        desc="Multiplicative factor of bg_img onto foreground map",
        mandatory=False)
    visualize_all_maps = traits.Bool(False,
                                     usedefault=True,
                                     desc="Visualize all mappings in "
                                     "mapping file, if false will visualize "
                                     "only the first mapping")
    zero_nan = traits.Bool(False,
                           usedefault=True,
                           desc="Display NaNs as zeros")


class _ISurfMapOutputSpecRPT(reporting.ReportCapableOutputSpec):
    pass


class ISurfMapRPT(IdentityRPT):
    '''
    Class for generating Niviz surface visualizations given
    a mesh and surface mapping
    '''

    input_spec = _ISurfMapInputSpecRPT
    output_spec = _ISurfMapOutputSpecRPT

    def _post_run_hook(self, runtime: Bunch) -> Bunch:
        self._left_surf = self.inputs.left_surf
        self._right_surf = self.inputs.right_surf
        self._cifti_map = self.inputs.cifti_map
        self._bg_map = self.inputs.bg_map
        self._views = self.inputs.views
        self._colormap = self.inputs.colormap
        self._visualize_all_maps = self.inputs.visualize_all_maps
        self._darkness = self.inputs.darkness
        self._zero_nan = self.inputs.zero_nan

        return super(ISurfMapRPT, self)._post_run_hook(runtime)

    def _generate_report(self):
        """Side effect function of ISurfMapRPT

        Generate a surface visualization

        Args:
            runtime: Nipype runtime object

        Returns:
            runtime: Resultant runtime object
        """

        from mpl_toolkits import mplot3d  # noqa: F401

        Hemispheres = namedtuple("Hemispheres", ["left", "right"])

        l_surf = nib.load(self._left_surf)
        r_surf = nib.load(self._right_surf)
        num_views = len(self._views)
        num_maps = 1
        vmin, vmax = None, None

        if self._cifti_map:
            cifti_map = nib.load(self._cifti_map)
            lv, lt, lm = niviz.surface.map_cifti_to_gifti(l_surf, cifti_map)
            rv, rt, rm = niviz.surface.map_cifti_to_gifti(r_surf, cifti_map)

            if lm.ndim == 1:
                lm = lm[None, :]
                rm = rm[None, :]

            if not self._visualize_all_maps:
                lm = lm[0, :]
                rm = rm[0, :]
            else:
                num_maps = lm.shape[0]

            map_hemi = Hemispheres(left=(lv, lt, lm), right=(rv, rt, rm))
            vmin, vmax = np.nanpercentile(cifti_map.get_fdata(), [2, 98])
        else:
            # Use vertices and triangles from Mesh
            lv, lt = niviz.surface.gifti_get_mesh(l_surf)
            rv, rt = niviz.surface.gifti_get_mesh(r_surf)
            map_hemi = Hemispheres(left=(lv, lt, None), right=(rv, rt, None))

        if self._bg_map:
            bg_map = nib.load(self._bg_map)
            _, _, l_bg = niviz.surface.map_cifti_to_gifti(l_surf, bg_map)
            _, _, r_bg = niviz.surface.map_cifti_to_gifti(r_surf, bg_map)
            bg_hemi = Hemispheres(left=l_bg, right=r_bg)
        else:
            bg_hemi = Hemispheres(left=None, right=None)

        # Construct figure
        w, h = plt.figaspect(num_maps / (num_views))
        fig, axs = plt.subplots(num_maps,
                                num_views,
                                subplot_kw={'projection': '3d'},
                                figsize=(w, h))
        fig.set_facecolor("black")
        fig.tight_layout()

        for i, a in enumerate(axs.flat):
            a.set_facecolor("black")

            view_ind = i % num_views
            map_ind = i // num_views

            view = self._views[view_ind]["view"]
            hemi = self._views[view_ind]["hemi"]

            display_map = getattr(map_hemi, hemi)
            display_bg = getattr(bg_hemi, hemi)

            v, t, m = display_map
            m = m[map_ind]
            if self._zero_nan:
                m[np.isnan(m)] = 0

            # Plot
            nplot.plot_surf([v, t],
                            surf_map=m,
                            bg_map=display_bg,
                            cmap=self._colormap,
                            axes=a,
                            hemi=hemi,
                            view=view,
                            bg_on_data=True,
                            darkness=self._darkness,
                            vmin=vmin,
                            vmax=vmax)

        plt.draw()
        plt.savefig(self._out_report)


class _ISurfVolInputSpecRPT(nrc._SVGReportCapableInputSpec):
    '''
    Input spec for reports coregistering surface and volume images

    '''
    bg_nii = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Background NIFTI for SVG',
                  mandatory=True)

    fg_nii = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Foreground NIFTI for SVG')

    surf_l = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Left surface file',
                  mandatory=True)

    surf_r = File(exists=True,
                  usedefault=False,
                  resolve=True,
                  desc='Right surface file',
                  mandatory=True)

    n_cuts = BaseInt(desc='Number of slices to display')


class _ISurfVolOutputSpecRPT(reporting.ReportCapableOutputSpec):
    pass


class SurfVolRC(IdentityRPT):
    '''
    Abstract mixin for surface-volume coregistered images
    '''
    pass


class ISurfVolRPT(SurfVolRC):
    '''
    Report interface for co-registered surface/volumetric images
    '''
    input_spec = _ISurfVolInputSpecRPT
    output_spec = _ISurfVolOutputSpecRPT

    def _post_run_hook(self, runtime):

        self._bg_nii = self.inputs.bg_nii
        self._fg_nii = self.inputs.fg_nii or None
        self._surf_l = self.inputs.surf_l
        self._surf_r = self.inputs.surf_r
        self._ncuts = self.inputs.n_cuts or 7

        # Propogate to superclass
        return super(ISurfVolRPT, self)._post_run_hook(runtime)

    def _generate_report(self):
        '''Make a composite for co-registration of surface and volume images'''

        import trimesh

        l_surf = nib.load(self._surf_l)
        r_surf = nib.load(self._surf_r)
        vol_img = nib.load(self._bg_nii)

        if vol_img.ndim == 4:
            vol_img = vol_img.slicer[:, :, :, 0]

        verts, trigs, offset = niviz.surface.gifti_get_full_brain_mesh(
            l_surf, r_surf)

        mesh = trimesh.Trimesh(vertices=verts, faces=trigs)
        mask_nii = nimg.threshold_img(vol_img, 1e-3)
        cuts = cuts_from_bbox(mask_nii, cuts=self._ncuts)

        sections = mesh.section_multiplane(plane_normal=[0, 0, 1],
                                           plane_origin=[0, 0, 0],
                                           heights=cuts['z'])

        zh = nplot.plot_anat(vol_img, display_mode='z', cut_coords=cuts['z'])

        for z, s in zip(cuts['z'], sections):
            ax = zh.axes[z].ax
            if s:
                for segs in s.discrete:
                    ax.plot(*segs.T, color='r', linewidth=0.5)

        if self._fg_nii:
            fg_img = nib.load(self._fg_nii).slicer[:, :, :, 0]
            fg_img = nimg.resample_to_img(fg_img,
                                          vol_img,
                                          interpolation="linear")
            # Custom colormap with transparencies
            ncolors = 256
            basecmap = 'viridis_r'
            color_array = plt.get_cmap(basecmap)(range(ncolors))
            color_array[:, -1] = np.linspace(1.0, 0.0, ncolors)

            # Set background intensity=0 to transparent
            color_array[0, :] = 0
            cmapviridis = mcolors.LinearSegmentedColormap.from_list(
                basecmap, colors=color_array)

            zh.add_overlay(fg_img, cmap=cmapviridis)

        zh.savefig(self._out_report)


def _run_imports() -> None:
    register_interface(ISurfMapRPT, 'surface')
    register_interface(ISurfVolRPT, 'surface_coreg')
