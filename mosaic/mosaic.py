from concurrent.futures import ThreadPoolExecutor

import os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from grid import Grid
import util
from math import ceil
import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "mosaic"
# This will load the root logger

try:
    if not callable(profile):
        logger.error(f"profile is defined, but not callable!")
except NameError:
    # provide a benign profile decorator
    def profile(ob):
        return ob


@profile  # <-- run with -m memory_profiler to activate
def mosaic(ops, progress_callback=None):
    default_ops = {
        "multi": 0.018,
        "diamond": True,
        "color": 1,
        "working_res": 0,
        "enlarge": 0,
        "pool": 1,
    }

    ops = util.dict_set_defaults(ops, default_ops)

    logger.info(f"ops:{ops}")

    input_path = ops["input_path"]
    output_path = ops["output_path"]

    multi = ops["multi"]
    diamond = ops["diamond"]
    color = ops["color"]
    working_res = ops["working_res"]
    enlarge = ops["enlarge"]
    pool = ops["pool"]

    grid = Grid(diamond=diamond, colorful=color, progress_callback=progress_callback)

    try:
        grid.setup(
            input_path, pix=0, pix_multi=multi, working_res=working_res, enlarge=enlarge
        )
    except Exception as e:
        error = f"grid.setup: {str(e)}"
        logger.error(error)
        return None

    total_updates = 20
    step_size = util.clamp_int(int(ceil(grid.rows / (1.0 * total_updates))), 1, 10000)

    ending_index = step_size * total_updates
    # diff = grid.rows - step_size*total_updates

    todos = []
    for i in range(total_updates + 1):
        s_index = step_size * i
        e_index = s_index + step_size
        todos.append((s_index, e_index, output_path))

        is_continue = False if e_index >= grid.rows else True
        if not is_continue:
            break

    # double check that we are not doing double work
    try:
        # create a thread pool with the default number of worker threads
        pool = ThreadPoolExecutor()
        logger.info(f"executor using {pool._max_workers} workers")
        futures = [pool.submit(grid.grid_start_end_thread, todo) for todo in todos]
        pool.shutdown(wait=True)  # shutdown waits for all tasks to complete
        logger.info("thread pool completed")
    except (KeyboardInterrupt, SystemExit):
        pool.shutdown(wait=False)
        raise
        # @todo handle errors!

    grid.save(output_path)
    return output_path
