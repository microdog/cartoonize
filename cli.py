import argparse
import os.path as osp
import subprocess
import tempfile

import skvideo.io

from white_box_cartoonizer.cartoonize import WB_Cartoonize

BASE_DIR = osp.dirname(osp.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', action='store_true', default=False)
    parser.add_argument(
        '--models',
        type=str,
        default=osp.join(BASE_DIR, 'white_box_cartoonizer/saved_models'),
    )
    parser.add_argument('--output', type=str, default='')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+')
    return parser.parse_args()


def get_frame_rate(filepath):
    file_metadata = skvideo.io.ffprobe(filepath)
    original_frame_rate = None
    if 'video' in file_metadata:
        if '@r_frame_rate' in file_metadata['video']:
            original_frame_rate = file_metadata['video']['@r_frame_rate']
    if original_frame_rate is None:
        raise ValueError(f'cannot parse frame rate from video: {filepath}')
    a, b = original_frame_rate.split('/')
    return round(int(a) / int(b), 2)


def extract_audio(filepath, audio_filepath):
    subprocess.run(
        [
            'ffmpeg',
            '-hide_banner',
            '-loglevel',
            'warning',
            '-i',
            filepath,
            '-map',
            '0:1',
            '-vn',
            '-acodec',
            'copy',
            '-strict',
            '-2',
            '-y',
            audio_filepath,
        ],
        check=True,
    )


def attach_audio(filepath, audio_filepath, output_filepath):
    subprocess.run(
        [
            'ffmpeg',
            '-hide_banner',
            '-loglevel',
            'warning',
            '-i',
            filepath,
            '-i',
            audio_filepath,
            '-codec',
            'copy',
            '-shortest',
            '-y',
            output_filepath,
        ],
        check=True,
    )


def process_video(
    args, cartoonizer: WB_Cartoonize, filepath: str, output_filepath: str
):
    frame_rate = get_frame_rate(filepath)

    with tempfile.NamedTemporaryFile('wb', suffix='.mp4') as tmp_audio_fp:
        with tempfile.NamedTemporaryFile('wb', suffix='.mp4') as tmp_video_fp:
            extract_audio(filepath, tmp_audio_fp.name)
            cartoonizer.process_video(
                filepath, str(frame_rate), final_name=tmp_video_fp.name
            )
            attach_audio(
                tmp_video_fp.name,
                tmp_audio_fp.name,
                output_filepath,
            )


def main():
    args = parse_args()

    cartoonizer = WB_Cartoonize(args.models, args.gpu)

    for filepath in args.files:
        final_video_path = osp.join(args.output, 'cartoon-' + osp.basename(filepath))
        print(filepath)
        process_video(args, cartoonizer, filepath, final_video_path)
        print(filepath, '->', final_video_path)


if __name__ == '__main__':
    main()
