import sys, os

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

parent = os.path.dirname(current)
sys.path.append(parent)  # <-- for worker.worker_utils

from mosaic import mosaic
import argparse

from worker.worker_util import download_url, str2b64, b642str, get_temp_file
import logging

logger = logging.getLogger(__name__)  # the __name__ resolve to "mosaic"
# This will load the root logger


def main():
    parser = argparse.ArgumentParser(description="Mosaic photos")

    parser.add_argument("urls", metavar="N", type=str, nargs="+", help="Url photos")
    parser.add_argument(
        "-d",
        "--diamond",
        default=False,
        action="store_true",
        help="Use diamond grid instead of squares",
    )
    parser.add_argument(
        "-c",
        "--color",
        default=False,
        action="store",
        choices=["0", "1", "2"],
        help="Specify color values",
    )
    parser.add_argument(
        "-a",
        "--analogous",
        default=False,
        action="store_true",
        help="Use analogous color",
    )
    parser.add_argument(
        "-r",
        "--working_res",
        default=0,
        required=False,
        type=int,
        help="Resolution to sample from",
    )
    parser.add_argument(
        "-e",
        "--enlarge",
        default=0,
        required=False,
        type=int,
        help="Resolution to draw",
    )
    parser.add_argument("-m", "--multi", default=0.014, type=float)
    parser.add_argument("-p", "--pool", default=1, type=int)
    parser.add_argument(
        "-o",
        "--out",
        default="/tmp/out.jpg",
        type=str,
        help="output file - default is /tmp/out.jpg",
    )
    parser.add_argument(
        "-b",
        "--base64url",
        default=False,
        action="store_true",
        help="urls are in base64url ecoding",
    )
    parser.add_argument(
        "-D",
        "--download-only",
        default=False,
        action="store_true",
        help="download image from url to local path",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        default="info",
        help="Provide logging level. Example --loglevel debug, default=info",
    )

    args = parser.parse_args()

    ll = args.loglevel.upper()
    logging.basicConfig(level=ll)

    url = args.urls[0] if args.urls else None  # assume in the clear
    url_b64 = str2b64(url) if not args.base64url else url  # url_b64 is base64 encoded
    url = b642str(url_b64) if args.base64url else url  # url is in the clear

    logger.info(f"url: {url}")
    logger.info(f"url_base64: {url_b64}")
    local_path = get_temp_file()
    local_path = download_url(url, local_path)

    if args.download_only:
        return 0

    ops = {
        "url": url,
        "input_path": local_path,
        "output_path": args.out,
        "multi": args.multi,
        "diamond": args.diamond,
        "color": args.color,
        "working_res": args.working_res,
        "enlarge": args.enlarge,
        "pool": args.pool,
    }

    logger.info(f"args: {args}")

    output_path = mosaic(ops)
    logger.info(f"output_path: {output_path}")

    return 0


if __name__ == "__main__":
    main()
