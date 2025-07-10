# scripts/preprocess_icl.py
#!/usr/bin/env python3
"""
Extract ICL isophotes from JWST F277W mosaic.
"""
import os
import argparse
import numpy as np
from astropy.io import fits
from photutils import Background2D, MedianBackground
from photutils import detect_threshold, detect_sources
from photutils import segmentation
from skimage import measure
import matplotlib.pyplot as plt


def preprocess_icl(fits_path, out_dir, isophotes):
    os.makedirs(out_dir, exist_ok=True)
    # Load image
    with fits.open(fits_path) as hdul:
        data = hdul[1].data  # assume SCI extension
    # Estimate background
    bkg = Background2D(data, (128,128), filter_size=(3,3), bkg_estimator=MedianBackground())
    data_sub = data - bkg.background
    # Mask sources using segmentation
    threshold = detect_threshold(data_sub, nsigma=2.)
    segm = detect_sources(data_sub, threshold, npixels=20)
    mask = segm.data > 0
    data_masked = np.copy(data_sub)
    data_masked[mask] = np.nan
    # Median filter to smooth residual
    from scipy.ndimage import median_filter
    smooth = median_filter(data_masked, size=15)
    # Extract isophotes using skimage
    for level in isophotes:
        # convert mag/arcsec2 to flux level (placeholder)
        flux_level = 10**(-0.4 * (level - 25))
        contours = measure.find_contours(smooth, flux_level)
        out_file = os.path.join(out_dir, f'icontour_{level:.1f}.npy')
        np.save(out_file, contours)
        print(f"Saved {len(contours)} contours at {level} mag/arcsec² to {out_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Preprocess ICL and extract isophotes')
    parser.add_argument('--fits', required=True,
                        help='Path to F277W mosaic FITS file')
    parser.add_argument('--out-dir', default='data/processed/icl_contours',
                        help='Output directory')
    parser.add_argument('--isophotes', nargs='+', type=float, default=[27.5,28.0,28.5],
                        help='List of mag/arcsec^2 isophote levels')
    args = parser.parse_args()
    preprocess_icl(args.fits, args.out_dir, args.isophotes)
