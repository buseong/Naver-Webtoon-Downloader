import os
import re
from io import BytesIO
from random import randint
from time import time
from urllib import request

import numpy as np
import psutil
import requests as rq
from PIL import Image
from bs4 import BeautifulSoup

headers: list[list[(str, str)]] = [
               [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')],
               [('User-Agent', '"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"')],
               [('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')],
               [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0')],
               [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ')],
               [('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ')],
               ]


def get_soup(url: str, usage: str):
    pprint(f'{usage} : {url}')
    opener = request.build_opener()
    header = headers[randint(0, len(headers) - 1)]
    opener.addheaders = header
    request.install_opener(opener)
    with request.urlopen(url) as html:
        soup = BeautifulSoup(html.read(), "html.parser")
    return soup


def pprint(text):
    memory_info = psutil.Process().memory_info()
    rss = memory_info.rss / 2 ** 20
    vms = memory_info.vms / 2 ** 20
    print(f"RSS: {rss: 10.6f} MB, VMS: {vms: 10.6f} | {text}")


def img_add(img_arr: list):
    # start_time = time()
    new_img = None
    # img_num = 0
    # img_size = 0
    # point = 5

    for i in range(len(img_arr) - 1):
        header = {'User-Agent': headers[randint(0, len(headers) - 1)][0][1]}
        # if i == 0:
        #     img_size = 0
        # start = time()
        # img_num += 1
        if i == 0:
            first_img = Image.open(BytesIO(rq.get(img_arr[i], headers=header).content))
        else:
            first_img = new_img
        second_img = Image.open(BytesIO(rq.get(img_arr[i + 1], headers=header).content))
        first_img_size = first_img.size
        second_img_size = second_img.size
        new_img = Image.new('RGB', (first_img_size[0], first_img_size[1] + (second_img_size[1])), (255, 255, 255))
        new_img.paste(first_img, (0, 0))
        new_img.paste(second_img, (0, first_img_size[1]))
        # new_img_y = new_img.size[1]
        # plus_img_size = new_img_y - img_size
        # total_img_size = (new_img.size[0] * new_img_y) / 10
        # if img_num < 10:
        #     img_num = str('0' + str(img_num))
        # pprint(f"{img_num} | {float(time() - start) : 10.{point}f} | {float(time() - start_time) : 10.{point}f} | "
        #        f"{int(total_img_size)} | {float(total_img_size)/1000000 : 10.{point}f} | {int(new_img_y)} | +{int(plus_img_size)}")
        # img_size = new_img.size[1]
        # img_num = int(img_num)
    return new_img


def get_ep(url: str):
    wt_id = re.findall('titleId=([0-9]+)', url)[0]
    wt_url = 'https://comic.naver.com/webtoon/list?titleId=' + str(wt_id)
    ep = re.findall('no=([0-9]+)', str(get_soup(wt_url, 'get ep').select('.title')[1]).replace('\n', ''))[0]
    ep_list = [f'https://comic.naver.com/webtoon/detail?titleId={wt_id}&no={i + 1}' for i in range(int(ep))]
    return ep_list


def get_title(url: str):
    title = re.findall('>(.+?)</', str(get_soup(url, 'get title').select('.title')[0]))[0]
    return title


def file_delete(address):
    if os.path.exists(address):
        for file in os.scandir(address):
            os.remove(file.path)
    else:
        pprint('File in fold is not exists')
        os.makedirs(address)
        file_delete(address)


def file_make(address):
    if not os.path.exists(address):
        if '.' in address.split('/')[-1]:
            address = '/'.join(address.split('/')[:-1])
        os.makedirs(address)
    else:
        pprint('already exists')


def img_download_cut(url: list, to_save_folder: str = 'toon', white_space: int = 1):
    if to_save_folder[-1] != '/':
        to_save_folder = to_save_folder + '/'
    episode = 1
    for i in url:
        folder = to_save_folder + str(episode)
        file_make(folder)
        wt_ = re.findall('src="(.+?)"', str(get_soup(i, 'get img').select('.wt_viewer')[0]).replace('\n', ''))
        image = img_add(wt_)
        img_num = 1
        cut_img_y = 0
        count = 0
        pix = np.array(image)
        for y in range(image.size[1]):
            judge = pix[y][np.arange(0, image.size[0])]
            if np.max(judge) == np.min(judge) == 255 or \
                    np.max(judge) == np.min(judge) == 0:
                count += 1
            if count == white_space:
                cut_img = image.crop((0, cut_img_y, image.size[0], y))
                if int(cut_img.size[1]) <= white_space:
                    img_num = img_num - 1
                else:
                    cut_img.save(f'{folder}/{img_num}.jpg')
                cut_img_y = y
                count = 0
                img_num += 1
        del pix
        episode += 1


if __name__ == '__main__':
    url = 'https://comic.naver.com/webtoon/detail?titleId=784248&no=51&weekday=tue'
    start_time = time()
    img_download_cut(url=get_ep(url), to_save_folder=get_title(url))
    pprint(time() - start_time)
