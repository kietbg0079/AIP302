import shutil

from module import crawl_icraw, merge_folder, clean_img, crawl_plant_net, download_img, rename_img_folder


ITEMS = {'rau-muong' : ['Water morning glory leaves', 'Ipomoea aquatica Forssk.'],
         'rau-den' : ['Amaranth leaves', 'Amaranthus tricolor L.'],
         'rau-ngot' : ['Katuk leaves', 'Sauropus androgynus (L.) Merr.'],
         'rau-mong-toi' : ['Malabar spinach leaves', 'Basella alba L.'],
         'rau-cai-xoong' : ['Watercress leaves', 'Nasturtium officinale R.Br.'],
         'rau-chan-vit' : ['Spinach leaves', 'Spinacia oleracea L.']}



#Icrawler module's Code sample
search_engine = ['google', 'baidu']
num_img = 100
dest_folder = 'dataset/engine'

for key, val in ITEMS.items():
    #using common name
    vi_name = key
    en_name = val[0]

    for engine in search_engine:
        crawl_icraw(vi_name, num_img, f'{dest_folder}/{key}/vi/{engine}', platform=engine)
        crawl_icraw(en_name, num_img, f'{dest_folder}/{key}/en/{engine}', platform=engine)

    merge_folder(f'{dest_folder}/{key}/vi', f'{dest_folder}/{key}/temp1')
    merge_folder(f'{dest_folder}/{key}/en', f'{dest_folder}/{key}/temp2')

    shutil.rmtree(f'{dest_folder}/{key}/vi')
    shutil.rmtree(f'{dest_folder}/{key}/en')

    merge_folder(f'{dest_folder}/{key}', f'{dest_folder}/{key}_final')

    clean_img(f'{dest_folder}/{key}_final')
    shutil.rmtree(f'{dest_folder}/{key}')



#Plant net crawler code sample

for key, val in ITEMS.items():
    plant_name = val[1]  #using scientific name
    dest_folder = f'dataset/plantnet/{key}'

    img_urls = crawl_plant_net(plant_name)
    download_img(img_urls, dest_folder)
    rename_img_folder(dest_folder)
    clean_img(dest_folder)

