import os
import hashlib

from django.utils.text import get_valid_filename

def write_meta_information_to_file(meta_file, md5sum, chunk, chunks):
    """Writes meta info about the upload, i.d., md5sum, chunk number ...

    :param meta_file: file to write to
    :param md5sum: checksum of all uploaded chunks
    :param chunk: chunk number
    :param chunks: total chunk number
    """
    if chunk < (chunks - 1):
        upload_meta_data = "status=uploading&chunk=%s&chunks=%s&md5=%s" % (
            chunk,chunks,md5sum)
        try:
            meta_file.write(upload_meta_data)
        finally:
            meta_file.close()
    else:
        # last chunk
        path = meta_file.name
        meta_file.close()
        os.remove(path)

def clean_filename(filename):
    i = filename.rfind(".")
    if i != -1:
        filename = filename[0:i] + filename[i:].lower()
    return get_valid_filename(filename)

def get_or_create_file(chunk, dst):
    if chunk == 0:
        f = file(dst, 'wb')
    else:
        f = file(dst, 'ab')
    return f

def upload_with_checksum(request, dst, md5chunk, md5total, chunk, chunks):
    """Save application/octet-stream request to file.

    :param dst: the destination filepath
    :param chunk: the chunk number
    :param chunks: the total number of chunks
    :param md5chunk: md5sum of chunk
    :param md5total: md5sum of all currently sent chunks
    """
    buf_len = int(request.POST['chunk_size'])
    buf = request.body.read(buf_len)

    md5 = hashlib.md5()
    md5.update(buf)
    if md5.hexdigest() != md5chunk:
        raise BadRequest("Checksum error")

    f = get_or_create_file(chunk, dst)

    f.write(buf)
    f.close()
    
    f_meta = file(dst + '.meta', 'w') 
    write_meta_information_to_file(f_meta, md5total, chunk, chunks)

def upload_simple(request, dst, chunk=0):
    f = get_or_create_file(chunk, dst)

    file = request.FILES['file']
    for b in file:
        f.write(b)
    f.close()
    

if __name__ == '__main__':
    # in cgi environment
    import cgitb; cgitb.enable()
    CGIHandler().run(app)
