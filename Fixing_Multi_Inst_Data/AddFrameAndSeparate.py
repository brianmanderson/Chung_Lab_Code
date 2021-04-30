__author__ = 'Brian M Anderson'
# Created on 4/29/2021
import os
import SimpleITK as sitk
import numpy as np
import pydicom


def add_frame_and_separate(path):
    image_reader = sitk.ImageFileReader()
    for root, dirs, files in os.walk(path):
        finished = os.path.join(root, 'Finished.txt')
        if os.path.exists(finished):
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
                    folder_dict[rows_cols] = {'files': [], 'uid': None, 'needs_uid': []}
                if image_reader.HasMetaDataKey("0020|0052"):
                    if folder_dict[rows_cols]['uid'] is None:
                        folder_dict[rows_cols]['uid'] = image_reader.GetMetaData("0020|0052")
                    folder_dict[rows_cols]['needs_uid'].append(False)
                else:
                    folder_dict[rows_cols]['needs_uid'].append(True)
                folder_dict[rows_cols]['files'].append(file)
            for key in folder_dict:
                base_uid = folder_dict[key]['uid']
                if base_uid is None:
                    base_uid = '1.3.12.2.1107.5.1.4.95642.30000017092813491242400000003.{}'.format(
                        np.random.randint(9999))
                file_list = np.asarray(folder_dict[key]['files'])[folder_dict[key]['needs_uid']]
                for file in file_list:
                    ds = pydicom.read_file(file)
                    ds.FrameOfReferenceUID = base_uid
                    pydicom.write_file(filename=file, dataset=ds)
                if len(folder_dict) > 1:
                    os.makedirs(os.path.join(root, key))
                    for file in folder_dict[key]['files']:
                        file_name = os.path.split(file)[-1]
                        os.rename(file, os.path.join(root, key, file_name))
                    fid = open(os.path.join(root, key, 'Finished.txt'), 'w+')
                    fid.close()
                else:
                    fid = open(finished, 'w+')
                    fid.close()
    return None


if __name__ == '__main__':
    pass
