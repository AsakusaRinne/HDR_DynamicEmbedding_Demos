import numpy as np
import cv2

from RGBE import readhdr

def rgbe_to_rgb_without_offset(rgbe):
    res = np.zeros((rgbe.shape[0], rgbe.shape[1], 3))
    p = rgbe[:, :, 3] > 0
    m = 2.0 ** (rgbe[:, :, 3][p] - 136.0)
    res[:, :, 0][p] = rgbe[:, :, 0][p] * m
    res[:, :, 1][p] = rgbe[:, :, 1][p] * m
    res[:, :, 2][p] = rgbe[:, :, 2][p] * m
    return np.array(res, dtype=np.float32)

def rgbe_to_rgb_with_offset(rgbe):
    res = np.zeros((rgbe.shape[0], rgbe.shape[1], 3))
    p = rgbe[:, :, 3] > 0
    m = 2.0 ** (rgbe[:, :, 3][p] - 136.0)
    res[:, :, 0][p] = (rgbe[:, :, 0][p] + 0.5) * m
    res[:, :, 1][p] = (rgbe[:, :, 1][p] + 0.5) * m
    res[:, :, 2][p] = (rgbe[:, :, 2][p] + 0.5) * m
    return np.array(res, dtype=np.float32)

if __name__ == "__main__":
    # This is the image path, which could be changed to your own image for experiment
    image_path = '../Stairs.hdr'

    # Read the RGB image with opencv directly
    rgb_image = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)
    width = rgb_image.shape[0]
    height = rgb_image.shape[1]
    # The layout of OpenCV is "BGR", so we need to transpose it to "RGB"
    temp = np.copy(rgb_image[:, :, 2])
    rgb_image[:, :, 2] = rgb_image[:, :, 0]
    rgb_image[:, :, 0] = temp

    # Get the original rgbe data of the image
    rgbe_image = readhdr(image_path)

    # Convert rgbe data to RGB with offset
    converted_image_with_offset = rgbe_to_rgb_with_offset(rgbe_image)
    flag = True
    for i in range(width):
        if not flag:
            break
        for j in range(height):
            if not flag:
                break
            for k in range(3):
                if rgb_image[i][j][k] != converted_image_with_offset[i][j][k]:
                    print("The converted image with offset is not equal to original image.")
                    flag = False
                    break
    if flag:
        print("The converted image with offset is equal to original image.")

    # Convert rgbe data to RGB with offset
    converted_image_without_offset = rgbe_to_rgb_without_offset(rgbe_image)
    flag = True
    for i in range(width):
        if not flag:
            break
        for j in range(height):
            if not flag:
                break
            for k in range(3):
                if rgb_image[i][j][k] != converted_image_without_offset[i][j][k]:
                    print("The converted image without offset is not equal to original image.")
                    break
    if flag:
        print("The converted image without offset is equal to original image.")