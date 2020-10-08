pipeline {
    agent { label 'master' }
    environment {
        ML_IMAGE_FOLDER         = 'imagefiles'
        IMAGE_NAME              = "${DOCKER_IMAGE_REPO_NAME}"
        MODEL_NAME              = "${MODEL_NAME}"
        SCORE_SCRIPT            = 'scoring/score.py'
        RESOURCE_GROUP          = "${RESOURCE_GROUP}"
        WORKSPACE_NAME          = "${WORKSPACE_NAME}"
        ML_CONTAINER_REGISTRY   = "${ML_CONTAINER_REGISTRY}"
        DEFAULT_CONDA_ENV_NAME  = 'mlopspython_ci_env'
    }
    stages {
        stage('initialize') {
            steps {
                echo 'Remove the previous one!'
            }
            post {
                always {
                    deleteDir() /* clean up our workspace */
                }
            }
        }
        stage ('Download build artifacts (get model name)') {
            environment {
                BUILD_ARTIFACT_FOLDER = "download"
            }
            steps {
                script {
                    copyArtifacts(projectName: "${env.build_job_name}", selector: buildParameter("ml_model_selector"), target: "${env.BUILD_ARTIFACT_FOLDER}");
                    def  FILES_LIST = sh (script: "ls   '${env.BUILD_ARTIFACT_FOLDER}'", returnStdout: true).trim()
                    //DEBUG
                    echo "FILES_LIST : ${FILES_LIST}"
                    MODEL_NAME = sh (script: "cat ${env.BUILD_ARTIFACT_FOLDER}/model_name.txt", 
                                     returnStdout: true).trim()
                    sh "echo ${MODEL_NAME}"
                }
            }
        }
        stage('generate_dockerfile') {
            steps {
                echo "Hello docker image build ${env.BUILD_ID}"
                checkout scm

                sh '''
                    conda env create --name $DEFAULT_CONDA_ENV_NAME --file ./diabetes_regression/ci_dependencies.yml --force 
                '''
                
                withCredentials([azureServicePrincipal("${AZURE_SP}")]) {
                    sh '''#!/bin/bash -ex
                        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET -t $AZURE_TENANT_ID
                        az account set -s $AZURE_SUBSCRIPTION_ID
                        export SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID
                        source $CONDA_PATH/activate $DEFAULT_CONDA_ENV_NAME
                        python3 -m ml_service.util.create_scoring_image
                    '''
                }
            }
        }
        stage('build_and_push') {
            steps {
                echo "Build docker images"

                sh '''#!/bin/bash -ex
                    az acr login --name $ML_CONTAINER_REGISTRY
                    docker build -t $NEXUS_DOCKER_REPO_BASE_URL/$IMAGE_NAME:$BUILD_ID ./diabetes_regression/scoring/$ML_IMAGE_FOLDER/ 
                '''

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: "${NEXUS_DOCKER_CREDENTIALS_NAME}",
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                        
                    sh '''#!/bin/bash -ex
                        docker login -u $USERNAME --password $PASSWORD https://$NEXUS_DOCKER_REPO_BASE_URL
                        docker push $NEXUS_DOCKER_REPO_BASE_URL/$IMAGE_NAME:$BUILD_ID
                    '''
                }
            }
        }
        stage('deploy') {
            steps {
                echo "Deploy to Azure App Service"

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: "${NEXUS_DOCKER_CREDENTIALS_NAME}",
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                        
                    sh '''#!/bin/bash -ex
                        az webapp config container set --name $AZURE_APPSERVICE_NAME --resource-group $APPSERVICE_RESOURCE_GROUP --docker-custom-image-name $NEXUS_DOCKER_REGISTRY_URL/$IMAGE_NAME:$BUILD_ID --docker-registry-server-url https://$NEXUS_DOCKER_REGISTRY_URL --docker-registry-server-user $USERNAME --docker-registry-server-password $PASSWORD
                        az webapp restart --name $AZURE_APPSERVICE_NAME --resource-group $APPSERVICE_RESOURCE_GROUP
                    '''
                }
            }
        }
    }
}