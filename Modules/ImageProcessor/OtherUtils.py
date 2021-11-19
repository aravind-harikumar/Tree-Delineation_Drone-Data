import os

def TouchPath(folder_path):
    # check existance of dsm tile output folder
    full_dir_path = os.path.join(folder_path)
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path)
        print("Folder does not exists! creating folder!")
