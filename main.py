import pathlib, audible, httpx, os
from tqdm import tqdm


def _get_download_link(auth, asin, codec="LC_128_44100_stereo"):
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

        # prepare link
        # see https://github.com/mkb79/Audible/issues/3#issuecomment-518099852
        link = r.headers['Location']
        tld = auth.locale.domain
        new_link = link.replace("cds.audible.com", f"cds.audible.{tld}")
        return new_link
    except Exception as e:
        print(f"Error: {e}")
        return


def download_file(url):
    with httpx.stream("GET", url) as r:
        try:
            title = r.headers["Content-Disposition"].split("filename=")[1]
            length = int(r.headers["Content-Length"])
            if(not os.path.exists("audiobooks")):
                os.mkdir("audiobooks")
            filename = pathlib.Path.cwd() / "audiobooks" / title

            with open(filename, 'wb') as f:
                with tqdm(total=length, unit_scale=True, unit_divisor=1024, unit="B") as progress:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
                        progress.update(len(chunk))

            print(f"File downloaded in {r.elapsed}")
            return filename
        except KeyError:
            return "Nothing downloaded"


if __name__ == "__main__":
    Auth_file = "Credentials"
    
    if(not os.path.exists(Auth_file)):
        auth = audible.LoginAuthenticator(
            input("Username: "),
            input("Password: "),
            locale="it",
            register=True)

        auth.to_file(
            filename=Auth_file,
            password="1234",
            encryption="bytes")
        
    auth = audible.FileAuthenticator(
            filename=Auth_file,
            password="1234")
        
    client = audible.Client(auth)

    library = client.get("library", num_results=1000)
    books = {book["title"]:book["asin"] for book in library["items"]}
    titles = [title for title in books.keys()]

    for index, title in enumerate(titles):
        print(str(index + 1) + ") " + title)

    print("\nEnter the number of the book you want to download"+
        "\nIf you want to download multiple book enter the "+
        "\nnumber of the first and the last book separated by a"+
        "\n dash and without spaces between (i.e. 0-10)\n")
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

    for index in range(first_book, last_book):
        asin = books[titles[index]]
        dl_link = _get_download_link(auth, asin)

        if dl_link:
            print(f"Download link now: {titles[index]}")
            status = download_file(dl_link)
            print(f"Downloaded file: {status}")