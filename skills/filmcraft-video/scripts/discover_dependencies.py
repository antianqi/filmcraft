import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def discover(skill_roots=(), include_defaults=True, versions=False):
    roots = [Path(p).expanduser() for p in skill_roots]
    roots += [Path(p).expanduser() for p in os.environ.get('FILMCRAFT_SKILL_ROOTS', '').split(os.pathsep) if p]
    if include_defaults:
        roots += [Path.home() / '.agents/skills', Path.home() / '.codex/skills']
    roots = list(dict.fromkeys(p.resolve() for p in roots))
    skills = {}
    for name in ('motionharness', 'video-shotcraft'):
        candidates = []
        for root in roots:
            path = root / name / 'SKILL.md'
            if path.is_file() and os.access(path, os.R_OK):
                resolved = str(path.resolve())
                if resolved not in candidates:
                    candidates.append(resolved)
        skills[name] = {'selected': candidates[0] if candidates else None, 'candidates': candidates}
    commands = {}
    for name in ('mh', 'ffmpeg', 'ffprobe'):
        executable = shutil.which(name)
        info = {'executable': executable}
        if executable and versions:
            argument = '--version' if name == 'mh' else '-version'
            result = subprocess.run([executable, argument], capture_output=True, text=True, timeout=15)
            info['returncode'] = result.returncode
            output = (result.stdout or result.stderr).strip().splitlines()
            info['version'] = output[0] if output else None
        commands[name] = info
    return {'skill_roots': [str(p) for p in roots], 'skills': skills, 'commands': commands}


def main():
    parser = argparse.ArgumentParser(description='Read-only discovery of Filmcraft local dependencies; never installs software.')
    parser.add_argument('--skill-root', action='append', default=[])
    parser.add_argument('--no-default-roots', action='store_true')
    parser.add_argument('--versions', action='store_true')
    parser.add_argument('--require-render', action='store_true')
    parser.add_argument('--require-shotcraft', action='store_true')
    args = parser.parse_args()
    result = discover(args.skill_root, not args.no_default_roots, args.versions)
    errors = []
    if args.require_render:
        if not result['skills']['motionharness']['selected']:
            errors.append('Missing readable motionharness/SKILL.md')
        for name, info in result['commands'].items():
            if not info['executable'] or info.get('returncode', 0) != 0:
                errors.append(f'Missing or failing command: {name}')
    if args.require_shotcraft and not result['skills']['video-shotcraft']['selected']:
        errors.append('Missing readable video-shotcraft/SKILL.md')
    result['errors'] = errors
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
