# Amazon-asin-uspto-parser


- Amazon-asin-uspto-parser is a desktop app useful for parser data from amazon each country site using ASIN.
- Also, can check the registration of brand trademarks.

## Requirements

```shell
pipreqs . --encoding UTF-8
pip install -r requirements.txt
```

- pin requirements
```shell
chromedriver_autoinstaller==0.6.2
selenium==4.5.0
flet==0.7.4

```

## Dev UI hot reload

```shell
flet run main.py -d
```

## Package

```shell
pip install pyinstaller
pip install pillow
flet pack main.py --icon ".\assets\amazon.png" 
```

## Pin Point - Hide console in pyinstaller

- Hide console interface with package using pyinstaller.
- Necessary!!! selenium==4.5.0 , other version not work.
- Comes with the following code.

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService  # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_service = ChromeService('chromedriver')
chrome_service.creationflags = CREATE_NO_WINDOW
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
```

## Fix Chrome v115 with chromedriver_autoinstaller

- Chrome v115.0.5790.110 
- chromedriver_autoinstaller == 0.6.2
- locate to source utils.py

### Point 1

```python
def get_matched_chromedriver_version(chrome_version, no_ssl=False):
    # Newer versions of chrome use the CfT publishing system
    if chrome_version >= "115":
        version_url = "googlechromelabs.github.io/chrome-for-testing/known-good-versions.json"
        version_url = "http://" + version_url if no_ssl else "https://" + version_url
        good_version_list = json.load(urllib.request.urlopen(version_url))
        compare_version = chrome_version.rsplit('.', 1)[0]
        for good_version in good_version_list["versions"]:
            # if good_version["version"] == chrome_version:
            #     return chrome_version
            if good_version["version"].startswith(compare_version):
                return good_version["version"]
    # check old versions of chrome using the old system
    else:
        version_url = "chromedriver.storage.googleapis.com"
        version_url = "http://" + version_url if no_ssl else "https://" + version_url
        doc = urllib.request.urlopen(version_url).read()
        root = elemTree.fromstring(doc)
        for k in root.iter("{http://doc.s3.amazonaws.com/2006-03-01}Key"):
            if k.text.find(get_major_version(chrome_version) + ".") == 0:
                return k.text.split("/")[0]
    return
```

### Point 2

```python
def get_chrome_version():
    if platform == "linux":
    elif platform == "mac":
    elif platform == "win":
        # check both of Program Files and Program Files (x86).
        # if the version isn't found on both of them, version is an empty string.

        # dirs = [f.name for f in os.scandir("C:\\Program Files\\Google\\Chrome\\Application") if f.is_dir() and re.match("^[0-9.]+$", f.name)]
        # if dirs:
        #     version = max(dirs)
        # else:
        #     dirs = [f.name for f in os.scandir("C:\\Program Files (x86)\\Google\\Chrome\\Application") if f.is_dir() and re.match("^[0-9.]+$", f.name)]
        #     version = max(dirs) if dirs else ''

        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application"

        try:
            dirs = [f.name for f in os.scandir(chrome_path) if f.is_dir() and re.match("^[0-9.]+$", f.name)]
            version = max(dirs) if dirs else ''
        except FileNotFoundError:
            version = ''

    else:
        return
    return version
```

## Could do better

1. Minimal exception handling.
2. Multi-threading/multi-process let chrome tabs parallel processing.
3. Perfect UI gen logic.