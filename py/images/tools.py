import os
from contextlib import contextmanager
from pathlib import Path
import subprocess

DEBUG = False


@contextmanager
def handle_error():
    try:
        yield
    except Exception as e:
        if DEBUG:
            print('exception!', e)
            print('[1]: print stack and exit')
            print('2: pdb')
            print('3: shell')
            resp = input('> ')

            if resp == '2':
                import pdb
                pdb.post_mortem()

            elif resp == '3':
                print('Starting interactive shell, type CTRL-D to exit.')
                subprocess.run(
                    ['bash', '--norc'],
                    env=dict(os.environ, PS1='debug $ '),
                )

        raise


def run(args, **kwargs):
    kwargs.setdefault('check', True)
    print('+', ' '.join(str(a) for a in args))
    with handle_error():
        return subprocess.run(args, **kwargs)


def download(url, path):
    if path.is_file():
        return
    return run(['curl', url, '-o', str(path)])


def xzcat(xz_path, content_path):
    with xz_path.open('rb') as xz_file:
        with content_path.open('wb') as content_file:
            return run(['xzcat'], stdin=xz_file, stdout=content_file)


@contextmanager
def losetup(image, offset):
    device = '/dev/loop0'
    run(['losetup', device, str(image), '-o', str(offset)])
    try:
        yield device
    finally:
        run(['losetup', '-d', device])


class Target:

    def __init__(self, device, mount_point):
        self.device = device
        self.mount_point = mount_point

    def chroot_run(self, args):
        return run(['chroot', str(self.mount_point)] + args)


@contextmanager
def mount_target(device, target, binds=[]):
    mounts = []

    try:
        run(['mount', device, str(target)])
        mounts.append(target)

        root = Path('/')
        for bind in (Path(b) for b in binds):
            bind_src = root / bind
            bind_target = target / bind

            run(['mount', '--bind', str(bind_src), str(bind_target)])
            mounts.append(bind_target)

        yield Target(device, target)

    finally:
        for point in reversed(mounts):
            run(['umount', '-l', str(point)])
