## Introduction

This is a demo to indicate that RLE in RGBE image is only affected by the pixels in the same row. In other words, if the RLE proceeds to the end of a row, it will stop the current encoding at once and start a new turn of encoding from the beginning of the next row. 

## Experiment Details

There are two simple tests in the code.


**The first one: indicate the sum of encoding size of each row is equal to that of the whole image.**

1. We read the RGBE image with OpenCV and get the size of the data part of the file, which is defined as ```original_size```.
2. We crop each row of the image and save them to files.
3. We read the files generated in step2 and get the sum of the size of data part of the files, which is defined as ```Sum(part_size)```.
4. See if ```Sum(part_size) = original_size```

**The second one: indicate that after modifying pixels in the same row, the encoding of other rows are not changed.**

1. We read the image with OpenCV and Randomly select a row and get the original size of this row which is defined as ```original_single_row_size```.
2. We randomly modify the pixels in the selected row.
3. We save the whole image in the step2 with OpenCV and get its encoding data size ```current_size```.
4. We save the selected row of the image in step2 with OpenCV and get its encoding data size ```current_single_row_size```.
5. See if ```current_size - original_size = current_single_row_size - original_single_row_size```.

Though we do not verify every encoding byte, the probability of size being the same after random modification is close to 0. Therefore, we believe that the experiments above could indicate our opinion.

## Usage

Please clone this repository and follow the steps below.

```shell script
$ pip install -r requirements.txt
$ cd RLE
$ python3 rle_line_effect_test.py
```

By default, we provide an RGBE image named "Stairs.hdr" to run the test. You can replace with your own file and modify the ```image_path``` variable in the code.