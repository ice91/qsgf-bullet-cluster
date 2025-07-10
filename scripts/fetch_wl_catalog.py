#!/usr/bin/env python3
"""
Download and calibrate weak-lensing shear catalog from MAST.
"""
import os
import argparse
import pandas as pd
from astroquery.mast import Observations

def fetch_wl_catalog(filters, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # Query JWST/NIRCam catalogs for shear measurements
    obs = Observations.query_criteria(
        obs_collection='JWST',
        proposal_id='GO-4598',
        instrument_name='NIRCam',
        dataproduct_type='image'
    )
    products = Observations.get_product_list(obs)

    # 篩出 catalog 類型 CSV 檔
    wl_products = Observations.filter_products(
        products,
        productSubGroupDescription='CATALOG',
        extension='csv',
        mrp_only=False
    )

    if len(wl_products) == 0:
        print("[ERROR] No WL catalog products found.")
        return

    print(f"Found {len(wl_products)} shear catalogs; downloading...")
    manifest = Observations.download_products(wl_products, download_dir=out_dir)
    print("Download complete.")

    # 假設第一個 CSV 是我們要的 shear catalog
    csv_path = os.path.join(out_dir, wl_products[0]['productFilename'])
    print(f"Loading catalog from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Example shape and redshift cuts
    df = df[df['snr'] > 10]
    df = df[df['size'] > df['psf_size']]

    out_path = os.path.join(out_dir, 'wl_catalog.filtered.csv')
    df.to_csv(out_path, index=False)
    print(f"Filtered WL catalog saved to {out_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fetch and filter WL catalog')
    parser.add_argument('--filters', nargs='+', required=True,
                        help='Bands used for shape measurement, e.g. F150W F200W')
    parser.add_argument('--out-dir', default='data/raw/wl_catalog',
                        help='Output directory')
    args = parser.parse_args()
    fetch_wl_catalog(args.filters, args.out_dir)
