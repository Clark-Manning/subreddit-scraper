import requests
import re
from bs4 import BeautifulSoup
import argparse
import os, glob
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

headers = {'User-Agent':'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
reddit_url = "https://www.reddit.com"

# TODO: parse comments; put each comment into a list; write entire list to csv

def get_soup(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, "lxml")

def find_comments(post_soup):
    for item in post_soup.select("._1qeIAgB0cPwnLhDF9XSiJM"):
        comment = item.get_text()

def formulate_post(item):
    videos = item.find_all("source")

    post_images = item.find_all("img", alt="Post image")

    if not post_images and not videos:  
        # TODO: potential repost. Figure out how to handle
        # print(item)
        return

    post_data = {"votes": None, "title": None, "commentCount": None, "url": None, "imageUrl": None, "videoUrl": None}
    
    #TODO: fix vote parsing logic
    post_votes = item.select("._1rZYMD_4xY3gRcSS3p8ODO")[0].get_text()
    post_data["votes"] = post_votes

    post_title = item.select("._eYtD2XCVieq6emjKBH3m")[0].get_text()
    post_data["title"] = post_title

    # TODO: parse out "comments" from comment count text
    post_comment_count = item.select(".FHCV02u6Cp2zYL0fhQPsO")[0].get_text()
    post_data["commentCount"] = post_comment_count

    post_slug = item.select("._2INHSNB8V5eaWp4P0rY_mE a[href]")[0]["href"]
    post_url = reddit_url + post_slug
    post_data["url"] = post_url 

    if post_images:
        post_image = post_images[0]["src"]
        post_data["imageUrl"] = post_image

    if videos:
        post_video = videos[0]["src"]
        post_data["videoUrl"] = post_video

    post_soup = get_soup(post_url)
    
    find_comments(post_soup)

    return post_data

def get_post_data(soup):
    processes = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for item in soup.select(".Post"):
            processes.append(executor.submit(formulate_post, item))

    for task in as_completed(processes):
        post = task.result()
        if post:
            yield post

def get_all_post_data(current_url):
    start_time = time()
    all_post_data = []
    # use get_post_data until have specified amount of data or there is no next link
    while len(all_post_data) < 10 and current_url:
        soup = get_soup(current_url)
        all_post_data.extend(get_post_data(soup))
        next_link_list = soup.find_all("link", rel="next")
        if len(next_link_list) > 0:
            current_url = next_link_list[0]["href"]
        else:
            current_url = None
        print(f'Time taken loop: {time() - start_time}')
    print(f'Time taken get_all_post_data: {time() - start_time}')
    return all_post_data

def get_all_values_by_key(all_post_data, keyname):
    values = []
    for post_data in all_post_data:
        if not post_data.get(keyname):
            continue
        else:
            values.append(post_data.get(keyname))
    return values

def download_img(url, pathname):
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get("Content-Length", 0))
    
    filename = os.path.join(pathname, url.split("/")[-1].split("?")[0])

    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            f.write(data)
            progress.update(len(data))

def download_all_imgs(urls, pathname):
    # downloads the img file and puts it in a folder
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    

    for file in os.scandir(pathname):
        os.remove(file.path)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            executor.submit(download_img, url, pathname)
        

def write_post_data_to_csv(all_post_data):
    _file = open("PostData.csv", "w")
    # loop all_post_data and write each data to file
    _file.write(",".join(all_post_data[0].keys()) + "\n")
    for post_data in all_post_data:
        post_values = []
        # add "" to escape existing commas for csv interpretation
        for value in post_data.values():
            post_values.append("\"" + (value or "") + "\"")
        _file.write(",".join(post_values) + "\n")
    _file.close()

if __name__ == "__main__":
    start_time = time()
    # command line argument accepts subreddit command in form "/r/subreddit/"
    parser = argparse.ArgumentParser(description="Specify the subreddit you want to scrape")
    parser.add_argument("subreddit", nargs="?", default="/r/aww/", type=str, help="/r/subreddit/")
    args = parser.parse_args()
    subreddit = args.subreddit
    subreddit_url = reddit_url + subreddit
    all_post_data = get_all_post_data(subreddit_url)
    write_post_data_to_csv(all_post_data)
    image_urls = get_all_values_by_key(all_post_data, "imageUrl")
    download_all_imgs(image_urls, "subreddit-images")
    video_urls = get_all_values_by_key(all_post_data, "videoUrl")
    download_all_imgs(video_urls, "subreddit-videos")
    # requests.exceptions.InvalidSchema: No connection adaptors were found for the list image_urls
    print(f'Time taken: {time() - start_time}')
    
