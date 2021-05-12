__author__ = 'Brian M Anderson'
# Created on 4/29/2021
"""
This code was created to fix issues with multi-institutional MR data

The main errors are: lacking a FrameOfReferenceUID, and that multiple exams have the same SeriesInstanceUID within 
a single folder
"""

"""
First, we need to address the single folder issue
"""
path = r'Z:\A221208_AllianceTrial\06_Data_Release_For_MD_Anderson'
separate = False
if separate:
    from Separate_Files import separate_files_based_on_rows_cols
    separate_files_based_on_rows_cols(path=path)

"""
Next, we need to add a FrameOfReferenceUID to each file if it does not have one
"""
add_frame_of_reference = False
if add_frame_of_reference:
    from AddFrameOfReference import add_frame_of_reference_uid
    add_frame_of_reference_uid(path=path)

"""
Or we could do both combined
"""
add_frame_and_separate = True
if add_frame_and_separate:
    from AddFrameAndSeparate import write_in_parallel
    write_in_parallel(path=path)