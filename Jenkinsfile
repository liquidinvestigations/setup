// vim: ft=groovy
parallel(
    liquid_cloud: {
        node('cloud') {
            deleteDir()
            checkout scm
            stage('CLOUD: Host Debug Information') {
                sh 'set -x && hostname && uname -a && free -h && df -h'
            }
            stage('CLOUD: Build a Factory & Prepare Cloud Image') {
                sh 'git clone https://github.com/liquidinvestigations/factory'
                sh 'cd factory/images; mkdir cloud-x86_64; cd cloud-x86_64; curl -L https://jenkins.liquiddemo.org/__images__/factory/cloud-x86_64-image.tar.xz | xzcat | tar x'
            }
            stage('CLOUD: Build Image') {
                sh 'cp jenkins-config.yml ansible/vars/config.yml'
                sh 'mkdir images'
                sh 'factory/factory run --smp 2 --memory 4096 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/jenkins_build /mnt/setup/bin/build_image cloud'
            }
            parallel(
                first_boot: {
                    stage("CLOUD: Run first boot") {
                        sh 'mkdir factory/images/liquid-cloud-x86_64'
                        sh 'cp images/ubuntu-x86_64-raw.img factory/images/liquid-cloud-x86_64/disk.img'
                        sh 'echo \'{"login": {"username": "liquid", "password": "liquid"}}\' > factory/images/liquid-cloud-x86_64/config.json'
                        sh 'factory/factory --platform liquid-cloud-x86_64 run --smp 2 --memory 4096  --share .:/mnt/setup /mnt/setup/bin/wait_first_boot.py'
                    }
                },
                archive_raw_image: {
                    stage('CLOUD: Archive Raw Image') {
                        sh 'xz -1 < images/ubuntu-x86_64-raw.img > liquid-cloud-x86_64-raw.img.xz'
                        archiveArtifacts 'liquid-cloud-x86_64-raw.img.xz'
                    }
                },
                create_vagrant_box: {
                    stage('CLOUD: Create Vagrant box for VirtualBox provider') {
                        sh 'factory/factory run --smp 2 --memory 4096 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/convert-image.sh'
                        sh 'mv images/output/ubuntu-x86_64-vbox.box liquid-cloud-x86_64-vbox.box'
                        archiveArtifacts 'liquid-cloud-x86_64-vbox.box'
                    }
                }
            )
        }
    },
    liquid_odroid_c2: {
        node('arm64') {
            deleteDir()
            checkout scm
            stage('ODROID C2: Host Debug Information') {
                sh 'set -x && hostname && uname -a && free -h && df -h'
            }
            stage('ODROID C2: Build a Factory & Prepare Cloud Image') {
                sh 'git clone https://github.com/liquidinvestigations/factory'
                sh 'cd factory/images; mkdir cloud-arm64; cd cloud-arm64; curl -L https://jenkins.liquiddemo.org/__images__/factory/cloud-arm64-image.tar.xz | xzcat | tar x'
            }
            stage('ODROID C2: Build Image') {
                sh 'cp jenkins-config.yml ansible/vars/config.yml'
                sh 'mkdir images'
                sh 'factory/factory run  --smp 2 --memory 1024 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/jenkins_build /mnt/setup/bin/build_image odroid_c2'
            }
            stage('ODROID C2: Archive Raw Image') {
                sh 'xz -1 < images/ubuntu-odroid_c2-raw.img > liquid-odroid_c2-arm64-raw.img.xz'
                archiveArtifacts 'liquid-odroid_c2-arm64-raw.img.xz'
            }
        }
    },
    failFast: true
)
