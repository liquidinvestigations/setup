import re
from pathlib import Path
from .builders.cloud import Builder_cloud
from .tools import run

SETUP_GIT = 'https://github.com/liquidinvestigations/setup'
LIQUID_DOMAIN = 'liquiddemo.org'

class DemoBuilder(Builder_cloud):

    def create_swapfile(self, target):
        swap_size_gb = 1
        swap_rel = 'var/local/swap1'
        swapfile = target.mount_point / swap_rel

        if swapfile.exists():
            print("swapfile exists; skipping")
            return

        print("creating {}GB swap file".format(swap_size_gb))
        run([
            'dd',
            'if=/dev/zero',
            'of={}'.format(swapfile),
            'bs=1M',
            'count={}'.format(1024 * swap_size_gb),
        ])

        run(['mkswap', str(swapfile)])

        target_fstab = target.mount_point / 'etc/fstab'
        with target_fstab.open('a', encoding='utf8') as f:
            f.write('/{} none swap sw 0 0\n'.format(swap_rel))

    def setup_sshd(self, target):
        sshd_config = target.mount_point / 'etc/ssh/sshd_config'
        with sshd_config.open(encoding='utf8') as f:
            config = f.read().splitlines(keepends=True)

        changed = False
        new_config = []
        for line in config:
            if re.match(r'^[#]?PasswordAuthentication no', line):
                print("Enabling sshd password authentication")
                line = 'PasswordAuthentication yes\n'
                changed = True
            new_config.append(line)

        if changed:
            with sshd_config.open('w', encoding='utf8') as f:
                f.write(''.join(new_config))

        else:
            print("Not changing SSH config, it looks good")

        target.chroot_run(['dpkg-reconfigure', 'openssh-server'])

    def setup_liquid_sudo(self, target):
        sudoers_liquid_demo = target.mount_point / 'etc/sudoers.d/liquid_demo'
        with sudoers_liquid_demo.open('w', encoding='utf8') as f:
            f.write('liquid ALL=(ALL:ALL) NOPASSWD: ALL\n')

    def setup_network(self, target):
        ens3_cfg = target.mount_point / 'etc/network/interfaces.d/ens3.cfg'
        with ens3_cfg.open('w', encoding='utf8') as f:
            f.write('auto ens3\niface ens3 inet dhcp\n')

    def setup_console(self, target):
        grub_files = [
            'boot/grub/grub.cfg',
            'etc/default/grub',
            'etc/default/grub.d/50-cloudimg-settings.cfg',
        ]
        for rel_path in grub_files:
            path = target.mount_point / rel_path
            run(['sed', '-i ', 's/console=tty1/console=ttyS0/g', str(path)])

    def setup_ansible(self, target):
        if not Path('/usr/bin/ansible-playbook').is_file():
            self.install_host_dependencies()

        setup_path = target.mount_point / 'opt/setup'

        if not setup_path.exists():
            run(['git', 'clone', SETUP_GIT, str(setup_path)])

        config_yml = setup_path / 'ansible/vars/config.yml'
        with config_yml.open('w', encoding='utf8') as f:
            f.write('liquid_domain: {}\n'.format(LIQUID_DOMAIN))
            f.write('devel: true\n')

        run([
            'ansible-playbook',
            'image_chroot.yml',
        ], cwd=str(setup_path / 'ansible'))

    def setup_demo(self):
        image = Path('/mnt/shared/demo.img')
        with self.open_target(image, self.OFFSET) as target:
            with self.patch_resolv_conf(target):
                #run(['bash'], cwd=str(target.mount_point)); return
                self.create_swapfile(target)
                self.setup_sshd(target)
                self.setup_liquid_sudo(target)
                self.setup_network(target)
                self.setup_console(target)
                self.setup_ansible(target)

def install():
    builder = DemoBuilder()
    builder.setup_demo()
