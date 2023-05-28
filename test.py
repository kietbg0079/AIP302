from module import crawl_icraw, merge_folder, clean_img, crawl_plant_net, download_img, rename_img_folder


#Icrawler module's Code sample
key = 'dog'
search_engine = ['google', 'baidu']
num_img = 50
dest_folder = 'test/dog'

for engine in search_engine:
    crawl_icraw(key, num_img, f'{dest_folder}/{engine}', platform=engine)

merge_folder(dest_folder, f'{dest_folder}/merge')
clean_img(f'{dest_folder}/merge')




#Plant net crawler code sample
plant_name = 'Sauropus androgynus (L.) Merr.'
dest_folder = 'test/plant/Sauropus androgynus'

img_urls = crawl_plant_net(plant_name)
download_img(img_urls, dest_folder)
rename_img_folder(dest_folder)
clean_img(dest_folder)