# scripts/fetch_wl_catalog.py
#!/usr/bin/env python3
"""
Download and calibrate weak-lensing shear catalog.
"""
import os
import argparse
import pandas as pd
import requests

def fetch_wl_catalog(filters, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # Placeholder URL
    url = 'https://example.com/wl_catalog.csv'
    r = requests.get(url)
    csv_path = os.path.join(out_dir, 'wl_catalog.raw.csv')
    with open(csv_path, 'wb') as f:
        f.write(r.content)
    print(f"Downloaded WL catalog to {csv_path}")
    # Load and apply PSF deconvolution flags etc.
    df = pd.read_csv(csv_path)
    # Example shape and redshift cuts
    df = df[df['snr']>10]
    df = df[df['size']>df['psf_size']]
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