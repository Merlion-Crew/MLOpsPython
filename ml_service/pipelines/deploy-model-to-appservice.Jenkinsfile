pipeline {
    agent { label 'master' }
    environment {
        ML_IMAGE_FOLDER         = 'imagefiles'
        IMAGE_NAME              = 'mlmodelimage'
        MODEL_NAME = 'diabetes_regression_model.pkl'
        MODEL_VERSION = "${MODEL_VERSION}"
        SCORE_SCRIPT = 'scoring/score.py'
        RESOURCE_GROUP = "${RESOURCE_GROUP}"
        WORKSPACE_NAME = "${WORKSPACE_NAME}"
        PACKAGE_FOLDER = './download'
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
                /*checkout scm*/
                checkout([$class: 'GitSCM', branches: [[name: '*/ml_model_uc81']],
                    userRemoteConfigs: [[url: 'https://github.com/Merlion-Crew/MLOpsPython.git/']]])
                azureCLI commands: [[exportVariablesString: '/id|SUBSCRIPTION_ID', script: "az account show"]], principalCredentialId: "${AZURE_SP}"
                
                sh '''#!/bin/bash -ex
                    az ml model download --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME --model-id $MODEL_NAME:$MODEL_VERSION --target-dir $PACKAGE_FOLDER
                '''
            }
        }
        stage('build_zip_package') {
            steps {
                echo "Packaging..."
                
                sh '''#!/bin/bash -ex
                    cp ./ml_service/util/scoring/* $PACKAGE_FOLDER/
                    cp ./diabetes_regression/$SCORE_SCRIPT $PACKAGE_FOLDER/
                '''
            }
        }
    }
}