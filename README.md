# Audible-Downloader

This script allows you to download, decrypt, and convert your audiobooks from Audible. Simply enter the answers to the questions in the console (i.e. username, password, country code...) and you will be presented with a list, select the number which correspond to the book you want to download and press enter. 

If you want to download multiple books you have to type the number corresponding to the first book and the one corresponding to the last book. At this moment you can select only a book or a range of books, if you want to download for example the 10th book and the 51st one you have to run this script twice. Then just wait for the audiobook(s) to be downloaded, decrypted and converted.

# Prerequisites

I assume you have already installed python (which is preinstalled in Linux and Mac OS) and ffmpeg. Otherwise these are the official download sites: [python](https://www.python.org/downloads/), [ffmpeg](https://ffmpeg.org/download.html) 

For any problems, please google first

For any Mac OS related question I probably can't answer since I have no Apple devices

# Installation
It's the same for Windows, Linux and Mac OS
```bash
git clone "https://github.com/doGior/Audible-Downloader"
cd Audible-Downloader
pip install -r requirements.txt
```

# Note

To change download folder, encryption password and to ffmpeg path (this one only in case of problem) you can modify the config.py file

# Anti-Piracy Notice

Note that this project does NOT ‘crack’ the DRM. It simply allows the user to use their own encryption key (fetched from Audible servers) to decrypt the audiobook in the same manner that the official audiobook playing software does.

Please only use this application for gaining full access to your own audiobooks for archiving/conversion/convenience. DeDRMed audiobooks should not be uploaded to open servers, torrents, or other methods of mass distribution. No help will be given to people doing such things. Authors, retailers, and publishers all need to make a living, so that they can continue to produce audiobooks for us to hear, and enjoy. Don’t be a parasite.
