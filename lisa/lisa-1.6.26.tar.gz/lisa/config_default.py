#! /usr/bin/python
# -*- coding: utf-8 -*-

CONFIG_DEFAULT={
    "autocrop": True,
    "autocrop_margin_mm": [10, 10, 10],
    "data3d": None,
    "datapath": None,
    "edit_data": False,
    "manualroi": True,
    "metadata": None,
    "output_label": 1,
    "qt_app": None,
    "roi": None,
    "seeds": None,
    "segmentation_smoothing": False,
    "segmodelparams": {
        # 'mdl_stored_file': '~/lisa_data/liver_intensity.Model.p',
        # "fv_type": 'fv_extern',
        # 'fv_extern':'intensity_localization_fv',
        # 'method': 'multiscale_graphcut',
        "params": {"covariance_type": "full", "n_components": 3}
    },
    "type": "gmmsame",
    "segparams": {"pairwise_alpha_per_mm2":45, "return_only_object_with_seeds": True},
    "series_number": None,
    "slab": {},
    "smoothing_mm": 4,
    "texture_analysis": None,
    "working_voxelsize_mm": 2.0,
    "viewermax": 225,
    "viewermin": -125,
}