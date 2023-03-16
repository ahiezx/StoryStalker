from requests import get
from json import loads
from colorama import Fore, init, Style, Back
from time import strftime, localtime, time
from datetime import timedelta

import os, requests, subprocess

init()

sessionid = input("[I] Enter Sessionid : ")
user = input("[I] Enter Username : ")
print(Style.BRIGHT, end='\n')
print(f"    {Back.GREEN} Collected Data: {Back.RESET}")

def getid():

    headers = {
        "Host": "i.instagram.com",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US",
        "User-Agent": "Instagram 10.23.0 (iPhone11,2; iOS 12_1_4; ar_SA@calendar=gregorian; ar-SA; scale=3.00; gamut=wide; 1125x2001) AppleWebKit/420+",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": f"sessionid={sessionid}"

    }
    id = get(f"https://i.instagram.com/api/v1/users/{user}/usernameinfo/", headers=headers).json()
    return id["user"]["pk"]

def show():

    Headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-CSRFToken": "hjCdOJzq7llBK5SLOASWmLOl6brvTOeK",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "198387",
        "X-IG-WWW-Claim": "hmac.AR3bjFtFQokEUHdyITbgTbt-6_X7NNIdTmaQC-ZkDK__1V_A",
        "Origin": "https://www.instagram.com",
        "Alt-Used": "i.instagram.com",
        "Connection": "keep-alive",
        "Referer": "https://www.instagram.com/",
        "Cookie": f"sessionid={sessionid}",
        "Sec-Fetch-Dest": "empty",
    }
    req = get(f"https://i.instagram.com/api/v1/feed/user/{getid()}/story/", headers=Headers)
    response = loads(req.text)
    resp = response['reel']['items']
    return resp

data = show()


class Story:

    def __init__(self, data):

        self.data = data

        self.id = data['pk']
        self.is_reel_media = data['is_reel_media']
        # self.taken_at shows GMT time as string + (realtive time inside parenthesis)
        detla = int(time()) - data['taken_at']
        if detla < 60:
            self.taken_at = strftime("%Y-%m-%d %H:%M:%S", localtime(data['taken_at'])) + f" ({detla} seconds ago)"
        elif detla < 3600:
            self.taken_at = strftime("%Y-%m-%d %H:%M:%S", localtime(data['taken_at'])) + f" ({detla // 60} minutes ago)"
        elif detla < 86400:
            self.taken_at = strftime("%Y-%m-%d %H:%M:%S", localtime(data['taken_at'])) + f" ({detla // 3600} hours ago)"
        elif detla < 604800:
            self.taken_at = strftime("%Y-%m-%d %H:%M:%S", localtime(data['taken_at'])) + f" ({detla // 86400} days ago)"
        
        expiringdelta = data['expiring_at'] - int(time())
        if expiringdelta < 60:
            self.expiring_at = f"{expiringdelta} seconds"
        elif expiringdelta < 3600:
            self.expiring_at = f"{expiringdelta // 60} minutes"
        elif expiringdelta < 86400:
            self.expiring_at = f"{expiringdelta // 3600} hours"
        elif expiringdelta < 604800:
            self.expiring_at = f"{expiringdelta // 86400} days"
        self.username = data['user']['username']
        self.full_name = data['user']['full_name']
        self.profile_pic = data['user']['profile_pic_url']
        self.is_private = data['user']['is_private']
        if data['media_type'] == 1:
            self.media_type = 'Image'
        elif data['media_type'] == 2:
            self.media_type = 'Video'
        else:
            self.media_type = 'Unknown'
        self.original_width = data['original_width']
        self.original_height = data['original_height']
        if 'video_versions' in data:
            self.media_url = data['video_versions'][0]['url']
        else:
            self.media_url = data['image_versions2']['candidates'][0]['url']
        self.product_type = data['product_type']
        if 'accessibility_caption' in data:
            self.accessibility_caption = data['accessibility_caption']
        else:
            self.accessibility_caption = None
        
    def open_media(self):
        response = requests.get(self.media_url)

        if response.status_code == 200:
            filename = os.path.basename(self.media_url.split('?')[0])
            try:
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                # remove the file

            except OSError as e:
                print(f"Error creating file: {e}")
                return

            try:
                os.startfile(filename)  # for Windows OS
                # alternatively, you can use the following code for cross-platform support:
                # import subprocess
                # subprocess.run(["open", filename])  # for macOS/Linux
            except OSError as e:
                print(f"Error opening file: {e}")

        else:
            print(f"Error: {response.status_code}")
    
    def remove_media(self):

        # close the file after open_media() is called
        
        filename = os.path.basename(self.media_url.split('?')[0])
        try:
            os.remove(filename)
        except OSError as e:
            print(f"Error removing file: {e}")

stories = []

for i in data:
    stories.append(Story(i))

print(f"\n    {Back.RED} Total Stories : {len(stories)} {Back.RESET}")

for story in stories:
    print(f"""
    {Fore.RED}Taken At : {story.taken_at}{Style.RESET_ALL}

    ID : {story.id}
    Is Reel Media : {story.is_reel_media}
    Expiring In : {story.expiring_at}
    Username : {story.username}
    Full Name : {story.full_name}
    Profile Pic : {story.profile_pic}
    Is Private : {story.is_private}
    Media Type : {Fore.YELLOW}{story.media_type}{Style.RESET_ALL}
    Original Width : {story.original_width}
    Original Height : {story.original_height}
    Media URL : {Fore.BLUE}{story.media_url}{Style.RESET_ALL}
    Product Type : {story.product_type}
    Accessibility Caption : {Fore.CYAN}{story.accessibility_caption}{Style.RESET_ALL}
    """)
    print(Fore.GREEN + "----------------------------------------" + Style.RESET_ALL)

    question = input("[I] Do you want to open this story? (y/n) ")

    if(question.lower() == "y" or question == ""):
        story.open_media()
    input("[I] Press enter to go to next story")
    story.remove_media()
    print(Fore.GREEN + "----------------------------------------" + Style.RESET_ALL)

print(f'{Fore.RED}No more stories to show{Style.RESET_ALL}')