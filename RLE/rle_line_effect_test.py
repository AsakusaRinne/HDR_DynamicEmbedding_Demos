import cv2
import os
import random

def get_rgbe_data_size(filename):
    '''
    Get the size of data of an rbge image, which means that the size of header is exclueded.
    :param filename: Filename
    :return: The size of data part of the given rgbe image
    '''
    fileinfo = {}
    with open(filename, 'rb') as fd:
        # Firstly, we read all the header and pass them
        tline = fd.readline().strip()
        if len(tline) < 3 or tline[:2] != b'#?':
            print('invalid header')
            return
        fileinfo['identifier'] = tline[2:]

        tline = fd.readline().strip()

        if (tline[:1] == b'#'):
            tline = fd.readline().strip()
        while tline:
            n = tline.find(b'=')
            if n > 0:
                fileinfo[tline[:n].strip()] = tline[n + 1:].strip()
            tline = fd.readline().strip()

        tline = fd.readline().strip().split(b' ')
        fileinfo['Ysign'] = tline[0][0]
        fileinfo['height'] = int(tline[1])
        fileinfo['Xsign'] = tline[2][0]
        fileinfo['width'] = int(tline[3])

        # The header part has been read, the left is the data
        data = [d for d in fd.read()]
        return len(data)

if __name__ == "__main__":
    # This is the image path, which could be changed to your own image for experiment
    image_path = '../Stairs.hdr'
    temp_file_path = './temp'
    if not os.path.exists(temp_file_path):
        os.mkdir(temp_file_path)
    image = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)
    # Get how many lines is there in the image
    row_count = image.shape[0]

    # We split the each line of the image and save them as files
    for i in range(row_count):
        filename = "%s/%d.hdr"%(temp_file_path, i)
        single_line_image = image[i : i + 1, :, :]
        cv2.imwrite(filename, single_line_image)

    # We read the single-line images from file system and verify that
    # the sum of their data size is equal to that of original image
    original_size = get_rgbe_data_size(image_path)
    accumulated_size = 0
    for i in range(row_count):
        filename = "%s/%d.hdr"%(temp_file_path, i)
        accumulated_size += get_rgbe_data_size(filename)
    if accumulated_size == original_size:
        print("Success! The sum of data size of each row equals to that of the whole image.")
    else:
        print("Failed! The original size is %d, while the accumulated size is %d."%(original_size, accumulated_size))

    # We randomly change the pixel values of a row and compare the size change.
    row_to_be_changed = random.randint(0, row_count - 1)
    for i in range(image.shape[1]):
        for j in range(3):
            image[row_to_be_changed, i, j] += random.uniform(0, 0.5)

    # We save the whole image first and get its size
    new_image_path = "./temp/new_image.hdr"
    cv2.imwrite(new_image_path, image)
    current_size = get_rgbe_data_size(new_image_path)

    # Get the original size of the row of the image
    original_row_size = get_rgbe_data_size("%s/%d.hdr"%(temp_file_path, row_to_be_changed))

    # Save the changed row as image and get the new size
    row_image_path = "./temp/changed_row.hdr"
    cv2.imwrite(row_image_path, image[row_to_be_changed : row_to_be_changed + 1, :, :])
    current_row_size = get_rgbe_data_size(row_image_path)

    if current_row_size - original_row_size == current_size - original_size:
        print("Success! The size change of the whole image equals to the size change of the modified row.")
    else:
        print("Failed! The size change computed with whole image is %d, but that with rows is %d"
              %(current_size - original_size, current_row_size - original_row_size))