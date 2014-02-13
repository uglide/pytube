"""Command-line interface for downloading YouTube videos
"""
import sys
import argparse

from youtube import YouTube


def main(args):
    yt = YouTube(args.url)
    video_id = yt.video_id
    videos = yt.mget_videos_by_id(video_id)
    for v in videos:
        sys.stdout.write("{0}\n".format(v))


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (
        bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="pytube", description=__doc__)

    parser.add_argument("-u", metavar="<url>", action="store", dest="url",
                        help="The YouTube video url", required=True)

    parser.add_argument("-i", metavar="<itag>", action="store", dest="itag",
                        type=int, help="The itag of the video to download")

    parser.add_argument("-l", action="store_true", default=False,
                        help="List the range of quality levels")

    parser.add_argument("-o", metavar="<filename>", dest="output", type=file,
                        help="The output file")

    parser.add_argument("--version", action="version",
                        version="%(prog)s 0.2.1")

    args = parser.parse_args()
