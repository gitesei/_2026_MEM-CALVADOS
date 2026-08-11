## MEM-CALVADOS: A Residue-Level Model for Flexible Membrane Protein

The repository contains the code and data to reproduce the analyses in the manuscript __MEM-CALVADOS: A Residue-Level Model for Flexible Membrane Proteins__.

### Layout
- `lipid_scan.ipynb` reproduces Fig. 2 and related SI figures
- `omega_scan.ipynb` reproduces Fig. 3 and related SI figures
- `WLXLL.ipynb` reproduces Fig. 4
- `GHR.ipynb` reproduces Fig. 5 and related SI figures
- `LAT_Grb2_Sos1.ipynb` reproduces Fig. 6 and related SI figures 
- `data/` contains the data used in the notebooks

### Usage

To open the Notebook, install [Miniconda](https://conda.io/miniconda.html) and make sure all required packages are installed by issuing the following terminal commands

```bash
    conda env create -f environment.yml
    conda activate memcal
    jupyter-notebook
```


