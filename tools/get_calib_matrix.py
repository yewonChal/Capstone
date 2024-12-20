import numpy as np
import cv2
import glob
import os
'''
https://kushalvyas.github.io/calib.html
'''

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

#Number of inner corners per a chessboard row and column
nx = 8 #9
ny = 5 #6

NumberofCalibrationImages = 15

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((nx*ny,3), np.float32)
objp[:,:2] = np.mgrid[0:nx,0:ny].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

cap_receive = cv2.VideoCapture(0)
i = 0
if not cap_receive.isOpened():
    print('VideoCapture not opened')
    exit(0)
import pdb

# Set properties. Each returns === True on success (i.e. correct resolution)
W = cap_receive.get(cv2.CAP_PROP_FRAME_WIDTH) #640
H = cap_receive.get(cv2.CAP_PROP_FRAME_HEIGHT) #480

W = 640
H = 480 #360
print(cap_receive.set(cv2.CAP_PROP_FRAME_WIDTH, W))
print(cap_receive.set(cv2.CAP_PROP_FRAME_HEIGHT, H))
# pdb.set_trace()
waitTime = 10 # Time for adjusting the camera
while i < NumberofCalibrationImages:
    tmp = 0
    while tmp < waitTime:
        print('Num of imgs {}/{}'.format(i,NumberofCalibrationImages),' : ',tmp)
        ret,img = cap_receive.read()
        if not ret:
            print('empty frame')
            break
        cv2.imshow('input frame', img)
        tmp = tmp + 1
        key = cv2.waitKey(1)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (nx,ny),None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (nx,ny), corners2,ret)
        cv2.imshow('input frame', img)
        cv2.waitKey(1000)
        imgpoints.append(corners2)
        objpoints.append(objp)
        i = i + 1
cv2.destroyAllWindows()

ret,img = cap_receive.read()
if not ret:
    print('empty frame')

h,  w = img.shape[:2]
print(img.shape[:2])


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (w, h),None,None)
print('Rotation vec')
print(rvecs)
print('Translation vec')
print(tvecs)
print('MTX')
print(mtx)
print('DIST')
print(dist)
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
# undistort
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
# crop the image
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]

# WRITE INTO YAML
import yaml

yaml_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'calib'))
if not os.path.exists(yaml_dir):
    os.makedirs(yaml_dir)

yaml_path = os.path.join(yaml_dir, 'sample_params.yaml')

# Custom representer to ensure 'data' fields are saved in flow style (single line)
def represent_list_flow(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(list, represent_list_flow)  # Apply this style for all lists

# Calibration data to be saved
calibration_data = {
    'image_width': w,
    'image_height': h,
    'camera_matrix': {
        'rows': 3,
        'cols': 3,
        'data': mtx.flatten().tolist()  # Ensure it stays in list format
    },
    'distortion_coefficients': {
        'rows': 1,
        'cols': 5,
        'data': dist.flatten().tolist()  # Ensure it stays in list format
    }
}

# Save to YAML file ensuring proper formatting with flow style for lists
with open(yaml_path, 'w') as yaml_file:
    yaml.dump(calibration_data, yaml_file, default_flow_style=False)

print(f"Camera calibration parameters saved to {yaml_path}")