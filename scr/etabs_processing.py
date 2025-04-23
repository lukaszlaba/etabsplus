import comtypes.client
#import csv
from tabulate import tabulate
import os

ETABSObject = None
SapModel = None

eUnit_dict = {'kip_ft_F': 4 ,'KN_m_C': 6, }

class Analysis_Options:
    P_max = True
    P_min = True
    P_abs = True
    V2_abs = True
    V3_abs = True
    T_abs = True
    M2_abs = True
    M3_min = True
    M3_max = True
    M3_abs = True
    Mtot_abs = True
    Vtot_abs = True
    PV2_abs = True
    PV3_abs = True
    PV_abs = True
    sigma_PM2_abs = True
    sigma_PM3_abs = True
    sigma_PM_abs = True
    ends_only = True
    reduce_LC_name = True

def connect():
    global ETABSObject, SapModel
    ETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = ETABSObject.SapModel
    set_unitsystem('KN_m_C')

def set_unitsystem(eUnit: str='KN_m_C'):

    #https://docs.csiamerica.com/help-files/etabs-api-2016/html/16d95aba-00c9-f947-5e62-6b18045ef3d7.htm
    #https://docs.csiamerica.com/help-files/etabs-api-2016/html/cff40d28-9b1a-7f00-cfb9-0386da2464cc.htm
    SapModel.SetPresentUnits(eUnit_dict[eUnit])

def get_model_filename() -> str:
    return os.path.basename(SapModel.GetModelFilename())

def get_lcs_list(filter_calulated_only: bool=False) -> list[str]:
    all_combinations = SapModel.RespCombo.GetNameList()[1]
    combination_list = []
    if filter_calulated_only:
        example_frame_mumber = SapModel.FrameObj.GetNameList()[1][0]
        for combo in all_combinations:
            # add this combo to output and try het results for example_frame_mumber to check there are results
            SapModel.Results.Setup.SetComboSelectedForOutput(combo)
            status = SapModel.Results.FrameForce(example_frame_mumber, 0)[-1]
            SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
            if status == 0:  # 0 means success
                combination_list.append(combo)
    else:
        combination_list = all_combinations
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    return combination_list

def get_cs_list() -> list[str]:
    cases = SapModel.LoadCases.GetNameList()[1]
    return cases

def get_groups_list() -> list[str]:
    groups = SapModel.GroupDef.GetNameList()[1]
    if groups[0] == 'All': groups = groups[1:]
    groups = list(groups)
    groups.sort()
    return groups

def get_frame_props_list() -> list[str]:
    frame_props = SapModel.PropFrame.GetAllFrameProperties()[1]
    frame_props = list(frame_props)
    frame_props.sort()
    return frame_props

def get_frame_list_for_group(group_name: str) -> list[str]:
    number_selected, object_types, object_names, _  = SapModel.GroupDef.GetAssignments(group_name)
    selected_frames = []
    for i in range(number_selected):
        if object_types[i] == 2:
            selected_frames.append(object_names[i])
    return selected_frames

def get_frame_list_for_prop(prop_name: str) -> list[str]:
    frames = []
    frame_data = ETABSObject.SapModel.FrameObj.GetAllFrames()
    frame_numbers = frame_data[1]
    frame_sections = frame_data[2]
    for f, s in zip(frame_numbers, frame_sections):
        if s == prop_name:
            frames.append(f)
    return frames

def get_frame_list_current_selected():
    number_selected, object_types, object_names, _  = SapModel.SelectObj.GetSelected()
    selected_frames = []
    for i in range(number_selected):
        if object_types[i] == 2:
            selected_frames.append(object_names[i])
    return selected_frames

def sigma(P=100E3, M22=50E3, M33=50E3, b=0.5, h=1.2):

    P = abs(P)
    M22 = abs(M22)
    M33 = abs(M33)
    W22 = h*b**2/6
    W33 = b*h**2/6
    A = h * b
    return (P/A + M22/W22 + M33/W33)*1E-6

b = 0.25
h = 0.8

def get_report(framelist, lc_list, progress=None):
    #------adding lc
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    for lc in list(lc_list):
        SapModel.Results.Setup.SetComboSelectedForOutput(lc)
    # future add cases SetCaseSelectedForOutput(case))
    #----------------------
    P_max = 0
    P_max_record = None

    P_maxabs = 0
    P_maxabs_record = None

    P_min = 0
    P_min_record = None

    V2_maxabs = 0
    V2_maxabs_record = None

    V3_maxabs = 0
    V3_maxabs_record = None

    T_maxabs = 0
    T_maxabs_record = None

    M2_maxabs = 0
    M2_maxabs_record = None

    M3_maxabs = 0
    M3_maxabs_record = None

    M3_max = 0
    M3_max_record = None

    M3_min = 0
    M3_min_record = None

    Mtot_maxabs = 0
    Mtot_maxabs_record = None

    Vtot_maxabs = 0
    Vtot_maxabs_record = None

    NM3signatot_maxabs = 0
    NM3signatot_maxabs_record = None

    NM2signatot_maxabs = 0
    NM2signatot_maxabs_record = None

    NMsignatot_maxabs = 0
    NMsignatot_maxabs_record = None


    #PV2, PV3, PV

    #------------------------
    frame_results = []
    total = len(framelist)
    n = 0
    for frame in framelist:

        #print(SapModel.PropFrame.GetArea(sectionName))
        #print(SapModel.PropFrame.GetArea(sectionName))
        #print(SapModel.GetSectProps)
        #https://docs.csiamerica.com/help-files/etabs-api-2016/html/7e0e26e6-6e25-6b5a-c523-003da72307e8.htm



        NumberResults,Obj, ObjSta,Elm,ElmSta,LoadCase,StepType, StepNum, P, V2, V3, T, M2, M3, Status = SapModel.Results.FrameForce(frame, 0)

        obj_ends = [0, max(ObjSta)]

        for i in range(len(P)):
            if Analysis_Options.ends_only:
                if not ObjSta[i] in obj_ends:
                    continue

            objsta = str(round(ObjSta[i],2))
            if ObjSta[i] == obj_ends[0]: objsta = str(round(ObjSta[i],2)) + '(i)'
            if ObjSta[i] == obj_ends[1]: objsta = str(round(ObjSta[i],2)) + '(j)'

            p = P[i]
            v2 = V2[i]
            v3 = V3[i]
            t = T[i]
            m2 = M2[i]
            m3 = M3[i]
            mtot = (m2**2 + m3**2)**0.5
            vtot = (v2**2 + v3**2)**0.5
            nm3signatot = sigma(p*1E3, 0, m3*1E3, b, h)
            nm2signatot = sigma(p*1E3, m2*1E3, 0, b, h)
            nmsignatot = sigma(p*1E3, m2*1E3, m3*1E3, b, h)


            this_record = ([frame, LoadCase[i], StepType[i], objsta, P[i], V2[i], V3[i], T[i], M2[i], M3[i]])

            if p > P_max:
                P_max = p
                P_max_record = [f'P_max={round(p,2)}'] + this_record
            if p < P_min:
                P_min = p
                P_min_record = [f'P_min={round(p,2)}'] + this_record


            if abs(p) > abs(P_maxabs):
                P_maxabs = abs(p)
                P_maxabs_record = [f'P_maxabs={round(abs(p),2)}'] + this_record


            if abs(v2) > abs(V2_maxabs):
                V2_maxabs = abs(v2)
                V2_maxabs_record = [f'V2_maxabs={round(abs(v2),2)}'] + this_record


            if abs(v3) >abs(V3_maxabs):
                V3_maxabs = abs(v3)
                V3_maxabs_record = [f'V3_maxabs={round(abs(v3),2)}'] + this_record


            if abs(t) >abs(T_maxabs):
                T_maxabs = abs(t)
                T_maxabs_record = [f'T_maxabs={round(abs(t),2)}'] + this_record


            if abs(m2) >abs(M2_maxabs):
                M2_maxabs = abs(m2)
                M2_maxabs_record = [f'M2_maxabs={round(abs(m2),2)}'] + this_record

            if abs(m3) >abs(M3_maxabs):
                M3_maxabs = abs(m3)
                M3_maxabs_record = [f'M3_maxabs={round(abs(m3),2)}'] + this_record


            if m3 > M3_max:
                M3_max = m3
                M3_max_record = [f'M3_max={round(m3,2)}'] + this_record
            if m3 < M3_min:
                M3_min = m3
                M3_min_record = [f'M3_min={round(m3,2)}'] + this_record



            if abs(mtot) >abs(Mtot_maxabs):
                Mtot_maxabs = abs(mtot)
                Mtot_maxabs_record = [f'M_tot={round(abs(mtot),2)}'] + this_record



            if abs(vtot) >abs(Vtot_maxabs):
                Vtot_maxabs = abs(vtot)
                Vtot_maxabs_record = [f'V_tot={round(abs(vtot),2)}'] + this_record

            if abs(nm3signatot) >abs(NM3signatot_maxabs):
                NM3signatot_maxabs = abs(nm3signatot)
                NM3signatot_maxabs_record = [f'P-M3 sigma_maxabs={round(abs(nm3signatot),2)}[MPa]'] + this_record


            if abs(nm2signatot) >abs(NM2signatot_maxabs):
                NM2signatot_maxabs = abs(nm2signatot)
                NM2signatot_maxabs_record = [f'P-M2 sigma_maxabs={round(abs(nm2signatot),2)}[MPa]'] + this_record

            if abs(nmsignatot) >abs(NMsignatot_maxabs):
                NMsignatot_maxabs = abs(nmsignatot)
                NMsignatot_maxabs_record = [f'P-M sigma_maxabs={round(abs(nmsignatot),2)}[MPa]'] + this_record
            #--------------progress ----
        if progress: progress.set_progress_1(int(n/total*100))
        else: print(f'{n} of {total}')
        n += 1
    if progress: progress.set_progress_1()
    #------------making output table

    out = []
    if Analysis_Options.P_max: out.append(P_max_record)
    if Analysis_Options.P_min: out.append(P_min_record)

    if Analysis_Options.P_abs: out.append(P_maxabs_record)

    if Analysis_Options.V2_abs: out.append(V2_maxabs_record)
    if Analysis_Options.V3_abs: out.append(V3_maxabs_record)

    if Analysis_Options.T_abs: out.append(T_maxabs_record)

    if Analysis_Options.M2_abs: out.append(M2_maxabs_record)

    if Analysis_Options.M3_abs: out.append(M3_maxabs_record)


    if Analysis_Options.M3_max: out.append(M3_max_record)
    if Analysis_Options.M3_min: out.append(M3_min_record)

    if Analysis_Options.Mtot_abs: out.append(Mtot_maxabs_record)


    if Analysis_Options.sigma_PM2_abs: out.append(NM2signatot_maxabs_record)
    if Analysis_Options.sigma_PM3_abs: out.append(NM3signatot_maxabs_record)
    if Analysis_Options.sigma_PM_abs: out.append(NMsignatot_maxabs_record)

    if Analysis_Options.Vtot_abs: out.append(Vtot_maxabs_record)


    # LC name reduce
    if Analysis_Options.reduce_LC_name:
        for row in out:
            if len(row[2])>20:
                row[2] = row[2][:20]+'..'

    col_name = ['Case' ,"Frame", "LC", "StepType", "ObjSta[m]", "P[kN]", "V2[kN]", "V3[kN]", "T[kNm]", "M2[kNm]", "M3[kNm]"]
    print('\n\n')

    report = ''

    if Analysis_Options.ends_only:
        report += '(Member ends analysis only - for connection design purpose)\n'
    else:
        report += '(Entire member length included for analysis)\n'
    report += tabulate(out, headers=col_name, tablefmt='psql', floatfmt=".2f")

    return report



if __name__ == '__main__':
    connect()
    print(get_model_filename())
    print(get_lcs_list())
    print(get_groups_list())
    print(get_frame_props_list())
    print(get_frame_list_for_group('L30_W1'))
    print(get_frame_list_for_prop('FW600X500X32X56'))
    print(get_frame_list_current_selected())

    test_frame_list = get_frame_list_for_group('L30_W1')
    test_lc_list = get_lcs_list()[:5]
    print(get_report(test_frame_list, test_lc_list))
    pass

