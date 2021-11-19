import subprocess
from subprocess import Popen
import os, sys
a = '/home/ensmingerlabgpu/Documents/MATLAB/BasicSnake_version2f' # test2D.m
os.chdir(a)
import matlab.engine

date = '20180514'
future = matlab.engine.start_matlab(background=True)
eng = future.result()
eng.test2D(date,nargout=0)
eng.quit()
print('Completed!')

























# functstr = ["matlab", " -nodisplay -nosplash - nodesktop -r", 'test2D; exit;']
# child = subprocess.Popen(functstr, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
# output, errors = child.communicate()
# print(output)
# print('dddddddddddddddd')