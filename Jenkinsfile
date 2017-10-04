// vim: ft=groovy
parallel(
    cloud: {
        node('cloud') {
            deleteDir()
            checkout scm
            stage('CLOUD: Build a Factory') {
                sh 'git clone https://github.com/liquidinvestigations/factory'
            }
            stage('CLOUD: Prepare Cloud Image') {
                sh 'factory/factory prepare-cloud-image'
            }
            stage('CLOUD: Write setup configuration file') {
                sh 'cp jenkins-config.yml ansible/vars/config.yml'
            }
            stage('CLOUD: Build Image') {
                sh 'mkdir images'
                sh 'factory/factory run --share .:/mnt/setup --share images:/mnt/images ANSIBLE_NOCOLOR=true time /mnt/setup/bin/build_image cloud'
            }
            stage("CLOUD: Run first boot") {
                sh 'mkdir factory/images/liquid-cloud-x86_64'
                sh 'cp images/ubuntu-x86_64-raw.img factory/images/liquid-cloud-x86_64/disk.img'
                sh 'echo \'{"login": {"username": "liquid", "password": "liquid"}}\' > factory/images/liquid-cloud-x86_64/config.json'
                sh 'factory/factory --platform liquid-cloud-x86_64 run --memory 2048 --share .:/mnt/setup /mnt/setup/bin/wait_first_boot.py'
            }
            stage('CLOUD: Archive Raw Image') {
                // The archiveArtifacts command keeps the relative path of the
                // file as the filename. To avoid this issue, we move all
                // binaries that will be archived to the workspace root.
                sh 'xz -1 < images/ubuntu-x86_64-raw.img > liquid-cloud-x86_64-raw.img.xz'
                archiveArtifacts 'liquid-cloud-x86_64-raw.img.xz'
            }
            stage('CLOUD: Create Vagrant box for VirtualBox provider') {
                sh 'factory/factory run --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/convert-image.sh'
                sh 'mv images/output/ubuntu-x86_64-vbox.box liquid-cloud-x86_64-vbox.box'
                archiveArtifacts 'liquid-cloud-x86_64-vbox.box'
            }
        }
    },
    odroid_c2: {
        node('arm64') {
            deleteDir()
            checkout scm
            stage('ODROID C2: Build a Factory') {
                sh 'git clone https://github.com/liquidinvestigations/factory'
            }
            stage('ODROID C2: Prepare Cloud Image') {
                sh 'factory/factory prepare-cloud-image'
            }
            stage('ODROID C2: Write setup configuration file') {
                sh 'cp jenkins-config.yml ansible/vars/config.yml'
            }
            stage('ODROID C2: Build Image') {
                sh 'mkdir images'
                sh 'factory/factory run --share .:/mnt/setup --share images:/mnt/images ANSIBLE_NOCOLOR=true time /mnt/setup/bin/build_image odroid_c2'
            }
            stage('ODROID C2: Archive Raw Image') {
                sh 'xz -1 < images/ubuntu-odroid_c2-raw.img > liquid-odroid_c2-arm64-raw.img.xz'
                archiveArtifacts 'liquid-odroid_c2-arm64-raw.img.xz'
            }
        }
    },
    failFast: true
)
