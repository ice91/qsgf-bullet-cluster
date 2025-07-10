#!/usr/bin/env python3
"""
Fetch JWST NIRCam FITS files from MAST for a given program and filters.
"""
import os
import argparse
from astroquery.mast import Observations

def fetch_jwst(program, filters, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    obs_table = Observations.query_criteria(
        obs_collection='JWST',
        project=program,
        instrument_name='NIRCam',
        dataproduct_type='image'
    )

    if len(obs_table) == 0:
        print(f"[ERROR] No JWST/NIRCam observations for program {program}")
        return

    # 将 MaskedColumn 转 Python list，再用列表推导过滤
    all_filters = obs_table['filters'].tolist()
    mask = [any(f in flist for f in filters) for flist in all_filters]
    filt_obs = obs_table[mask]

    if len(filt_obs) == 0:
        print(f"[ERROR] No data match filters {filters}")
        return

    products = Observations.get_product_list(filt_obs)
    calib = Observations.filter_products(
        products,
        productSubGroupDescription='CAL',
        extension='fits',
        mrp_only=False
    )

    print(f"Found {len(calib)} calibrated files. Downloading…")
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
