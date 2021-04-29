__author__ = 'Brian M Anderson'
# Created on 4/29/2021
import os
import SimpleITK as sitk
import pydicom
import numpy as np


def add_frame_of_reference_uid(path):
    file_reader = sitk.ImageFileReader()
    for root, dirs, files in os.walk(path):
        has_ref_file = os.path.join(root, 'HasFrameOfReferenceUID.txt')
        if os.path.exists(has_ref_file):
            continue
        dicom_files = [os.path.join(root, i) for i in files if i.endswith('.dcm')]
        if dicom_files:
            base_uid = '1.3.12.2.1107.5.1.4.95642.30000017092813491242400000003.{}'.format(np.random.randint(9999))
            for file in dicom_files:
                file_reader.SetFileName(file)
                file_reader.Execute()
                if not file_reader.HasMetaDataKey("0020|0052"):
                    ds = pydicom.read_file(file)
                    ds.FrameOfReferenceUID = base_uid
                    pydicom.write_file(filename=file, dataset=ds)
            fid = open(has_ref_file, 'w+')
            fid.close()
    return None


if __name__ == '__main__':
    pass
