
import urllib.request
import time
import base64
import tempfile
import os
import imghdr

import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "util"
                                      # This will load the root logger

def generate_local_input_output_files(args):
    
    error = None

    # ..................................................................... url
    url = args['url']
    url = convert_url(url)
 
    if url is None:
        url = args['url']
        error = f'Unknown url : {url}'
        logger.error( error )
        return error
    else:
        args['url'] = url

    # .............................................................. input_path
    #
    # Does not use random name, to avoid leaking files in case of lost worker
    # By using uid, a retried task would generate the same input_path ...
    #
    uid = args['uid']
    input_path = args['input_path'] if 'input_path' in args else  get_temp_file(name=uid)
    
    if  os.path.exists(input_path):
        os.remove(input_path)

    try:
        if url : # pass empty url to process local image path
            input_path = download_url(url, input_path)
            args['input_path'] = input_path
    except Exception as e:
        error = str(e)
        input_path = None

    if input_path is None:
        error = f'Could not download image from {url}' + error
        logger.error(error)
        return error

    # ......................................................... output_path

    uid = args['uid']
    output_path = '/public/output-' + uid + get_ext(input_path, with_dot=True) 
    if  'output_path' in args:
        output_path = args['output_path'] 
    else:
        args['output_path'] = output_path
    
    # ............................................... invoke task with args
    
    args['cleanup-remove-files'] = [input_path, output_path]

    return error # assignment 


def convert_url(url,filter=None):
    schema = str_schema(url, filter=filter)
    if not schema:
        try:
            url = b642str(url)
        except Exception as e:
            url = None
            logger.error(str(e))
        schema = str_schema(url, filter=filter)

    url = url if schema else None
    logger.debug(f'convert_url return {url}')
    return url

def str_schema(s, filter=None):
    schema_del = '://'
    schema,_ = s.split(schema_del,1) if schema_del in s else (None, None)
    if filter:
        if schema not in filter:
            logger.warn(f'unsupported schema {schema} in {s}')
            schema = None # ignore unsupported schema 
    
    logger.debug(f'found schema {schema} in {s}')
    return schema
    
#def int_clip(i,min_n,max_n):
#    i = max(min( max_n, i), min_n)
#    return i

def str_ident(s, pad ):
    return ''.join(pad+line for line in s.splitlines(True)) 

def str2int(s):
    if s is None: 
        return None
    if not isinstance(s, str):
        s = str(s)
    i = None
    try: 
        i = int(s)
    except Exception as e:
        logger.warning(str(e))
    return i

def get_ext(path,with_dot=False):
    basename = os.path.basename(path)  # os independent
    ext = '.'.join(basename.split('.')[1:])   # <-- main part
    
    if ext is not None:
        ext = ext.lower()
        if with_dot:
            ext = '.' + ext
    return ext

def hash_str(s,len=12):
    digest = hashlib.sha256(bytes(s)).hexdigest(len//2)
    return digest

def get_temp_file(name=None,suffix=None):
    #_,tf = tempfile.mkstemp(suffix) 
    if  suffix is None:
        suffix = ''

    if  name is None:
        name = os.urandom(8).hex() + suffix
    
    tf = os.path.join(tempfile.gettempdir(), name)
    return tf

def download_url(url, local_path, ua=True):

    logger.info(f'download_url url:{url} >> local path:{local_path}')    

    if os.path.exists(local_path):
        logger.debug(f'local path exists ... using cached value') 
        os.utime(local_path, None)
        return local_path

    try:
        if not ua or ua is False:
            logger.debug(f'User-Agent as urllib')
            urllib.urlretrieve(url, local_path) # maybe blocked by some servers due to user-agent
        else: 
            ua = ua if isinstance(ua,str) else 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' 
            logger.debug(f'User-Agent as {ua}')

            headers={'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}

            request_=urllib.request.Request(url,None,headers) #The assembled request
            response = urllib.request.urlopen(request_)# store the response

            #create a new file and write the image
            f = open(local_path,'wb')
            f.write(response.read())
            f.close()
    
    except Exception as e:
        local_path = None
        logger.error(str(e))

    if local_path is not None:
        
        ext = imghdr.what(local_path)
        if  ext == 'jpeg': 
            ext = 'jpg'

        logger.debug(f'download_url: ext is {ext}')
        
        if ext:
            local_path_ext = local_path + '.' + ext
            os.rename( local_path, local_path_ext)
            local_path = local_path_ext
        logger.debug(f'urlretrieve url:{url} >> local path:{local_path}')
    
    return local_path

def str2b64(s_bytes):
    if isinstance(s_bytes, str):
        s_bytes = bytes(s_bytes,'utf-8')
    b64_bytes = base64.urlsafe_b64encode(s_bytes)
    b64_str = str(b64_bytes,'utf-8')
    logger.debug(f'str2b64({s_bytes}) => {b64_str} )')
    return b64_str

def b642str(b64_bytes):
    if isinstance(b64_bytes, str):
        b64_bytes = bytes(b64_bytes, 'utf-8')
    s_bytes = base64.urlsafe_b64decode( b64_bytes + b"===" )
    s_str = str(s_bytes,'utf-8')
    #s     = str(str_b, 'utf-8')
    logger.debug(f'b642str({b64_bytes}) => {s_str} )')
    return s_str

def now_ms():
    return int( time.time_ns() / (1000*1000) )

def since_ms( start_ms, finish_ms = None ):
    if finish_ms is None:
        finish_ms = now_ms()
    return finish_ms - start_ms
