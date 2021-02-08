__author__ = 'Brian M Anderson'
# Created on 6/11/2020

'''
This works by taking the rigid registration from the disease and mapping it over to the flair image

Then, this geometry is used as a centroid and HU's to create a region grown algorithm
'''
from connect import *

primary_exam = 'MR 78'
edema_exam = 'MR 73'
roi_name_base = r"Brain metastasis {}"

case = get_current("Case")
patient = get_current("Patient")
mets_rois = []
rois_in_case = []
for name in case.PatientModel.RegionsOfInterest:
    rois_in_case.append(name.Name)
for i in range(999):
    if roi_name_base.format(i) in rois_in_case:
        mets_rois.append(roi_name_base.format(i))
for met_roi_name in mets_rois:
    if not case.PatientModel.StructureSets[primary_exam].RoiGeometries[met_roi_name].HasContours():
        continue
    edema_roi_name = met_roi_name + '_Edema_BMA'
    if edema_roi_name not in rois_in_case:
        case.PatientModel.CreateRoi(Name=edema_roi_name, Color='Blue')
    if not case.PatientModel.StructureSets[edema_exam].RoiGeometries[met_roi_name].HasContours():
        case.PatientModel.CopyRoiGeometries(SourceExamination=case.Examinations[primary_exam], TargetExaminationNames=[edema_exam], RoiNames=[met_roi_name])

    centroid = case.PatientModel.StructureSets[edema_exam].RoiGeometries[met_roi_name].GetCenterOfRoi()
    centroid = {'x': centroid.x, 'y': centroid.y, 'z': centroid.z}
    HU_Dict = case.Examinations[edema_exam].Series[0].ImageStack.GetIntensityStatistics(RoiName=met_roi_name)
    lower = HU_Dict['Average']
    for i in lower:
        lower = i.Key
    roi_volume = case.PatientModel.StructureSets[primary_exam].RoiGeometries[met_roi_name].GetRoiVolume()
    upper = 9999
    case.PatientModel.StructureSets[edema_exam].RoiGeometries[edema_roi_name].CreateGeometryThroughRegionGrowing3D(SeedPoints=[centroid], LowThreshold=lower,
                                                                                                                   HighThreshold=upper,Radius=1.,
                                                                                                                   NumberOfIncrementalSteps=1,
                                                                                                                   MaxVolume=10*roi_volume, GrowFromHighThreshold=True)
    case.PatientModel.StructureSets[edema_exam].SimplifyContours(RoiNames=[edema_roi_name], RemoveHoles3D=True)
    subtract_roi = met_roi_name + '_Peritumeral_Edema_BMA'
    if subtract_roi not in rois_in_case:
        case.PatientModel.CreateRoi(Name=subtract_roi, Color='Red')
    case.PatientModel.RegionsOfInterest[subtract_roi].CreateAlgebraGeometry(
        Examination=case.Examinations[edema_exam], Algorithm="Auto",
        ExpressionA={'Operation': "Union", 'SourceRoiNames': [edema_roi_name],
                     'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0,
                                        'Right': 0, 'Left': 0}},
        ExpressionB={'Operation': "Union", 'SourceRoiNames': [met_roi_name],
                     'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0,
                                        'Right': 0, 'Left': 0}}, ResultOperation="Subtraction",
        ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0,
                              'Left': 0})
    break
patient.Save()