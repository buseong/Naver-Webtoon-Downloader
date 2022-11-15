from not_save import *
from time import time
import os


class Nt_Downloader:
    def __init__(self, url, location=...):
        self.url = url
        self.title = get_title(url)
        self.location = location

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if not isinstance(url, str):
            raise TypeError(f'{url} is not str, {url} is {type(url)}')
        else:
            self._url = url

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if not isinstance(location, (str, list)):
            raise TypeError(f'{location} is not correct types, {location} is {type(location)}')
        else:
            if location is ...:
                location = os.getcwd().replace('\\', '/') + '/' + self.title
                self.location = location
            elif os.path.isdir(location):
                self.location = location
            else:
                raise FileNotFoundError(f'Not found directory "{location}"')

    def DownloadNT(self):
        url = self._url
        location = self._location

        start_time = time()
        eposide_list = get_ep(url)
        img_download_cut(url=eposide_list, to_save_folder=location)
        end_time = time() - start_time
        print(end_time)


if __name__ == '__main__':
    url = 'https://comic.naver.com/webtoon/detail?titleId=784248&no=51&weekday=tue'
    downloader = Nt_Downloader(url)
    print(downloader.location)
    print(downloader.title)
