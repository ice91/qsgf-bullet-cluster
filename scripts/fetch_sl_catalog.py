# scripts/fetch_sl_catalog.py
#!/usr/bin/env python3
"""
Download and filter strong-lensing multiple image catalog.
"""
import os
import argparse
import pandas as pd
import requests

def fetch_sl_catalog(source, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # Example URL mapping
    urls = {
        'Remus2023': 'https://example.com/remus2023_sl_catalog.csv'
    }
    url = urls.get(source)
    if url is None:
        raise ValueError(f"Unknown source {source}")
    r = requests.get(url)
    csv_path = os.path.join(out_dir, f'{source}_sl_catalog.csv')
    with open(csv_path, 'wb') as f:
        f.write(r.content)
    print(f"Downloaded SL catalog to {csv_path}")
    # Filter ambiguous parity or unresolved morphology if columns exist
    df = pd.read_csv(csv_path)
    if 'parity' in df.columns:
        df = df[df['parity'].isin(['even','odd'])]
    if 'morphology_flag' in df.columns:
        df = df[df['morphology_flag']==0]
    filtered_path = os.path.join(out_dir, f'{source}_sl_catalog.filtered.csv')
    df.to_csv(filtered_path, index=False)
    print(f"Filtered SL catalog saved to {filtered_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fetch and filter SL catalog')
    parser.add_argument('--source', required=True,
                        help='Catalog source key, e.g. Remus2023')
    parser.add_argument('--out-dir', default='data/raw/sl_catalog',
                        help='Output directory')
    args = parser.parse_args()
    fetch_sl_catalog(args.source, args.out_dir)
