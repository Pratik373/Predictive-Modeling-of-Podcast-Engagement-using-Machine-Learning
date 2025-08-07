#!/usr/bin/env bash
# Author: Chinmay Thete
# Date: 07-Aug-2025
# Description: Downloads model .pkl files from Google Drive using gdown

# Activate virtual environment if needed
# source myenv/bin/activate

# Install gdown if not already installed
pip show gdown &>/dev/null || pip install gdown

# File IDs (update these as per your actual file IDs)
RF_ID="1udq4rkuf1ZEcOpPidSo5CTXPAM10Klqx"
SCALER_ID="1Eq595Pnp8L0-106dz5UyzMq0EwKSGQZV"
#COLS_ID="YOUR_FEATURE_COLUMNS_FILE_ID"

# Download files
gdown --id "$RF_ID" --output random_forest.pkl
gdown --id "$SCALER_ID" --output scaler.pkl
#gdown --id "$COLS_ID" --output feature_columns.pkl

echo "✅ All model files downloaded successfully!"
