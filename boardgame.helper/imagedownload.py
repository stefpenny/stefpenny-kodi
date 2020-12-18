import requests
import os
import subprocess

def download(dir, image_url, newName):

    if not os.path.exists(dir):
        os.makedirs(dir)
    
    file_name = image_url.split('/')[-1]
    file_ext = file_name.split('.')[-1]

    if not os.path.exists(dir + newName + '.' + file_ext):
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            with open(dir + newName + '.' + file_ext, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            return

                