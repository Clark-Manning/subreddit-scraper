import requests
import re
from bs4 import BeautifulSoup

headers = {'User-Agent':'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
reddit_url = "https://www.reddit.com"

# TODO: fetch images from all_post_data and store in folder
# TODO: fetch videos from all_post_data and store in folder
# TODO: parse comments
# TODO: make paginated requests for posts and comments 
# TODO: handle reposts
# TODO: investigate video content; unexpected value appearing in videoUrl

def get_soup(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, "lxml")

def find_comments(post_soup):
    for item in post_soup.select("._1qeIAgB0cPwnLhDF9XSiJM"):
        print(item.get_text())

def get_all_post_data(soup):
    all_post_data = []
    for item in soup.select(".Post"):
        try:
            videos = item.find_all("source")

            post_images = item.find_all("img", alt="Post image")

            if not post_images and not videos:  
                # TODO: potential repost. Figure out how to handle
                # print(item)
                continue

            post_data = {"votes": None, "title": None, "commentCount": None, "url": None, "imageUrl": None, "videoUrl": None}
            
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

            all_post_data.append(post_data)

        except Exception as e:
            print(e)
    return all_post_data

def write_post_data_to_csv(all_post_data):
    _file = open("PostData.csv", "w")
    # loop all_post_data and write each data to file
    _file.write(",".join(all_post_data[0].keys()) + "\n")
    for post_data in all_post_data:
        post_values = []
        # add "" to escape existing commas for csv interpretation
        for value in post_data.values():
            post_values.append("\"" + value + "\"")
        _file.write(",".join(post_values) + "\n")
    _file.close()

if __name__ == "__main__":
    # TODO: accept subreddit as a command line argument
    subbreddit = "/r/aww/"
    subreddit_url = reddit_url + subbreddit
    soup = get_soup(subreddit_url)
    all_post_data = get_all_post_data(soup)
    write_post_data_to_csv(all_post_data)


    print(all_post_data)