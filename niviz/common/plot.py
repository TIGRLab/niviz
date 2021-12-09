'''
Plotting layouts and utilities
'''
import nilearn.image as nimg
import nilearn.plotting as nplot
from niworkflows.viz.utils import (cuts_from_bbox, extract_svg,
                                   robust_set_limits)
from svgutils.transform import fromstring


def plot_orthogonal_views(data,
                          bbox_nii=None,
                          auto_brightness=False,
                          display_modes=['x', 'y', 'z'],
                          n_cuts=10,
                          plot_func=nplot.plot_anat,
                          figure_title=""):

    if bbox_nii is None:
        bbox_nii = nimg.threshold_img(data, 1e-3)

    cuts = cuts_from_bbox(data, cuts=n_cuts)
    if auto_brightness:
        robust_params = robust_set_limits(bbox_nii.get_fdata().reshape(-1), {})
    else:
        robust_params = {}

    svgs = []
    for d in display_modes:
        plot_params = {
            "display_mode": d,
            "cut_coords": cuts[d],
            **robust_params
        }
        display = plot_func(data, **plot_params)
        svg = extract_svg(display)
        svg = svg.replace("figure_1", f"{figure_title}-{d}")
        svgs.append(fromstring(svg))
        display.close()
    return svgs


def plot_montage(data,
                 orientation,
                 bbox_nii=None,
                 n_cuts=15,
                 n_cols=5,
                 auto_brightness=False,
                 plot_func=nplot.plot_anat,
                 figure_title="figure"):
    '''
    Plot a montage of cuts for a given orientation
    for an image
    '''

    if bbox_nii is None:
        bbox_nii = nimg.threshold_img(data, 1e-3)

    cuts = cuts_from_bbox(bbox_nii, cuts=n_cuts)
    if auto_brightness:
        robust_params = robust_set_limits(bbox_nii.get_fdata().reshape(-1), {})
    else:
        robust_params = {}

    svgs = []
    for i in range(n_cuts // n_cols):

        start = i * n_cols
        end = min(i * n_cols + n_cols, n_cuts)
        row_cuts = cuts[orientation][start:end]

        plot_params = {
            "display_mode": orientation,
            "cut_coords": row_cuts,
            **robust_params
        }

        display = plot_func(data, **plot_params)
        svg = extract_svg(display)
        svg = svg.replace("figure_1", f"{figure_title}:{start}-{end}")
        svgs.append(fromstring(svg))

    return svgs
