# Tree Delineation in VHR Optical Drone Data

The module detects individual trees in drone-based optical remote sensing data, and tree-level physiogicval parameter estiamtion. In particular the module performs the followng: 
Markup : * Bullet list Raw drone-based optical data preprocessing (including nDSM and orthomosaic generatation using photogrammetric processing using Agisoft APIs).
          * Bullet list Detects individual tree
a) Raw drone-based optical data preprocessing (including nDSM and orthomosaic generatation using photogrammetric processing using Agisoft APIs).
b) Detects individual tree
c) Genate fuzzy (FCM-MRF) maps of forest
c) Delineated individual trees
d) Estimate tree biophysical and physiological parameters.

Syntax:
python GenerateOrthoImage.py

NOTES:
a) Agisoft Metashape Professional Software
b) Python version should be >= 3.7.
c) Ensure that the following Python packages exist in your Python Environment: datatime, numpy, pandas, and Metashape. The Metashape package can be found at :https://s3-eu-west-1.amazonaws.com/download.agisoft.com/Metashape-1.6.5-cp35.cp36.cp37-none-win_amd64.whl. Download and extract it; Run the following command from inside the extracted folder:python -m pip install <.whl-file-name> )
d) Change data in/out path in the code.
