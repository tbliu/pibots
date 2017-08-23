import flickrapi
import os
import auth_keys as auth

def upload(img_path):
        api_key = auth.get_flickr_key()
        secret = auth.get_flickr_secret()
        flickr = flickrapi.FlickrAPI(api_key, secret)
        flickr.authenticate_via_browser(perms='write')
        flickr.upload(filename=img_path, \
            title=os.path.basename(img_path), \
            is_private=True)
