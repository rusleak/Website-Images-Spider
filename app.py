import os
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
import uuid  # For unique filenames


class ImageSpider:
    def __init__(self):
        self.home = os.getcwd()

    def grab_all_image_links(self, URL):
        try:
            valid_links = []
            url_protocol = URL.split('/')[0]
            url_html = requests.get(URL, timeout=10).text  # #1 Timeout for the request for safety
            Image_urls = re.findall(r'((http\:|https\:)?\/\/[^"\' ]*?\.(png|jpg))', url_html,
                                    flags=re.IGNORECASE | re.MULTILINE | re.UNICODE)
            for image in Image_urls:
                image_url = image[0]
                if not image_url.startswith(url_protocol):
                    image_url = url_protocol + image_url
                valid_links.append(image_url)
            print('Done')
        except requests.RequestException as graberror:  # #2 Error handler for request issues
            print('Grab error while getting links')
            print(graberror)
            return []
        return valid_links

    @staticmethod
    def extract_image_name(url):
        # #3 Generating unique filenames
        image_name = str(url).split('/')[-1]
        unique_name = f"{uuid.uuid4()}_{image_name}"  # Adding a unique identifier to prevent overwriting
        return unique_name

    @staticmethod
    def extract_site_name(url):
        sitename = str(url).split('/')[2]
        return sitename

    def saving_images(self, url):
        Image_links = self.grab_all_image_links(url)
        for link in Image_links:
            if not link.endswith(('.jpg', '.png')):  # #4 Check file extension before downloading
                continue
            try:
                raw_image = requests.get(link, stream=True, timeout=10).raw  # #5 Timeout for downloading images
                img = Image.open(raw_image)
                image_name = self.extract_image_name(link)
                img.save(image_name)
            except Exception as e:  # #6 Error handler for image download issues
                print(f"Failed to download {link}: {e}")

    def grab_all_links(self, url):
        links = [url]
        try:
            link_html = requests.get(url, timeout=10).text  # #7 Timeout for fetching all links
            all_links = BeautifulSoup(link_html, 'html.parser').findAll('a')
            for link in all_links:
                href = link.get('href')
                if href:
                    if href.startswith('http') or href.startswith('https'):
                        links.append(href)
        except requests.RequestException as e:  # #8 Error handler for all link requests
            print(f"Failed to grab links from {url}: {e}")
        return links

    def download_images(self):
        url = input('Enter URL with images : ')
        try:
            sitename = self.extract_site_name(url)
            print(f'Extracting from {sitename} ...')
            os.mkdir(sitename)
            os.chdir(sitename)
            print('\nShould we scan the entire site or just the home page?')
            option = int(input('1. Entire site\n2. Just this page\nOption : '))
            if option == 1:
                all_avaialble_links = set(self.grab_all_links(url))
            else:
                all_avaialble_links = [url]
            for link in all_avaialble_links:
                try:
                    print(link)
                    self.saving_images(link)
                except Exception as e:  # #9 Error handler for saving images
                    print(f"Error while saving images from {link}: {e}")

        except Exception as Error:
            print('Error occurred while grabbing site links')
            print(Error)

        finally:
            print('Scraping finished')
            os.chdir(self.home)


spider = ImageSpider()
spider.download_images()
