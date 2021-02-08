__author__ = 'Brian M Anderson'
# Created on 1/27/2021

from connect import *


def rigid_and_map(case, primary_exam, secondary_exam, exam_names, brain_roi, gtv_roi):
    if not case.PatientModel.StructureSets[primary_exam.Name].RoiGeometries[brain_roi].HasContours():
        ct_exams = [i for i in exam_names if i.startswith('CT')]
        primary_ct = None
        for ct_exam in ct_exams:
            if case.PatientModel.StructureSets[ct_exam].RoiGeometries[brain_roi].HasContours():
                primary_ct = ct_exam
        assert primary_ct is not None, 'Trying to find a CT with a brain contour, none was found'
        rigid_registration(case=case, primary_exam=primary_exam.Name, ct_exam=primary_ct)
        case.PatientModel.CopyRoiGeometries(SourceExamination=case.Examinations[primary_ct],
                                            TargetExaminationNames=[primary_exam.Name],
                                            RoiNames=[brain_roi])
    if not case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[brain_roi].HasContours():
        rigid_registration(case=case, primary_exam=primary_exam.Name, ct_exam=secondary_exam.Name)
        case.PatientModel.CopyRoiGeometries(SourceExamination=primary_exam,
                                            TargetExaminationNames=[secondary_exam.Name],
                                            RoiNames=[brain_roi])
    if not case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[gtv_roi].HasContours():
        rigid_registration(case=case, primary_exam=primary_exam.Name, ct_exam=secondary_exam.Name)
        case.PatientModel.CopyRoiGeometries(SourceExamination=primary_exam,
                                            TargetExaminationNames=[secondary_exam.Name],
                                            RoiNames=[gtv_roi])


def main(t2_flair_name, gtv_name):
    primary_exam = get_current("Examination")
    case = get_current("Case")
    patient = get_current("Patient")
    exam_names = [e.Name for e in case.Examinations]
    assert t2_flair_name in exam_names, 'The T2 Flair image defined is not present in the set'
    secondary_exam = case.Examinations[t2_flair_name]

    rois_in_case = []
    for roi in case.PatientModel.RegionsOfInterest:
        rois_in_case.append(roi.Name)

    gtv_roi = None
    brain_roi = None
    for roi in rois_in_case:
        if roi.lower() == gtv_name.lower():
            gtv_roi = roi
        elif roi.lower() == 'brain':
            brain_roi = roi
    assert gtv_roi is not None, 'The program is looking for an roi that starts with GTV_M'
    assert brain_roi is not None, 'Needs a brain roi'
    rigid_and_map(case=case, primary_exam=primary_exam, secondary_exam=secondary_exam, brain_roi=brain_roi,
                  gtv_roi=gtv_roi, exam_names=exam_names)
    mapping_exams(patient=patient, case=case, secondary_exam=secondary_exam, brain_roi=brain_roi, rois_in_case=rois_in_case,
                  gtv_roi=gtv_roi)


def mapping_exams(patient, case, secondary_exam, gtv_roi, brain_roi, rois_in_case):
    expanded_roi = '{}_Expanded'.format(gtv_roi)
    if expanded_roi not in rois_in_case:
        case.PatientModel.CreateRoi(Name=expanded_roi, Color="SaddleBrown", Type="Organ", TissueName=None,
                                    RbeCellTypeName=None, RoiMaterial=None)
        rois_in_case.append(expanded_roi)
    case.PatientModel.RegionsOfInterest[expanded_roi].CreateAlgebraGeometry(Examination=secondary_exam,
                                                                            Algorithm="Auto",
                                   ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [gtv_roi],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 1, 'Inferior': 1,
                                                                   'Anterior': 1, 'Posterior': 1, 'Right': 1,
                                                                   'Left': 1}},
                                   ExpressionB={'Operation': "Intersection", 'SourceRoiNames': [brain_roi],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}}, ResultOperation="Intersection",
                                   ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0,
                                                         'Posterior': 0, 'Right': 0, 'Left': 0})
    HU_Max = case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[expanded_roi].GetImageIntensityStatisticsForRoi(Percentile=95)
    HU_Max = HU_Max['Max']
    print(HU_Max)
    for i in HU_Max:
        print(i)
        break
    HU_Max = i
    percentage_max = HU_Max * 0.75

    threshold_roi = '{}_Threshold'.format(gtv_roi)
    if threshold_roi not in rois_in_case:
        case.PatientModel.CreateRoi(Name=threshold_roi, Color="Yellow", Type="Organ", TissueName=None,
                                    RbeCellTypeName=None, RoiMaterial=None)
        rois_in_case.append(threshold_roi)
    case.PatientModel.RegionsOfInterest[threshold_roi].GrayLevelThreshold(Examination=secondary_exam,
                                                                          LowThreshold=percentage_max,
                                                                          HighThreshold=percentage_max * 10,
                                                                          PetUnit="", CbctUnit=None, BoundingBox=None)
    threshold_in_brain = '{}_threshold_in_Brain'.format(gtv_roi)
    if threshold_in_brain not in rois_in_case:
        rois_in_case.append(threshold_in_brain)
        case.PatientModel.CreateRoi(Name=threshold_in_brain, Color="Red", Type="Organ", TissueName=None,
                                    RbeCellTypeName=None, RoiMaterial=None)
    patient.Save()
    case.PatientModel.RegionsOfInterest[threshold_in_brain].CreateAlgebraGeometry(Examination=secondary_exam,
                                                                            Algorithm="Auto",
                                   ExpressionA={'Operation': "Intersection", 'SourceRoiNames': [threshold_roi],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}},
                                   ExpressionB={'Operation': "Intersection", 'SourceRoiNames': [brain_roi],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}}, ResultOperation="Intersection",
                                   ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0,
                                                         'Posterior': 0, 'Right': 0, 'Left': 0})
    # case.PatientModel.RegionsOfInterest[threshold_roi].DeleteRoi()

    new_rois = []
    if '{}_0'.format(threshold_in_brain) in rois_in_case:
        new_rois.append('{}_0'.format(threshold_in_brain))
    else:
        print(threshold_in_brain)
        case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[threshold_in_brain].GetConnectedComponents(MaxVolume=999, MinVolume=0, MaxNumberOfComponents=999)
        rois_in_case = []
        for roi in case.PatientModel.RegionsOfInterest:
            rois_in_case.append(roi.Name)
        new_rois = []
        if '{}_0'.format(threshold_in_brain) in rois_in_case:
            new_rois.append('{}_0'.format(threshold_in_brain))
    # case.PatientModel.RegionsOfInterest[threshold_in_brain].DeleteRoi()
    print(new_rois)
    if new_rois:
        seed_grown = '{}_Seed_Grown'.format(gtv_roi)
        if seed_grown not in rois_in_case:
            rois_in_case.append(seed_grown)
            case.PatientModel.CreateRoi(Name=seed_grown, Color="Red", Type="Organ", TissueName=None,
                                        RbeCellTypeName=None, RoiMaterial=None)
        centroids = []
        for roi in new_rois:
            print(new_rois)
            HU_Max = case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[
                roi].GetImageIntensityStatisticsForRoi(Percentile=95)
            HU_Max = HU_Max['Max']
            print(HU_Max)
            for i in HU_Max:
                print(i)
                break
            HU_Max = i
            percentage_max = HU_Max * 0.75
            centroid = case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[roi].GetCenterOfRoi()
            centroids.append({'x': centroid.x, 'y': centroid.y, 'z': centroid.z})
            print(centroids)
            case.PatientModel.StructureSets[secondary_exam.Name].RoiGeometries[
                roi].CreateGeometryThroughRegionGrowing3D(SeedPoints=centroids, Radius=1., LowThreshold=percentage_max,
                                                                 HighThreshold=HU_Max * 10, ThresholdUnit='',
                                                                 MaxVolume=0.0, NumberOfIncrementalSteps=100, GrowFromHighThreshold=False)
        seed_in_brain = '{}_seed_in_Brain'.format(gtv_roi)
        if seed_in_brain not in rois_in_case:
            rois_in_case.append(seed_in_brain)
            case.PatientModel.CreateRoi(Name=seed_in_brain, Color="Blue", Type="Organ", TissueName=None,
                                        RbeCellTypeName=None, RoiMaterial=None)
        case.PatientModel.RegionsOfInterest[seed_in_brain].CreateAlgebraGeometry(Examination=secondary_exam,
                                                                                      Algorithm="Auto",
                                                                                      ExpressionA={
                                                                                          'Operation': "Intersection",
                                                                                          'SourceRoiNames': [
                                                                                              roi],
                                                                                          'MarginSettings': {
                                                                                              'Type': "Expand",
                                                                                              'Superior': 0,
                                                                                              'Inferior': 0,
                                                                                              'Anterior': 0,
                                                                                              'Posterior': 0,
                                                                                              'Right': 0,
                                                                                              'Left': 0}},
                                                                                      ExpressionB={
                                                                                          'Operation': "Intersection",
                                                                                          'SourceRoiNames': [brain_roi],
                                                                                          'MarginSettings': {
                                                                                              'Type': "Expand",
                                                                                              'Superior': 0,
                                                                                              'Inferior': 0,
                                                                                              'Anterior': 0,
                                                                                              'Posterior': 0,
                                                                                              'Right': 0,
                                                                                              'Left': 0}},
                                                                                      ResultOperation="Intersection",
                                                                                      ResultMarginSettings={
                                                                                          'Type': "Expand",
                                                                                          'Superior': 0, 'Inferior': 0,
                                                                                          'Anterior': 0,
                                                                                          'Posterior': 0, 'Right': 0,
                                                                                          'Left': 0})
        case.PatientModel.StructureSets[secondary_exam.Name].SimplifyContours(
            RoiNames=[seed_in_brain], RemoveHoles3D=True, RemoveSmallContours=False,
            ReduceMaxNumberOfPointsInContours=False, MaxNumberOfPoints=None,
            CreateCopyOfRoi=False, ResolveOverlappingContours=True)
        case.PatientModel.RegionsOfInterest['{}_Expanded'.format(gtv_roi)].DeleteRoi()
        case.PatientModel.RegionsOfInterest['{}_Threshold'.format(gtv_roi)].DeleteRoi()
        case.PatientModel.RegionsOfInterest['{}_Seed_Grown'.format(gtv_roi)].DeleteRoi()
        for roi in rois_in_case:
            if roi.startswith(threshold_in_brain):
                case.PatientModel.RegionsOfInterest[roi].DeleteRoi()

    patient.Save()


def create_external(case, ref_ct, ablation_ct):
    external_rois = [roi.Name for roi in case.PatientModel.RegionsOfInterest if roi.Type == 'External']
    if not external_rois:
        case.PatientModel.CreateRoi(Name="External", Color="Blue", Type="External",
                                    TissueName=None, RbeCellTypeName=None,
                                    RoiMaterial=None)
        external_roi = 'External'
    else:
        external_roi = external_rois[0]

    for exam_name in [ref_ct, ablation_ct]:
        exam = case.Examinations[exam_name]
        if not case.PatientModel.StructureSets[exam_name].RoiGeometries[external_roi].HasContours():
            case.PatientModel.RegionsOfInterest[external_roi].CreateExternalGeometry(Examination=exam)


def ComputeRigidRegistration(case, RefCT, AblationCT,):
    tag = {'Group': (0x020), 'Element': (0x0052)}
    perform_rigid_reg = True
    for registration in case.Registrations:
        if not registration.StructureRegistrations:
            continue
        to_frame_of_ref = registration.StructureRegistrations[0].FromExamination.EquipmentInfo.FrameOfReference
        from_frame_of_ref = registration.StructureRegistrations[0].ToExamination.EquipmentInfo.FrameOfReference
        tempout = [i.Name for i in case.Examinations if
                   i.GetStoredDicomTagValueForVerification(**tag)['FrameOfReferenceUID'] == to_frame_of_ref or
                   i.GetStoredDicomTagValueForVerification(**tag)['FrameOfReferenceUID'] == from_frame_of_ref]
        if RefCT in tempout and AblationCT in tempout:
            perform_rigid_reg = False

    if perform_rigid_reg:
        set_progress('Creating external, computing rigid')
        create_external(case=case, ref_ct=RefCT, ablation_ct=AblationCT)
        case.ComputeRigidImageRegistration(FloatingExaminationName=AblationCT, ReferenceExaminationName=RefCT,
                                           UseOnlyTranslations=False, HighWeightOnBones=False, InitializeImages=True,
                                           FocusRoisNames=[], RegistrationName=None)

    return None


def rigid_registration(case, primary_exam, ct_exam):
    tag = {'Group': (0x020), 'Element': (0x0052)}
    frame_of_ref_ref = \
        case.Examinations[primary_exam].GetStoredDicomTagValueForVerification(**tag)['FrameOfReferenceUID']
    frame_of_ref_sec = \
        case.Examinations[ct_exam].GetStoredDicomTagValueForVerification(**tag)['FrameOfReferenceUID']
    if frame_of_ref_ref != frame_of_ref_sec:
        ComputeRigidRegistration(case=case, RefCT=primary_exam, AblationCT=ct_exam)


if __name__ == '__main__':
    main(t2_flair_name='MR 1', gtv_name='GTV_MAF')
