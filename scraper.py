import requests
import re
from bs4 import BeautifulSoup

# TODO: grab image url
# TODO: grab post url
# TODO: make request to fetch posts
# TODO: parse comments 

if __name__ == "__main__":
    page = requests.get("https://www.reddit.com/r/aww/")
    soup = BeautifulSoup(page.text, "html.parser")


    # posts = soup.find_all(id=re.compile("^t3"))    
    '''print(posts[0])
    print(len(posts))'''

    posts = soup.find_all(class_=re.compile("^_1oQyIsiPHYt6nx7VOmd1sz"))

    for i in range(0, len(posts)):
        title = posts[i].find_all("h3")
        print(title)
        img_url = posts[i].find_all(alt="Post image")
        print(img_url)


