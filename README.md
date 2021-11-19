# Tree Delineation in VHR Optical Drone Data

The module detects individual trees in drone-based optical remote sensing data, and tree-level physiogicval parameter estiamtion. In particular the module performs the followng: 
- Raw drone-based optical data preprocessing (including nDSM and orthomosaic generatation using photogrammetric processing using Agisoft APIs).
- Detect individual tree
- Genate fuzzy (FCM-MRF) map for crow and background
- Delineated individual trees
- Estimate tree biophysical and physiological parameters.
- 
Syntax:
python GenerateOrthoImage.py

NOTES:
* Agisoft Metashape Professional Software
* Python version should be >= 3.7.
* Ensure that the following Python packages exist in your Python Environment: datatime, numpy, pandas, and Metashape. The Metashape package can be found at :https://s3-eu-west-1.amazonaws.com/download.agisoft.com/Metashape-1.6.5-cp35.cp36.cp37-none-win_amd64.whl. Download and extract it; Run the following command from inside the extracted folder:python -m pip install <.whl-file-name> )
* Change data in/out path in the code.
