# Driver Test for Face Recognition (Colab)

This folder contains all necessary data and scripts to test face recognition models in Google Colab, especially for users without a local GPU.

## Contents
- `known_faces/` : Folder with sample face images for recognition.
- `test_face_recognition.py` : Example script to run face recognition on the provided images.

## How to Use in Google Colab
1. Upload the entire `driver_test` folder to your Google Drive.
2. In your Colab notebook, mount your Google Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
3. Change directory to the `driver_test` folder:
   ```python
   %cd /content/drive/MyDrive/driver_test
   ```
4. Install required packages:
   ```python
   !pip install face_recognition opencv-python
   ```
5. Run the test script:
   ```python
   !python test_face_recognition.py
   ```

## Notes
- You can add more images to the `known_faces` folder for testing.
- The script will print out recognized faces and their matches. 