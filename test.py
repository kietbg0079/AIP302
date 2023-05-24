import os
import shutil
import numpy as np


def split_train_val(path, dest, class_name, val_ratio):
    files = os.listdir(path)
    size = len(files)

    val_len = int(size * val_ratio)
    arr_file = np.array(files)
    np.random.shuffle(arr_file)

    val_lst = arr_file[:val_len]
    train_lst = arr_file[val_len:]

    dest_val = os.path.join(dest, f'val/{class_name}')
    dest_train = os.path.join(dest, f'train/{class_name}')
    os.makedirs(dest_val, exist_ok=True)
    os.makedirs(dest_train, exist_ok=True)

    for img in val_lst:
        shutil.copy(os.path.join(path, img), dest_val)

    for img in train_lst:
        shutil.copy(os.path.join(path, img), dest_train)


for i in ['amaranth', 'morning-glory', 'spinacia-oleracea']:
    split_train_val('data/data/' + i, 'dataset', i, 0.10)
