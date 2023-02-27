from multiprocessing.dummy import Pool as ThreadPool
import argparse

import os, sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from grid import Grid
from util import *

import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "mosaic"
                                      # This will load the root logger

def mosaic(ops, progress_callback ):

    default_ops = {
        'multi'   : 0.014,
        'diamond' : True,
        'color'   : 1,
        'working_res' : 0,
        'enlarge' : 2000,
        'pool'    : 1
    }
    
    ops = dict_set_defaults( ops, default_ops )

    logger.info(f'ops:{ops}')
    
    url = ops['url']
    url = convert_url(url)

    if url is None:
        url = ops['url']
        logger.error(f'Unknown url : {url}' )
        return -1, None

    local_path  = ops['local_path' ] if 'local_path' in ops else get_temp_file()
    output_path = ops['output_path'] if 'output_path' in ops else None

    try:
        if url : # pass empty url to process local image path
            local_path = download_url(url, local_path)
    except Exception as e:
        logger.error(str(e))
        # @todo : handle errors somehow...
        local_path = None

    if local_path is None:
        logger.error(f'Could not download image from {url}' )
        return -1, None

    if not output_path:
        output_path = '/public/output-' + ops['uid'] + get_ext(local_path, with_dot=True)

    multi       = ops['multi']
    diamond     = ops['diamond']
    color       = ops['color']
    working_res = ops['working_res']
    enlarge     = ops['enlarge']
    pool        = ops['pool']

    grid = Grid(local_path, pix=0, pix_multi=multi, diamond=diamond,
                colorful=color, working_res=working_res, enlarge=enlarge,
                progress_callback=progress_callback)

    total_updates = 20
    step_size = clamp_int(int(math.ceil(grid.rows/(1.0*total_updates))), 1, 10000)

    ending_index = step_size*total_updates
    # diff = grid.rows - step_size*total_updates

    todos = []
    for i in range(total_updates+1):
        s_index = step_size*i
        e_index = s_index + step_size
        todos.append((s_index, e_index, output_path))

        is_continue = False if e_index >= grid.rows else True
        if not is_continue:
            break
        
    # double check that we are not doing double work
    try:
        pool = ThreadPool(10)
        pool.map(grid.grid_start_end_thread, todos)
        pool.close()
        pool.join()
    except (KeyboardInterrupt, SystemExit):
        pool.terminate()

    grid.save(output_path)

    # Cleanup local copy
    if local_path:
        if  os.path.isfile(local_path):
            os.remove(local_path)
            logger.info(f'local file removed :{local_path}')
        else:
            logger.warning( f'local file does not exist :{local_path}')

    return 0, output_path


def main():
    parser = argparse.ArgumentParser(description='Mosaic photos')

    parser.add_argument('urls', metavar='N', type=str, nargs='+',
                        help='Url photos')
    parser.add_argument("-d", "--diamond", default=False, action='store_true',
                        help="Use diamond grid instead of squares")
    parser.add_argument("-c", "--color", default=False,
                        action='store', choices=["0", "1", "2"],
                        help="Specify color values")
    parser.add_argument("-a", "--analogous", default=False, action='store_true',
                        help="Use analogous color")
    parser.add_argument("-r", "--working_res", default=0, required=False, type=int,
                        help="Resolution to sample from")
    parser.add_argument("-e", "--enlarge", default=0, required=False, type=int,
                        help="Resolution to draw")
    parser.add_argument("-m", "--multi", default=.014, type=float)
    parser.add_argument("-p", "--pool", default=1, type=int)
    parser.add_argument("-o", "--out", default="/tmp/out.jpg", type=str, 
                        help="output file - default is /tmp/out.jpg")
    parser.add_argument('-b', "--base64url", default=False, action='store_true',
                        help="urls are in base64url ecoding")
    parser.add_argument('-D', "--download-only", default=False, action='store_true',
                        help="download image from url to local path")

    args = parser.parse_args()
   
    url = args.urls[0] if args.urls else None # assume in the clear
    url_b64 = str2b64(url) if not args.base64url else url # url_b64 is base64 encoded
    url     = b642str(url_b64) if args.base64url else url # url is in the clear

    print(f'url: {url}')
    print(f'url_base64: {url_b64}')
    local_path = get_temp_file() 
    
    if args.download_only:
        local_path=download_url(url, local_path)
        return 0

    ops = {
        'url'       : url,
        'output_path': args.out,
        'multi'     : args.multi,
        'diamond'   : args.diamond,
        'color'     : args.color,
        'working_res': args.working_res,
        'enlarge'   : args.enlarge,
        'pool'      : args.pool
    }

    mosaic( ops )

    return 0

if __name__ == "__main__":
    main()