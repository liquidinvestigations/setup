// vim: ft=groovy
properties([
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '3', daysToKeepStr: '', numToKeepStr: '3')),
    pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '2d']])
])

node('cloud') {
    def cloud_image = 'https://jenkins.liquiddemo.org/__images__/factory/cloud-x86_64-image.tar.xz'
    def liquid_prerequisites_cloud_image = 'https://jenkins.liquiddemo.org/job/setup-prerequisites/job/master/lastSuccessfulBuild/artifact/liquid-cloud-x86_64-prerequisites.img.xz'
    stage('CLOUD: Host Debug Information') {
        sh 'set -x && hostname && uname -a && free -h && df -h'
    }
    deleteDir()
    checkout scm
    stage('CLOUD: Build a Factory & Prepare Cloud Image') {
        sh 'git clone https://github.com/liquidinvestigations/factory'
        sh "cd factory/images; mkdir cloud-x86_64; cd cloud-x86_64; curl -L {$cloud_image} | xzcat | tar x"
    }
    stage('CLOUD: Prepare the build') {
        sh 'cp jenkins-config.yml ansible/vars/config.yml'
        sh 'mkdir images'
        sh "curl -L {$liquid_prerequisites_cloud_image} | xzcat > images/ubuntu-x86_64-raw.img"
    }
    stage('CLOUD: Build Image') {
        sh 'factory/factory run --smp 2 --memory 2048 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/jenkins_build /mnt/setup/bin/build_image cloud --image /mnt/images/ubuntu-x86_64-raw.img'
    }
    stage('CLOUD: Test and Archive') {
        parallel(
            first_boot: {
                stage("CLOUD: Run first boot") {
                    sh 'mkdir factory/images/liquid-cloud-x86_64'
                    sh 'cp images/ubuntu-x86_64-raw.img factory/images/liquid-cloud-x86_64/disk.img'
                    sh 'echo \'{"login": {"username": "liquid", "password": "liquid"}}\' > factory/images/liquid-cloud-x86_64/config.json'
                    sh 'factory/factory --platform liquid-cloud-x86_64 run --smp 2 --memory 2048  --share .:/mnt/setup /mnt/setup/bin/wait_first_boot.py'
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
                    sh 'factory/factory run --smp 2 --memory 2048 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/convert-image.sh'
                    sh 'mv images/output/ubuntu-x86_64-vbox.box liquid-cloud-x86_64-vbox.box'
                    archiveArtifacts 'liquid-cloud-x86_64-vbox.box'
                }
            }
        )
    }
}
