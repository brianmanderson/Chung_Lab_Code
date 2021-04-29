__author__ = 'Brian M Anderson'
# Created on 4/29/2021
import os
import SimpleITK as sitk
import numpy as np


def separate_files_based_on_rows_cols(path):
    image_reader = sitk.ImageFileReader()
    for root, dirs, files in os.walk(path):
        separated_text = os.path.join(root, 'Separated.txt')
        if os.path.exists(separated_text):
            continue
        dicom_files = [os.path.join(root, i) for i in files if i.endswith('.dcm')]
        if dicom_files:
            folder_dict = {}
            for file in dicom_files:
                print(file)
                image_reader.SetFileName(file)
                image_reader.Execute()
                rows_cols = '{}_{}'.format(image_reader.GetMetaData("0028|0010"), image_reader.GetMetaData("0028|0011"))
                if rows_cols not in folder_dict:
                    folder_dict[rows_cols] = []
                folder_dict[rows_cols].append(file)
            if len(folder_dict) > 1:
                for key in folder_dict:
                    os.makedirs(os.path.join(root, key))
                    for file in folder_dict[key]:
                        file_name = os.path.split(file)[-1]
                        os.rename(file, os.path.join(root, key, file_name))
                    fid = open(os.path.join(root, key, 'Separated.txt'), 'w+')
                    fid.close()
            else:
                fid = open(separated_text, 'w+')
                fid.close()
    return None


if __name__ == '__main__':
    pass
