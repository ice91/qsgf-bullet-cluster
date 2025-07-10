# Makefile — 一鍵化執行整條管線

CONDA_ENV := qsgf-bc
PYTHON     := python
MAST_PROG  := GO-2561
JWST_FLTS  := F090W F115W F150W F200W F277W F356W F410M F444W

.PHONY: all env download mass_map flow mhd fit plots test clean

all: mass_map flow mhd fit plots

## 建議建立與啟動 Conda 環境
env:
	@echo "建立並啟動 Conda 環境…"
	conda env create -f environment.yml
	@echo "啟動後： conda activate $(CONDA_ENV)"

## 下載所有原始資料
download: download_jwst download_sl download_wl preprocess_icl

download_jwst:
	@$(PYTHON) scripts/fetch_jwst_data.py \
			--program $(MAST_PROG) \
			--filters $(JWST_FLTS) \
			--out-dir data/raw/jwst \
		|| { echo "[FAIL] fetch_jwst_data failed"; exit 1; }


download_sl:
	$(PYTHON) scripts/fetch_sl_catalog.py \
		--source Remus2023 \
		--out-dir data/raw/sl_catalog

download_wl:
	$(PYTHON) scripts/fetch_wl_catalog.py \
		--filters F150W F200W \
		--out-dir data/raw/wl_catalog

preprocess_icl:
	$(PYTHON) scripts/preprocess_icl.py \
		--fits data/raw/jwst/F277W_cal.fits \
		--out-dir data/processed/icl_contours \
		--isophotes 27.5 28.0 28.5

## 重建質量地圖
mass_map:
	$(PYTHON) - <<EOF
	from src.recon.mars_interface import run_mars
	run_mars('data/raw/sl_catalog/Remus2023_sl_catalog.filtered.csv',
		'data/raw/wl_catalog/wl_catalog.filtered.csv',
		out_map='data/processed/mass_maps/kappa.npy')
	EOF

## 計算幾何流並輸出等值線
flow:
	$(PYTHON) - <<EOF
	from src.qsgf.flow_field import compute_streamlines
	compute_streamlines('data/processed/mass_maps/kappa.npy',
					params_file='config/eps_params.yaml',
					out_dir='data/processed/flow_contours')
	EOF

## 計算 ICL–流線對齊指標
mhd:
	$(PYTHON) - <<EOF
	from src.qsgf.metrics import compute_mhd
	compute_mhd('data/processed/icl_contours/icontour_28.0.npy',
				'data/processed/flow_contours/streamline.npy',
				clip=1.0)
	EOF

## 執行 MCMC 擬合
fit:
	$(PYTHON) src/sampling/mcmc.py --config config/mcmc.yaml --output results/chain.h5

## 繪製結果圖
plots:
	$(PYTHON) - <<EOF
	from src.viz.plot_maps import plot_kappa_vs_flow
	plot_kappa_vs_flow('data/processed/mass_maps/kappa.npy',
						'data/processed/flow_contours/streamline.npy',
						out_png='figures/kappa_vs_flow.png')
	from src.viz.plot_corner import plot_corner
	plot_corner('results/chain.h5', out_png='figures/corner.png')
	EOF

## 執行單元測試
test:
	pytest --maxfail=1 --disable-warnings -q

## 清除中繼檔與結果
clean:
	rm -rf data/processed/*
	rm -rf results/*
	rm -rf figures/*
