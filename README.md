
# FlareSight-AI

FlareSight-AI is an AI-driven project for satellite solar analysis and control. The project operates in two main stages:

1. **Interface & Model Prediction Stage**  
   - **Model Loading:** Pre-trained CNN models for Continuum and Magnetogram analysis (`continuum_cnn1.h5` and `magnetogram_cnn1.h5`) are loaded.
   - **Image Acquisition & Processing:** The Gradio interface fetches the latest solar images from specified APIs/URLs. These images are resized and cropped to meet model input requirements.
   - **Prediction & Result Saving:** The processed images are fed to the models to generate predictions. The results are then saved in JSON format (e.g., `continuum_result.json` and `magnetogram_result.json`).

2. **Satellite Integration Stage**  
   - **Result Utilization:** The JSON result files are read to extract key indices (such as the KP index) and prediction values.
   - **Command Determination & Transmission:** Based on the model outputs and KP classification, control commands are generated.
   - **Bluetooth Communication & PyBricks Integration:**  
     The project includes complete PyBricks-based code in the `control.py` and `integration.py` scripts. These scripts handle the hardware integration and remote command transmission over Bluetooth to the satellite (or its control unit). They ensure that commands (e.g., moving a motor forward or reversing) are sent correctly based on the prediction results.

## Features

- **Deep Learning Models:**  
  - **Continuum Model:** Predicts solar continuum features.
  - **Magnetogram Model:** Predicts solar magnetogram features.

- **User Interface:**  
  - A Gradio-based interface for fetching images, processing predictions, and displaying results.

- **Result Logging:**  
  - Prediction outputs are saved as JSON files, which are then used for further satellite integration.

- **Satellite Control Integration:**  
  - Complete PyBricks-based code in `control.py` and `integration.py` handles the generation and transmission of control commands via Bluetooth.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/adakilinc/FlareSight-AI.git
   cd FlareSight-AI

