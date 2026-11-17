import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(arguments):
    result = subprocess.run(arguments, capture_output=True, text=True, check=True)
    return result.stdout, result.stderr


def numeric(value):
    if value in (None, 'N/A', '0/0'):
        return None
    return float(Fraction(str(value)))


def inspect_file(path):
    output, _ = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])
    probe = json.loads(output)
    videos = [s for s in probe['streams'] if s.get('codec_type') == 'video']
    if not videos:
        raise ValueError(f'No video stream: {path}')
    video = videos[0]
    duration = numeric(video.get('duration'))
    if duration is None:
        duration = numeric(probe.get('format', {}).get('duration'))
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    count = video.get('nb_frames')
    return {
        'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest.hexdigest(),
        'video': {'codec': video.get('codec_name'), 'width': video.get('width'), 'height': video.get('height'),
                  'fps': numeric(video.get('avg_frame_rate')), 'duration': duration,
                  'frames': int(count) if count not in (None, 'N/A') else None,
                  'pixel_format': video.get('pix_fmt')},
        'audio': [{'codec': s.get('codec_name'), 'sample_rate': s.get('sample_rate'), 'channels': s.get('channels')}
                  for s in probe['streams'] if s.get('codec_type') == 'audio'],
    }


def video_hash(path):
    output, _ = run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0', '-c:v', 'copy', '-f', 'hash', '-hash', 'sha256', '-'])
    value = output.strip()
    if not re.fullmatch(r'SHA256=[a-f0-9]{64}', value):
        raise ValueError(f'Unexpected FFmpeg hash output: {value}')
    return value.partition('=')[2]


def main():
    parser = argparse.ArgumentParser(description='Technical video inspection; does not judge creative quality, listening or reference parity.')
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--compare-video', type=Path)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--fps', type=float)
    parser.add_argument('--width', type=int)
    parser.add_argument('--height', type=int)
    parser.add_argument('--decode', action='store_true')
    parser.add_argument('--audio-levels', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    for command in ('ffmpeg', 'ffprobe'):
        if not shutil.which(command):
            raise ValueError(f'Required command not found: {command}')
    paths = [args.video.resolve()]
    if args.compare_video:
        paths.append(args.compare_video.resolve())
    if args.report.resolve() in paths or args.report.suffix.lower() != '.json':
        raise ValueError('Report must be a separate .json file, never an input video.')
    for path in paths:
        if not path.is_file():
            raise ValueError(f'Input file not found: {path}')
    files = [inspect_file(path) for path in paths]
    info = files[0]['video']
    errors = []
    for key in ('width', 'height', 'fps', 'duration'):
        expected = getattr(args, key)
        if expected is None:
            continue
        actual = info[key]
        tolerance = max(.001, 1 / info['fps']) if key == 'duration' and info['fps'] else .001
        if actual is None or abs(actual - expected) > tolerance:
            errors.append(f'{key}: expected {expected}, observed {actual}')
    if args.duration is not None and args.fps is not None:
        expected_frames = round(args.duration * args.fps)
        if info['frames'] != expected_frames:
            errors.append(f'frame count: expected {expected_frames}, observed {info["frames"]}')
    result = {'files': files, 'checks': {}, 'errors': errors,
              'unverified': ['visual design', 'human listening', 'audio synchronization', 'reference-video parity', 'user creative acceptance']}
    if args.decode:
        for path in paths:
            run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-map', '0:v:0', '-f', 'null', '-'])
        result['checks']['complete_video_decode'] = True
    if args.compare_video:
        hashes = [video_hash(path) for path in paths]
        result['checks']['encoded_video_hashes'] = hashes
        result['checks']['encoded_video_equal'] = hashes[0] == hashes[1]
        if hashes[0] != hashes[1]:
            errors.append('Encoded video streams differ; decoded pixel equality was not evaluated.')
    if args.audio_levels:
        if not files[0]['audio']:
            errors.append('Audio-level inspection requested but the video has no audio stream.')
        else:
            _, stderr = run(['ffmpeg', '-hide_banner', '-i', str(paths[0]), '-map', '0:a:0', '-vn', '-af', 'volumedetect', '-f', 'null', '-'])
            levels = re.findall(r'(mean_volume|max_volume):\s*(-?[\d.]+|inf|-inf)\s*dB', stderr)
            if not levels:
                raise ValueError('FFmpeg did not return requested audio-level measurements.')
            result['checks']['decoded_audio_levels_dbfs'] = dict(levels)
            result['checks']['audio_level_scope'] = 'First delivered audio stream, original channel layout; sample-peak statistics, not true peak or listening.'
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(args.report.resolve()), 'passed_technical_checks': not errors, 'errors': errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        detail = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) and error.stderr else str(error)
        print(json.dumps({'error': detail}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
