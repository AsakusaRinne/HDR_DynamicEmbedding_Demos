## Introduction

This is a demo to indicate that the offset 0.5 in the conversion between RGB and rgbe has been removed in OpenCV library.

## Experiment Details

1. We read the image with OpenCV. Let the image read by OpenCV be ```IA```.
2. We read the rgbe data of the image directly. Let it be ```rgbe```.
3. We convert the ```rgbe``` to RGB data with and without offset 0.5 respectively.
4. We compare each pixel of the converted data and ```IA``` to see which one is the same with the result of OpenCV.

## Usage

Please clone this repository and follow the steps below.

```shell script
$ pip install -r requirements.txt
$ cd Conversion
$ python3 rgbe_rgb_conversion.py
```

By default, we provide an RGBE image named "Stairs.hdr" to run the test. You can replace with your own file and modify the ```image_path``` variable in the code.
