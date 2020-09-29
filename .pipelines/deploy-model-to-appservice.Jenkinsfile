pipeline {
    agent { label 'master' }
    environment {
        ML_IMAGE_FOLDER = 'imagefiles'
        IMAGE_NAME      = 'mlmodelimage'
        MODEL_NAME      = "${MODEL_NAME}"
        MODEL_VERSION   = "${MODEL_VERSION}"
        SCORE_SCRIPT    = 'scoring/score.py'
        RESOURCE_GROUP  = "${RESOURCE_GROUP}"
        WORKSPACE_NAME  = "${WORKSPACE_NAME}"
        PACKAGE_FOLDER  = './download'
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
        stage('download_model') {
            steps {
                echo "Downloading..."
                checkout scm
                
                withCredentials([azureServicePrincipal("${AZURE_SP}")]) {
                    sh '''#!/bin/bash -ex
                        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET -t $AZURE_TENANT_ID
                        az account set -s $AZURE_SUBSCRIPTION_ID
                        az ml model download --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME --model-id $MODEL_NAME:$MODEL_VERSION --target-dir $PACKAGE_FOLDER
                    '''
                }
            }
        }
        stage('build_zip_package') {
            steps {
                echo "Packaging..."
                
                sh '''#!/bin/bash -ex
                    cp ./ml_service/util/scoring/* $PACKAGE_FOLDER/
                    cp ./diabetes_regression/$SCORE_SCRIPT $PACKAGE_FOLDER/
                    cd $PACKAGE_FOLDER/
                    zip -r deployment-${BUILD_NUMBER}.zip .
                '''
            }
        }
        stage('prod') {
            steps {
                echo 'Deploying!'
                sh '''
                    cd $PACKAGE_FOLDER/
                    curl -X POST -u '\$'$AZURE_APPSERVICE_NAME:$AZURE_APPSERVICE_DEPLOYMENT_PASSWORD --data-binary @"deployment-${BUILD_NUMBER}.zip" https://$AZURE_APPSERVICE_NAME.scm.azurewebsites.net/api/zipdeploy
                '''
            }
        }
    }
}