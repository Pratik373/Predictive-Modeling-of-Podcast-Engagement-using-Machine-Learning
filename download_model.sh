#!/bin/bash

echo "📥 Downloading model files from Google Drive..."

# Replace these with your actual Google Drive file IDs
RF_ID="your-random-forest-id"
SCALER_ID="your-scaler-id"
COLS_ID="your-feature-columns-id"

# Download each file using curl
curl -L -o random_forest.pkl "https://drive.google.com/uc?export=download&id=${RF_ID}"
curl -L -o scaler.pkl "https://drive.google.com/uc?export=download&id=${SCALER_ID}"
curl -L -o feature_columns.pkl "https://drive.google.com/uc?export=download&id=${COLS_ID}"

echo "✅ All model files downloaded successfully!"
