import re
from pathlib import Path
from contextlib import contextmanager
import subprocess
from ..tools import run, losetup, mount_target

IMAGES = Path('/mnt/images')


class BaseBuilder:

    setup = Path(__file__).resolve().parent.parent.parent.parent

    def install_host_dependencies(self):
        run(['apt-add-repository', '-y', 'ppa:ansible/ansible'])
        run(['apt-get', '-qq', 'update'])
        run(['apt-get', '-qq', 'install', '-y', 'ansible', 'git', 'qemu-utils'],
            stdout=subprocess.DEVNULL)

    def get_base_image(self):
        raise NotImplementedError

    def resize_partition(self, image, new_size):
        run(['truncate', '-s', new_size, str(image)])

        sfdisk_orig = (
            run(['sfdisk', '-d', str(image)], stdout=subprocess.PIPE)
            .stdout.decode('latin1')
            .splitlines(keepends=True)
        )

        sfdisk_new = []
        for line in sfdisk_orig:
            if 'type=83' in line:
                line = re.sub(r'size=[^,]+,', '', line)
            sfdisk_new.append(line)

        run(['sfdisk', str(image)], input=''.join(sfdisk_new).encode('latin1'))

    @contextmanager
    def open_target(self, image, offset):
        mount_point = Path('/mnt/target')
        mount_point.mkdir(parents=True, exist_ok=True)

        with losetup(image, offset) as device:
            with mount_target(device, mount_point, ['proc', 'dev']) as target:
                yield target

    @contextmanager
    def patch_resolv_conf(self, target):
        resolv_conf = target.mount_point / 'etc' / 'resolv.conf'
        resolv_conf_orig = resolv_conf.with_name(resolv_conf.name + '.orig')

        resolv_conf.rename(resolv_conf_orig)
        with resolv_conf.open('wb') as dst:
            dst.write(b"nameserver 8.8.8.8\n")

        try:
            yield

        finally:
            resolv_conf_orig.rename(resolv_conf)

    def prepare_chroot(self, target):
        target.chroot_run(['apt-get', '-qq', 'update'])
        target.chroot_run(['apt-get', '-qq', 'install', '-y', 'python'],
                          stdout=subprocess.DEVNULL)
        target.chroot_run(['apt-get', '-qq', 'clean'])

    def _ansible_playbook(self, playbook):
        run(['ansible-playbook', '-i', 'hosts', playbook],
            cwd=str(self.setup / 'ansible'))

    def prepare_docker_images(self):
        self._ansible_playbook('image_host_docker.yml')

    def copy_docker_images(self, target):
        run(['service', 'docker', 'stop'])
        run([
            'cp', '-a',
            '/var/lib/docker',
            str(target.mount_point / 'var/lib/docker'),
        ])

    def install(self, target):
        self._ansible_playbook('image_chroot.yml')

    def build(self):
        self.install_host_dependencies()
        image, offset = self.get_base_image()
        self.resize_partition(image, '8G')

        with self.open_target(image, offset) as target:
            run(['resize2fs', target.device])

            with self.patch_resolv_conf(target):
                self.prepare_chroot(target)
                self.prepare_docker_images()
                self.copy_docker_images(target)
                self.install(target)
