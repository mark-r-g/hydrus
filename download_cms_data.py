from io import BytesIO
from hashlib import sha1
from os.path import isdir, join, abspath, dirname
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.request import urlopen

import hydrus.constants as c


class WrongSha1Error(Exception): pass


URL = (
    # "https://www.qualitynet.org/dcs/BlobServer",
    "http://www.qualitynet.org/dcs/BlobServer"
    "?blobkey=id"
    "&blobnocache=true"
    "&blobwhere="
    "{blob}"
    "&blobheader=multipart%2Foctet-stream"
    "&blobheadername1=Content-Disposition"
    "&blobheadervalue1=attachment%3Bfilename%3D"
    "{filename}"
    "&blobcol=urldata"
    "&blobtable=MungoBlobs"
    )

DEST = c.IN if isdir(c.IN) else '.'


def download_cms_data(blob, filename, exp_hash):
    url = URL.format(blob=blob, filename=filename)
    print('Downloading', filename)
    try:
        with urlopen(url) as remote:
            with BytesIO() as bio:
                bio.write(remote.read())
                bio.seek(0)
                hash = sha1(bio.read()).hexdigest()
                if hash == exp_hash:
                    print('Extracting to', abspath(DEST))
                    with ZipFile(bio, compression=ZIP_DEFLATED) as z:
                        z.extractall(path=DEST)
                else:
                    raise WrongSha1Error("Incorrect SHA1 hash.")
    except Exception as e:
        print('Download failed:', e)
    else:
        print('Download complete.', end='\n\n')


if __name__ == '__main__':
    download_cms_data(
        1228890641889,
        'SAS_All_Data_Dec2016_suppressd.zip',
        '8b9a23afd3e9b88427aa9932557d17cd0b4be640',
        )
    download_cms_data(
        1228890620679,
        'SAS_Data-Input_Oct2016.zip',
        '62ab0e94811842f3212196e203cd95374fbb10d4',
        )
