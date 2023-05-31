from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from icrawler.builtin import GoogleImageCrawler, BaiduImageCrawler
import time
import tensorflow as tf
from PIL import Image
import shutil
import numpy as np
import os
import io
import urllib


#Crawl image from search image engines (Bing, Google, Baidu)
def crawl_icraw(keyword, num, dir, platform='google'):
    if platform == 'google':
        crawler = GoogleImageCrawler(storage={'root_dir': dir})
    # elif platform == 'bing':
    #     crawler = BingImageCrawler(storage={'root_dir': dir})
    elif platform == 'baidu':
        crawler = BaiduImageCrawler(storage={'root_dir': dir})
    else:
        print('fail platform')
    crawler.crawl(keyword=keyword, max_num=num)

#Merge multiple image folders to one folder (Work with icrawler module)
def merge_folder(path, dest_folder):
    folders = os.listdir(path)
    num = 0
    os.makedirs(dest_folder,exist_ok=True)

    for folder in folders:
        path_folder = os.path.join(path, folder)
        files = os.listdir(path_folder)

        for file in files:
            names = str(num).zfill(5) + '.' + file.split('.')[-1]
            shutil.copy(os.path.join(path_folder, file), os.path.join(dest_folder, names))
            num += 1


#Crawl plant images from plant net platform
def crawl_plant_net(name):
    def extract_url(parent):
        url_list = []
        leafs = parent.find_elements(By.TAG_NAME, 'div')
        for leaf in leafs:
            url = leaf.find_element(By.TAG_NAME, 'a').get_attribute('href')
            url_list.append(url)

        return url_list
    driver = webdriver.Chrome('chromedriver.exe')
    plantnet_url = f'https://identify.plantnet.org/the-plant-list/species/{name}/data'

    driver.get(plantnet_url)
    time.sleep(1)

    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='__layout']/div/main/div/div[4]/div/nav/ul/li[2]/a"))))
    time.sleep(1)

    lst_url = []
    geo_public = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[1]')
    lst_url += extract_url(geo_public)
    geo_private = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[2]')
    lst_url += extract_url(geo_private)
    try:
        not_geo = driver.find_element(By.XPATH, '/html/body/div/div/div/main/div/div[4]/div/div/div[2]/div[3]')
        lst_url += extract_url(not_geo)
    except:
        pass
    time.sleep(5)
    return lst_url

#Download image from url (Work with plant net crawl module)
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


#Rename all images in folder to 00000*.jpg format
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

#Delete corrupt image for training process
def clean_img(path):
    num_skipped = 0

    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
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


#Split images in folder into train and val set
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

def merge_plantnet_imagesearch(plant_folder, search_folder, dest_folder, ratio):
    plant_img = os.listdir(plant_folder)
    search_img = os.listdir(search_folder)

    plant_len = len(plant_img)
    search_len = plant_len * ratio

    for id in range(search_len):
        if id <= plant_len:
            shutil.copy(os.path.join(plant_folder, plant_img[id]), dest_folder)
        shutil.copy(os.path.join(search_folder, search_img[id]), dest_folder)