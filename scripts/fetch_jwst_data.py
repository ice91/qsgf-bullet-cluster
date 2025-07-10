#!/usr/bin/env python3
"""
Fetch JWST NIRCam FITS files from MAST for a given program and filters.
"""
import os
import argparse
from astroquery.mast import Observations

def fetch_jwst(program, filters, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # Query JWST/NIRCam images for the given proposal_id
    obs_table = Observations.query_criteria(
        obs_collection='JWST',
        proposal_id=program,          # e.g. 'GO-4598'
        instrument_name='NIRCam',
        dataproduct_type='image'
    )

    # Filter by NIRCam filters list
    filt_obs = obs_table[
        obs_table['filters'].apply(lambda fl: any(f in fl for f in filters))
    ]

    if len(filt_obs) == 0:
        print(f"[ERROR] No JWST/NIRCam data for program {program} with filters {filters}")
        return

    # Get product list and select calibrated FITS
    products = Observations.get_product_list(filt_obs)
    calib = Observations.filter_products(
        products,
        productSubGroupDescription='CAL',
        extension='fits',
        mrp_only=False
    )

    print(f"Found {len(calib)} calibrated files. Downloading …")
    Observations.download_products(calib, download_dir=out_dir)
    print("Download complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download JWST NIRCam FITS from MAST')
    parser.add_argument('--program', required=True,
                        help='MAST proposal_id, e.g. GO-4598')
    parser.add_argument('--filters', nargs='+', required=True,
                        help='List of NIRCam filters, e.g. F115W F150W')
    parser.add_argument('--out-dir', default='data/raw/jwst',
                        help='Output directory')
    args = parser.parse_args()
    fetch_jwst(args.program, args.filters, args.out_dir)
