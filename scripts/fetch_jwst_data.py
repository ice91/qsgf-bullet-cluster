# scripts/fetch_jwst_data.py
#!/usr/bin/env python3
"""
Fetch JWST NIRCam FITS files from MAST for a given program and filters.
"""
import os
import argparse
from astroquery.mast import Observations

def fetch_jwst(program, filters, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # 直接在 query_criteria 篩選 instrument_name 與 filters
    obs_table = Observations.query_criteria(
        facility_name='JWST',
        instrument_name='NIRCam',
        filters=filters,
        project=program,
        dataproduct_type='image',
    )

    if len(obs_table) == 0:
        print(f"[ERROR] No JWST/NIRCam observations found for program {program} with filters {filters}")
        return

    # 取 products 並下載 calibrated FITS 檔
    products = Observations.get_product_list(obs_table)
    calib = Observations.filter_products(
        products,
        productSubGroupDescription='CAL',
        extension='fits',
        mrp_only=False
    )

    print(f"Found {len(calib)} files. Downloading to {out_dir} ...")
    Observations.download_products(calib, download_dir=out_dir)
    print("Download complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download JWST NIRCam FITS from MAST')
    parser.add_argument('--program', required=True,
                        help='MAST Program ID, e.g. GO-2561')
    parser.add_argument('--filters', nargs='+', required=True,
                        help='List of NIRCam filters, e.g. F115W F150W')
    parser.add_argument('--out-dir', default='data/raw/jwst',
                        help='Output directory')
    args = parser.parse_args()
    fetch_jwst(args.program, args.filters, args.out_dir)
