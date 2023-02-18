
from multiprocessing.dummy import Pool as ThreadPool
from grid import Grid
import argparse
from util import *
import math
import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "run"
                                      # This will load the root logger
def run(ops):

    url         = ops['url']
    local_path  = ops['local_path' ]
    output_path = ops['output_path']
    multi       = ops['multi']
    diamond     = ops['diamond']
    color       = ops['color']
    working_res = ops['working_res']
    enlarge     = ops['enlarge']
    pool        = ops['pool']

    print(f'local_path:{local_path}')
    print(f'output_path:{output_path}')
    print(f'pix_multi:{multi}')
    print(f'diamond:{diamond}')
    print(f'color:{color}')
    print(f'working_res:{working_res}')
    print(f'enlarge:{enlarge}')
    print(f'pool:{pool}')
  
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

    grid = Grid(local_path, pix=0, pix_multi=multi, diamond=diamond,
                colorful=color, working_res=working_res, enlarge=enlarge)

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
        pool = ThreadPool(8)
        pool.map(grid.grid_start_end_thread, todos)
        pool.close()
        pool.join()
    except (KeyboardInterrupt, SystemExit):
        pool.terminate()

    ext = get_ext(local_path, with_dot=True)
    output_path = output_path + ext 
    grid.save(output_path)

    return 0, output_path
    #
    #
    # print 100in
    # grid.grid_start_end(0, grid.rows)
    # grid.save(output_path)

    # if e_index < grid.rows:
    #     s_index = ending_index
    #     e_index = grid.rows
    #     grid.grid_start_end(s_index, e_index)
    #     grid.save(output_path)
    #     print 100


def run_defaults( ops ):
    
    print_dict(ops)
    uid = ops['uid']
    
    ops['output_path'] = '/tmp/out-' + str(uid) 
    ops['multi'  ] = 0.014
    ops['diamond'] = True
    ops['color'  ] = 1
    ops['working_res'] = 0
    ops['enlarge'] = 2000
    ops['pool']    = 1

    print(f'ops={ops}')
    rc, output_path = run(ops)

    return rc, output_path

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
        'url' : url,
        'local_path': local_path,
        'output_path': args.out,
        'multi'     : args.multi,
        'diamond'   : args.diamond,
        'color'     : args.color,
        'working_res': args.working_res,
        'enlarge'   : args.enlarge,
        'pool'      : args.pool
    }

    run( ops )

    return 0


if __name__ == "__main__":
    main()
