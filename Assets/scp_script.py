import shutil
import os
from os.path import join



target_dir = '/mnt/bigai_ml/all_datasets/RoboVerse/roboverse_data/hssd_scenes'

source_dir = './data/all_scenes/'

for folder in os.listdir(source_dir):
    if folder.split('_')[-1] == 'final':
        if os.path.exists(join(target_dir, folder)):
            continue
        shutil.copytree(join(source_dir, folder), join(target_dir, folder))
        
