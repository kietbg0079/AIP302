from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tensorflow as tf
from PIL import Image
import shutil
import numpy as np
import os
import io
import urllib


ITEMS = {'rau muống' : 'Water morning glory leaves',
         'rau dền' : 'Amaranth leaves',
         'rau ngót' : 'Katuk leaves',
         'rau mồng tơi' : 'Malabar spinach leaves',
         'rau cải xoong' : 'Watercress leaves',
         'rau chân vịt' : 'Spinach leaves'}





driver = webdriver.Chrome('chromedriver.exe')


def crawl_plant_net(name):
    plantnet_url = f'https://identify.plantnet.org/prosea/species/{name}/data'

    driver.get(plantnet_url)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='__layout']/div/main/div/div[4]/div/nav/ul/li[2]/a"))))
    time.sleep(1)

    geo_public = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[1]')
    geo_private = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[2]')
    not_geo = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[3]')

    def extract_url(parent):
        url_list = []
        leafs = parent.find_elements(By.TAG_NAME, 'div')
        for leaf in leafs:
            url = leaf.find_element(By.TAG_NAME, 'a').get_attribute('href')
            url_list.append(url)

        return url_list

    time.sleep(5)
    return {'geo_public' : extract_url(geo_public),
            'geo_private' : extract_url(geo_private),
            'not_geo' : extract_url(not_geo)}


def download_img(url_lst, dest):
    if os.path.exists(dest):
        idx = len(os.listdir(dest))
    else:
        os.makedirs(dest, exist_ok=True)
        idx = 0

    for url in url_lst:
        try:
            file_name = os.path.join(dest, str(idx).zfill(5) + '.jpg')
            byte_img = urllib.request.urlopen(url).read()
            img = Image.open(io.BytesIO(byte_img))
            img.save(file_name)
            idx += 1
            print(f'Done {str(idx)}')
        except:
            print(url)



def rename_img_folder(path_folder):
    imgs = os.listdir(path_folder)
    idx = 0
    for img in imgs:
        img_path = os.path.join(path_folder, img)
        img_new_name = str(idx).zfill(5) + '.jpg'
        img_new_path = os.path.join(path_folder, img_new_name)
        if img[-3:] == 'jpg':
            try:
                os.rename(img_path, img_new_path)
                idx += 1
            except:
                idx += 1
                print(img)
        else:
            try:
                im = Image.open(img_path)
                rgb_im = im.convert("RGB")
                rgb_im.save(img_new_path)
                os.remove(img_path)
                idx += 1
            except:
                idx += 1
                print(img)
        print(f'done {idx}')


def clean_img(path, subfolder):
    num_skipped = 0
    for folder_name in subfolder:
        folder_path = os.path.join(path, folder_name)
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            try:
                fobj = open(fpath, "rb")
                is_jfif = tf.compat.as_bytes("JFIF") in fobj.peek(10)
            finally:
                fobj.close()

            if not is_jfif:
                num_skipped += 1
                # Delete corrupted image
                os.remove(fpath)

    print("Deleted %d images" % num_skipped)



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