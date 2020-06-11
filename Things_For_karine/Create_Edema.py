__author__ = 'Brian M Anderson'
# Created on 6/11/2020

'''
This works by taking the rigid registration from the disease and mapping it over to the flair image

Then, this geometry is used as a centroid and HU's to create a region grown algorithm
'''
from connect import *

primary_exam = 'MR 78'
edema = 'MR 73'
roi_name = r"Brain metastasis 1"
new_roi = roi_name + '_Edema_BMA'
case = get_current("Case")
patient = get_current("Patient")
rois_in_case = []
for name in case.PatientModel.RegionsOfInterest:
    rois_in_case.append(name.Name)
if new_roi not in rois_in_case:
    case.PatientModel.CreateRoi(Name=new_roi, Color='Blue')
if not case.PatientModel.StructureSets[edema].RoiGeometries[roi_name].HasContours():
    case.PatientModel.CopyRoiGeometries(SourceExamination=case.Examinations[primary_exam], TargetExaminationNames=[edema], RoiNames=[roi_name])

centroid = case.PatientModel.StructureSets[edema].RoiGeometries[roi_name].GetCenterOfRoi()
centroid = {'x': centroid.x, 'y': centroid.y, 'z': centroid.z}
HU_Dict = case.Examinations[edema].Series[0].ImageStack.GetIntensityStatistics(RoiName=roi_name)
lower = HU_Dict['Average']
for i in lower:
    lower = i.Key
upper = 9999
case.PatientModel.StructureSets[edema].RoiGeometries[new_roi].CreateGeometryThroughRegionGrowing3D(SeedPoints=[centroid], LowThreshold=lower, HighThreshold=upper,Radius=1.)
case.PatientModel.StructureSets[edema].SimplifyContours(RoiNames=[new_roi], RemoveHoles3D=True)
patient.Save()