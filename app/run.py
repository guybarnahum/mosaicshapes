
from multiprocessing.dummy import Pool as ThreadPool
from grid import Grid
import argparse
from util import *
import math
import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "run"
                                      # This will load the root logger

def run(url_b64, photo_path, pix_multi, diamond, color,
                      working_res, enlarge, pool, output_path):

    url = b642str(url_b64)
    #print(f'photo_path:{photo_path}')
    #print(f'pix_multi:{pix_multi}')
    #print(f'diamond:{diamond}')
    #print(f'color:{color}')
    #print(f'working_res:{working_res}')
    #print(f'enlarge:{enlarge}')
    #print(f'pool:{pool}')
    #print(f'output_path:{output_path}')

    grid = Grid(url, photo_path, pix=0, pix_multi=pix_multi, diamond=diamond,
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


def run_defaults( args ):
    
    print_dict(args)

    uid       = args['uid']
    url_b64   = args['url']
    photo_path=args['temp']

    multi=0.014
    diamond=True
    color=1
    working_res=0
    enlarge=2000
    pool=1
    output_path='/tmp/out-' + str(uid) + '.jpg'

    rc, output_path = run(url_b64, photo_path, multi, diamond, color, working_res, enlarge, pool, output_path)
    return rc, output_path

def main():
    parser = argparse.ArgumentParser(description='Mosaic photos')

    parser.add_argument('urls', metavar='N', type=str, nargs='+',
                        help='Url photos base64 url encoded')
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
    parser.add_argument("-o", "--out", default="/tmp/out.jpg", type=str)
    parser.add_argument('-b', "--base64url", default=False, action='store_true',
                        help="convert urls to base64url ecoding")
    parser.add_argument('-D', "--download-only", default=False, action='store_true',
                        help="download image from url to local path")

    args = parser.parse_args()
   
    url = args.urls[0] if args.urls else None # assume in the clear
    url_b64 = str2b64(url) if not args.base64url else url # url_b64 is base64 encoded
    url     = b642str(url_b64) if args.base64url else url # url is in the clear

    print(f'url: {url}')
    print(f'url_base64: {url_b64}')

    photo_path = '/tmp/555.jpg' 
    
    if args.download_only:
        photo_path=download_url(url, photo_path)
        return 0

    run(url_b64, photo_path, args.multi, args.diamond, args.color,
        args.working_res, args.enlarge, args.pool, args.out)
    return 0


if __name__ == "__main__":
    main()
