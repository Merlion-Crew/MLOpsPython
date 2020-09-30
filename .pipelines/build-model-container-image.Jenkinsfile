pipeline {
    agent { label 'master' }
    environment {
        ML_IMAGE_FOLDER = 'imagefiles'
        IMAGE_NAME      = 'mlmodelimage'
        MODEL_NAME      = "${MODEL_NAME}"
        SCORE_SCRIPT    = 'scoring/score.py'
        RESOURCE_GROUP  = "${RESOURCE_GROUP}"
        WORKSPACE_NAME  = "${WORKSPACE_NAME}"
        ML_CONTAINER_REGISTRY   = "${ML_CONTAINER_REGISTRY}"
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
        stage('generate_dockerfile') {
            steps {
                echo "Hello build ${env.BUILD_ID}"
                //checkout scm
                checkout([$class: 'GitSCM', branches: [[name: '*/ml_model_uc76']],
                    userRemoteConfigs: [[url: 'https://github.com/Merlion-Crew/MLOpsPython.git/']]])

                /*withCredentials([azureServicePrincipal("${AZURE_SP}")]) {
                    sh '''#!/bin/bash -ex
                        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET -t $AZURE_TENANT_ID
                        az account set -s $AZURE_SUBSCRIPTION_ID
                        SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID
                    '''
                }*/

                azureCLI commands: [[exportVariablesString: '/id|SUBSCRIPTION_ID', script: "az account show"]], principalCredentialId: "${AZURE_SP}"
                
                sh '''#!/bin/bash -ex
                    echo $SUBSCRIPTION_ID
                    source /home/azureuser/anaconda3/bin/activate mlopspython_ci
                    python3 -m ml_service.util.create_scoring_image
                '''
            }
        }
        stage('build_and_push') {
            steps {
                echo "Build docker images"

                sh '''#!/bin/bash -ex
                    az acr login --name $ML_CONTAINER_REGISTRY
                    docker build -t $NEXUS_DOCKER_REGISTRY_URL/$IMAGE_NAME:$BUILD_ID ./diabetes_regression/scoring/$ML_IMAGE_FOLDER/ 
                '''

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'nexus-docker-repo',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                        
                    sh '''#!/bin/bash -ex
                        docker login -u $USERNAME --password $PASSWORD https://$NEXUS_DOCKER_REGISTRY_URL
                        docker push $NEXUS_DOCKER_REGISTRY_URL/$IMAGE_NAME:$BUILD_ID
                    '''
                }
            }
        }
        stage('deploy') {
            steps {
                echo "Deploy to Azure App Service"

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'nexus-docker-repo',
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