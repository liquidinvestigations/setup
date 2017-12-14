// vim: ft=groovy
properties([
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '3', daysToKeepStr: '', numToKeepStr: '3')),
    pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '2d']])
])

node('cloud') {
    def liquid_prerequisites_cloud_image = 'https://jenkins.liquiddemo.org/job/setup-prerequisites/job/master/lastSuccessfulBuild/artifact/liquid-cloud-x86_64-prerequisites.img.gz'
    stage('CLOUD: Host Debug Information') {
        sh 'set -x && hostname && uname -a && free -h && df -h'
    }
    deleteDir()
    dir('setup') {
        checkout scm
    }
    try {
        stage('CLOUD: Prepare factory') {
            sh "#!/bin/bash\npython3 <(curl -sL https://github.com/liquidinvestigations/factory/raw/master/install.py) factory"
        }
        stage('CLOUD: Prepare the build') {
            sh 'cp setup/jenkins-config.yml setup/ansible/vars/config.yml'
            sh 'mkdir images'
            sh "wget -q $liquid_prerequisites_cloud_image -O images/pre.img.gz"
            sh 'zcat images/pre.img.gz > images/ubuntu-x86_64-raw.img'
            sh 'rm images/pre.img.gz'
        }
        stage('CLOUD: Build Image') {
            sh 'factory/factory run --smp 2 --memory 2048 --share setup:/mnt/setup --share images:/mnt/images /mnt/setup/bin/jenkins_build /mnt/setup/bin/build_image cloud --image /mnt/images/ubuntu-x86_64-raw.img'
        }
        stage('CLOUD: Test and Archive') {
            parallel(
                first_boot: {
                    try {
                        stage("CLOUD: Run first boot") {
                            sh 'mkdir factory/images/liquid'
                            sh 'cp images/ubuntu-x86_64-raw.img factory/images/liquid/disk.img'
                            sh 'factory/factory run --share setup:/mnt/setup --share factory/images/liquid:/mnt/liquid /mnt/setup/bin/with-image-chroot /mnt/liquid/disk.img bash /opt/setup/ci/prepare-image-for-testing'
                            sh 'echo \'{"login": {"username": "liquid-admin", "password": "liquid"}}\' > factory/images/liquid/config.json'
                            sh 'factory/factory run --image liquid --smp 2 --memory 2048  --share setup:/mnt/setup PYTHONUNBUFFERED=yeah /mnt/setup/bin/run_first_boot_tests.py'
                        }
                    }
                    finally {
                        junit 'setup/tests/results/*.xml'
                    }
                },
                archive_raw_image: {
                    stage('CLOUD: Archive Raw Image') {
                        sh 'gzip -1 < images/ubuntu-x86_64-raw.img > liquid-cloud-x86_64-raw.img.gz'
                        archiveArtifacts 'liquid-cloud-x86_64-raw.img.gz'
                    }
                }
            )
        }
    } finally {
        deleteDir()
    }
}
