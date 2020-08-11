#!/usr/bin/env python3
#
# alert_notify.py version 0.1
#
# Copyright (c) 2020 scudre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from sys import argv, exit
import os.path
import requests
import logging

# ===========================================
# Setup Instructions
# ===========================================
# Step 1: Blue Iris Configuration
#
# 1) Open settings for camera you want to receive notifications from
# 2) On Trigger tab: Check 'Capture an alert list image', and 'Store alert images as hi-res files'
#   a) This setting is required for the &ALERT_PATH macro to work.  Without it you'll get a notification without the alert image
# 3) On Alerts tab: Click 'On alert...' button
# 4) In Action set window press the + and choose 'Run a program or script'
#   a) For File: Choose this python script
#   b) For Parameters set it exactly to: "%X %x" "&CAM" "&ALERT_PATH" 
# 5) Repeat for each camera you want to receive notifications from
#
# Step 2: Required Script Configuration in alert_notify.py
#
# 1) P_USER, P_TOKEN: Pushover User Key, and API Token/Key
# 2) ALERT_DIR: Directory where alert images are saved.  
#   a) You can find this path in Blue Iris Settings --> 'Clips and archiving' tab --> 
#      Clicking on 'Alerts' in the Folders section

# ===========================================
# Script Configuration
# ===========================================

# Pushover User Key, and API Token/Key
P_USER = ''
P_TOKEN = ''

# Blue Iris Alert Directory
ALERT_DIR = 'C:\\BlueIris\\Alerts'

# Logging level, it can be set to DEBUG if you're troubleshooting the script
LOG_LEVEL = logging.WARNING

#============================================

def notify(timestamp, cam_name, image_fd=None):
    files = {}
    if image_fd:
        files = {
            'attachment': ('image.jpg', image_fd, 'images/jpeg')
        }
        
    data = {
        'token': P_TOKEN,
        'user': P_USER,
        'message': '{} - Motion Detected at {}'.format(cam_name, timestamp),
    }
    
    pushover_uri = 'https://api.pushover.net/1/messages.json'
    response = requests.post(pushover_uri, data=data, files=files)
    if response.status_code == 200:
        logging.debug('Sending complete')
    else:
        err_list = response.json().get('errors')
        status_code = response.status_code
        logging.error('Error sending pushover notification HTTP %s: %s',
                      status_code, ', '.join(err_list))
                      
def main():
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        logging.basicConfig(filename=os.path.join(script_dir, 'alert_notify.log'),
                            level=LOG_LEVEL,
                            format='%(asctime)s [%(levelname)s] %(message)s')
        logging.info('Executing {}...'.format(__file__))
        
        logging.debug('args: {}'.format(argv))
        try:
            _, timestamp, cam_name, alert_file = argv
            with open(os.path.join(ALERT_DIR, alert_file), 'rb') as fd:
                notify(timestamp, cam_name, fd)
        except IOError:
            logging.warning('Alert image {} not found.'.format(os.path.join(ALERT_DIR, alert_file)))
            notify(timestamp, cam_name)
    except Exception:
        logging.exception('Unexpected error:')
 
    return 0

    
if __name__ == "__main__":
    exit(main())
