import audible, httpx, os, subprocess, asyncio, config, uvloop
from shutil import which
from tqdm import tqdm


async def _get_download_link(auth, asin, codec="LC_128_44100_stereo"):
    ''' (FileAuthenticator, str, str) --> str | None
    Gets the download url for the given book '''
    if auth.adp_token is None:
        raise Exception("No adp token present. Can't get download link.")

    try:
        content_url = ("https://cde-ta-g7g.amazon.com/FionaCDEServiceEngine/"
                       "FSDownloadContent")
        params = {
            'type': 'AUDI',
            'currentTransportMethod': 'WIFI',
            'key': asin,
            'codec': codec
        }            
        r = httpx.get(
            url=content_url,
            params=params,
            allow_redirects=False,
            auth=auth
        )

        link = r.headers['Location']
        tld = auth.locale.domain
        new_link = link.replace("cds.audible.com", f"cds.audible.{tld}")
        return new_link
    except Exception as e:
        print(f"Error: {e}")
        return


async def download_file(url):
    ''' (str) --> str
    Downloads the file from the given url and returns its path '''
    client = httpx.AsyncClient()
    async with client.stream("GET", url) as r:
        try:
            title = r.headers["Content-Disposition"].split("filename=")[1]
            length = int(r.headers["Content-Length"])
            if(not os.path.exists("tmp")):
                os.mkdir("tmp")
            filename = os.path.join(os.path.curdir, os.path.join("tmp", title))

            with open(filename, 'wb') as f:
                with tqdm(total=length, unit_scale=True, unit_divisor=1024, unit="B") as progress:
                    async for chunk in r.aiter_bytes():
                        f.write(chunk)
                        progress.update(len(chunk))

            print(f"File downloaded in {r.elapsed}")
            return filename
        except KeyError:
            return "Nothing downloaded"

async def ConvertToMp3(input_file, ab, out_file):
    ''' (str, str, str) --> str
    Uses ffmpeg (it has to be installed) to convert the file '''

    out_file += ".mp3"
    ffmpeg = which(config.ffmpeg)
    if not ffmpeg:
        raise Exception('ffmpeg not found!')
    cmd = [config.ffmpeg, "-activation_bytes", ab, "-i", input_file, out_file]
    subprocess.check_output(cmd, universal_newlines=True)
    os.remove(input_file)
    return out_file


async def main():
    #Name of the encrypted file with Amazon credentials
    Auth_file = "Credentials"
    
    #If it doesn't exists, it will be created
    if(not os.path.exists(Auth_file)):
        auth = audible.LoginAuthenticator(
            input("Username: "),
            input("Password: "),
            locale=input("Enter one of the following country" +
            "\ncode 'de', 'us', 'ca', 'uk', 'au', 'fr', 'jp', 'it', 'in' \nEnter: "),
            register=True)

        print("This information will be stored in an encrypted" +
        "\nfile so you don't have to insert them anymore.")
        config.credentials_pass = input("Enter a password for the encryption: ")
        auth.to_file(
            filename=Auth_file,
            password=config.credentials_pass,
            encryption="bytes")
    else:
        auth = audible.FileAuthenticator(
                filename=Auth_file,
                password=config.credentials_pass)
        
    client = audible.Client(auth)
    activation_bytes = auth.get_activation_bytes()

    #Checking download folder
    if(not os.path.exists(config.download_folder)):
        os.mkdir(config.download_folder)

    #Retrieving audiobooks
    library = client.get("library", num_results=1000)
    books = {book["title"]:book["asin"] for book in library["items"]}
    titles = [title for title in books.keys()]

    #Printing list of audiobooks
    for index, title in enumerate(titles):
        print(str(index + 1) + ") " + title)

    #Input of the book(s) that will be downloaded
    print("\nEnter the number of the book you want to download" +
        "\nIf you want to download multiple book enter the" +
        "\nnumber of the first and the last book separated" +
        "\nby a dash and without spaces between (i.e. 0-10)\n")
    book_range = input("Enter: ")
    book_range = book_range.split("-")

    if(len(book_range) == 2):
        first_book,last_book = book_range
        first_book = int(first_book) - 1
        last_book = int(last_book)
    elif(len(book_range) == 1):
        first_book = int(book_range[0]) - 1
        last_book = first_book + 1
    else:
        raise Exception("Invalid input!")
    
    #Downloading and converting books
    for index in range(first_book, last_book):
        asin = books[titles[index]]
        dl_link = await _get_download_link(auth, asin)
    
        if dl_link:
            print(f"Downloading now: {titles[index]}")
            status = await download_file(dl_link)
            print(f"Downloaded file: {status}")

            print("Now converting")
            status = await ConvertToMp3(status, activation_bytes, os.path.join(config.download_folder, titles[index].replace(" ", "")))
            print(f"Converted file: {status}")


if __name__ == "__main__":
    uvloop.install()
    loop = asyncio.run(main())