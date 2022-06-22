import cv2
import numpy as np

import random
from struct import pack

def find_n(x:float)->int:
    '''
    To compute m*2^n
    :param x:
    :return: the first is m, the second is n
    '''
    m=x
    n=0
    while(m<1):
        n=n-1
        m=x/(2**n)

    return n+1

def get_e_from_float(RGB, normalize='minmax'):
    if RGB.ndim == 3:
        zeros=np.sum(RGB,axis=2)==0
        max_value = np.max(RGB, axis=2)
        e = np.floor(np.log2(max_value)) + 129
        e[zeros]=0
        if normalize == 'minmax':
            e_min = np.min(e)
            e_max = np.max(e)
            e = (e - e_min) / (e_max - e_min)
        elif normalize == 'log':
            e_max = np.max(e)
            e = np.log(e + 1) / np.log(e_max + 1)
        else:
            raise NotImplementedError
        e = np.expand_dims(e, axis=2)
        return e
    else:
        raise NotImplementedError


def rgbe2float(rgbe: np.ndarray) -> np.ndarray:
    res = np.zeros((rgbe.shape[0], rgbe.shape[1], 3))
    p = rgbe[:, :, 3] > 0
    m = 2.0 ** (rgbe[:, :, 3][p] - 136.0)
    res[:, :, 0][p] = rgbe[:, :, 0][p] * m
    res[:, :, 1][p] = rgbe[:, :, 1][p] * m
    res[:, :, 2][p] = rgbe[:, :, 2][p] * m
    return np.array(res, dtype=np.float32)


def float2rgbe(RGB: np.ndarray) -> np.ndarray:
    '''
    Convert from RGB to rgbe
    :param RGB:
    :return:
    '''
    rgbe = np.zeros([RGB.shape[0], RGB.shape[1], 4], dtype=float)
    p = np.max(RGB, axis=2)
    find_n_v = np.vectorize(find_n)
    p = find_n_v(p)
    p = np.expand_dims(p, 2)
    p = np.array(p, dtype=float)
    rgbe[:, :, :3] = RGB * 256 / (2 ** p)
    rgbe[:, :, 3:4] = p + 128

    return rgbe


def readhdr(fileName: str) -> np.ndarray:
    '''
    Directly read the rgbe values of the given image file
    :param fileName:
    :return:
    '''
    fileinfo = {}
    with open(fileName, 'rb') as fd:
        tline = fd.readline().strip()
        if len(tline) < 3 or tline[:2] != b'#?':
            print('invalid header')
            return
        fileinfo['identifier'] = tline[2:]

        # while(tline[:1]==b'#'):
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

        data = [d for d in fd.read()]
        height, width = fileinfo['height'], fileinfo['width']
        if width < 8 or width > 32767:
            data.resize((height, width, 4))
            print("error")
            return rgbe2float(data)

        img = np.zeros((height, width, 4))
        dp = 0
        for h in range(height):
            if data[dp] != 2 or data[dp + 1] != 2:
                print('this file is not run length encoded')
                print(data[dp:dp + 4])
                return
            if data[dp + 2] * 256 + data[dp + 3] != width:
                print('wrong scanline width')
                return
            dp += 4
            for i in range(4):
                ptr = 0
                while (ptr < width):
                    if data[dp] > 128:
                        count = data[dp] - 128
                        if count == 0 or count > width - ptr:
                            print('bad scanline data')
                        img[h, ptr:ptr + count, i] = data[dp + 1]
                        ptr += count
                        dp += 2
                    else:
                        count = data[dp]
                        dp += 1
                        if count == 0 or count > width - ptr:
                            print('bad scanline data')
                        img[h, ptr:ptr + count, i] = data[dp: dp + count]
                        ptr += count
                        dp += count
        return img


def savehdr(filename: str, rgbe: np.ndarray) -> bool:
    '''
    Directly save the rgbe data to ".hdr" image file.
    Please note that the header is customized and may be
    different from images saved by some public libraries such as OpenCV.
    :param filename:
    :param rgbe:
    :return:
    '''
    if (rgbe.shape[1] < 8 or rgbe.shape[1] > 32767):
        print("The width of the hdr image must be in range(8,32767)")
        return False

    rgbe = rgbe.astype(int)

    with open(filename, 'wb') as fw:
        fw.write(b'#?RGBE')
        fw.write(b'\n')
        fw.write(b'FORMAT=32-bit_rle_rgbe')
        fw.write(b'\n')
        fw.write(b'\n')

        fw.write(b'-Y ')
        fw.write(bytes(str(rgbe.shape[0]), 'ansi'))
        fw.write(b' +X ')
        fw.write(bytes(str(rgbe.shape[1]), 'ansi'))
        fw.write(b'\n')

        for j in range(rgbe.shape[0]):
            fw.write(pack('B', 2))
            fw.write(pack('B', 2))
            fw.write(pack('B', int(rgbe.shape[1] / 256)))
            fw.write(pack('B', int(rgbe.shape[1] % 256)))

            for i in range(4):
                value = rgbe[j, 0, i]
                same_length = 1
                dif_list = []
                dif_list.append(rgbe[j, 0, i])
                for k in range(1, rgbe.shape[1]):
                    if (rgbe[j, k, i] == value):
                        if (len(dif_list) > 1):
                            dif_list.pop(-1)
                            fw.write(pack('B', len(dif_list)))
                            for _, d in enumerate(dif_list):
                                fw.write(pack('B', d))
                            dif_list.clear()
                            dif_list.append(value)

                        if (same_length < 127):
                            same_length = same_length + 1
                        else:
                            fw.write(pack('B', 255))
                            fw.write(pack('B', value))
                            same_length = 1
                    elif (rgbe[j, k, i] != value and same_length == 1):
                        value = rgbe[j, k, i]
                        if (len(dif_list) < 127):
                            dif_list.append(rgbe[j, k, i])
                        else:
                            fw.write(pack('B', 127))
                            for _, d in enumerate(dif_list):
                                fw.write(pack('B', d))
                            dif_list.clear()
                            dif_list.append(value)
                    elif (rgbe[j, k, i] != value and same_length > 1):
                        fw.write(pack('B', 128 + same_length))
                        fw.write(pack('B', value))
                        value = rgbe[j, k, i]
                        same_length = 1
                        dif_list = [value]

                if (len(dif_list) > 1):
                    fw.write(pack('B', len(dif_list)))
                    for _, d in enumerate(dif_list):
                        fw.write(pack('B', d))
                elif (same_length > 1):
                    fw.write(pack('B', 128 + same_length))
                    fw.write(pack('B', value))
                else:
                    fw.write(pack('B', 1))
                    fw.write(pack('B', value))
    fw.close()
    return True
