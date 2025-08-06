#!/bin/bash
# Author:Chinmay Thete
# Date Created:05/08/2025
# Modification Date:06/08/2025
# Description: Download pickle file of model.
# Usage:bash download_model.sh
# prerequiest:Files should be on Google Drive.


echo "📥 Downloading model files from Google Drive..."

# Replace these with your actual Google Drive file IDs
RF_ID="1udq4rkuf1ZEcOpPidSo5CTXPAM10Klqx"
SCALER_ID="1Eq595Pnp8L0-106dz5UyzMq0EwKSGQZV"


# Download each file using curl
curl -L -o random_forest.pkl "https://drive.google.com/uc?export=download&id=${RF_ID}"
curl -L -o scaler.pkl "https://drive.google.com/uc?export=download&id=${SCALER_ID}"


echo "All model files downloaded successfully!"
