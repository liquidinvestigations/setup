import re
from pathlib import Path
from contextlib import contextmanager
import subprocess
from ..tools import run, losetup, mount_target

IMAGES = Path('/mnt/images')


class Platform:

    def get_base_image(self):
        raise NotImplementedError


@contextmanager
def patch_resolv_conf(target):
    resolv_conf = target.mount_point / 'etc' / 'resolv.conf'
    resolv_conf_orig = resolv_conf.with_name(resolv_conf.name + '.orig')

    resolv_conf.rename(resolv_conf_orig)
    with resolv_conf.open('wb') as dst:
        dst.write(b"nameserver 8.8.8.8\n")

    try:
        yield

    finally:
        resolv_conf_orig.rename(resolv_conf)


class BaseBuilder:

    setup = Path(__file__).resolve().parent.parent.parent.parent

    def install_ansible(self):
        have_ansible = (
            run(['which', 'ansible-playbook'], stdout=PIPE)
            .stdout.strip()
        )
        if not have_ansible:
            run(['apt-add-repository', '-y', 'ppa:ansible/ansible'])
            run(['apt-get', '-qq', 'update'])
            run(['apt-get', '-qq', 'install', '-y', 'ansible', 'git'])

    def install_qemu_utils(self):
        run(['apt-get', '-qq', 'install', '-y', 'qemu-utils'])

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
    def open_target(self, image):
        mount_point = Path('/mnt/target')
        mount_point.mkdir(parents=True, exist_ok=True)

        with losetup(image, self.platform.offset) as device:
            with mount_target(device, mount_point, ['proc', 'dev']) as target:
                with patch_resolv_conf(target):
                    yield target

    def prepare_chroot(self, target):
        target.chroot_run(['apt-get', '-qq', 'update'])
        target.chroot_run(['apt-get', '-qq', 'install', '-y', 'python'],
                          stdout=subprocess.DEVNULL)
        target.chroot_run(['apt-get', '-qq', 'clean'])

    def _ansible_playbook(self, playbook):
        run(['ansible-playbook', '-i', 'hosts', playbook],
            cwd=str(self.setup / 'ansible'))

    def install_docker_images(self, target):
        self._ansible_playbook('image_host_docker.yml')
        run(['service', 'docker', 'stop'])
        run([
            'cp', '-a',
            '/var/lib/docker',
            str(target.mount_point / 'var/lib/docker'),
        ])

    def install(self, target):
        self._ansible_playbook('image_chroot.yml')

    def prepare_image(self):
        image = self.platform.get_base_image()
        self.resize_partition(image, '8G')

        with self.open_target(image) as target:
            run(['resize2fs', target.device])

        return image

    def build(self):
        self.install_ansible()
        self.install_qemu_utils()
        image = self.prepare_image()
        with self.open_target(image) as target:
            self.prepare_chroot(target)
            self.install_docker_images(target)
            self.install(target)
