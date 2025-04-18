import comtypes.client
import csv
from tabulate import tabulate



'''
Changelog:
- end force only option added

'''




def sigma(P=100E3, M22=50E3, M33=50E3, b=0.5, h=1.2):

    P = abs(P)
    M22 = abs(M22)
    M33 = abs(M33)
    W22 = h*b**2/6
    W33 = b*h**2/6
    A = h * b
    return (P/A + M22/W22 + M33/W33)*1E-6


# Connect to ETABS API
ETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
SapModel = ETABSObject.SapModel


#https://docs.csiamerica.com/help-files/etabs-api-2016/html/16d95aba-00c9-f947-5e62-6b18045ef3d7.htm
#https://docs.csiamerica.com/help-files/etabs-api-2016/html/cff40d28-9b1a-7f00-cfb9-0386da2464cc.htm
KN_m_C = 6
SapModel.SetPresentUnits(KN_m_C)



#https://docs.csiamerica.com/help-files/etabs-api-2016/html/acd799b2-657e-2a81-5810-297c90a07815.htm
_, combinations, _, = SapModel.RespCombo.GetNameList()


#filtered_combinations = combinations[:5]

filtered_combinations = []

# for name in combinations:
#     number = None
#     try:
#         number = int(name.split(':')[0])
#         #print(number)
#         if number < 6033:
#             print(name)
#             filtered_combinations.append(name)
#     except:
#         pass
#
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
# for each in list(filtered_combinations):
#     SapModel.Results.Setup.SetComboSelectedForOutput(each)

SapModel.Results.Setup.SetComboSelectedForOutput("EQD_X_E+(HOR)")
SapModel.Results.Setup.SetComboSelectedForOutput("EQD_Y_E+(HOR)")

#SapModel.Results.Setup.SetComboSelectedForOutput("[TL+]")



#SapModel.Results.Setup.SetComboSelectedForOutput("1012:1.00(11. DL-FLOOR_EQP_PIP)+1.00(65.[TL+])+1.00(52.WL(-X))+1.00(58.WL(CPI-,-X))")


#--------------------------------------------------

# Get selected frame elements
#number_selected, object_types, object_names, _  = SapModel.SelectObj.GetSelected()


#End only option

END_ONLY = True

# Get selected frame elements
group_name = 'L30_C1'
b = 0.25
h = 0.8
number_selected, object_types, object_names, _  = SapModel.GroupDef.GetAssignments(group_name)

selected_frames = []
for i in range(number_selected):
    if object_types[i] == 2:
        selected_frames.append(object_names[i])

#--------------------------------------------------

#https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm

# Extract forces for selected frames


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



frame_results = []
total = len(selected_frames)
n = 0
for frame in selected_frames:
    #print(frame)
    #print(SapModel.Results.FrameForce(frame, 0))
    print(f'{n} of {total}')
    n += 1
    NumberResults,Obj, ObjSta,Elm,ElmSta,LoadCase,StepType, StepNum, P, V2, V3, T, M2, M3, Status = SapModel.Results.FrameForce(frame, 0)

    #print(ObjSta)
    #print(LoadCase)
    #print(P)
    #print(ElmSta)

    obj_ends = [0, max(ObjSta)]

    for i in range(len(P)):
        if END_ONLY:
            if not ObjSta[i] in obj_ends:
                continue
        #print(i)
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
        #print(nmsignatot)
        #frame_results.append([frame, LoadCase[i], StepType[i], ElmSta[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])
        this_record = ([frame, LoadCase[i], StepType[i], ObjSta[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])

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

#--------------------------------------------------


out = []
#if P_max_record: out.append(P_max_record)
#if P_min_record: out.append(P_min_record)

if P_maxabs_record: out.append(P_maxabs_record)

if V2_maxabs_record: out.append(V2_maxabs_record)
if V3_maxabs_record: out.append(V3_maxabs_record)

#if T_maxabs_record: out.append(T_maxabs_record)

if M2_maxabs_record: out.append(M2_maxabs_record)

if M3_maxabs_record: out.append(M3_maxabs_record)


#if M3_max_record: out.append(M3_max_record)
#if M3_min_record: out.append(M3_min_record)

if Mtot_maxabs_record: out.append(Mtot_maxabs_record)


if NM2signatot_maxabs_record: out.append(NM2signatot_maxabs_record)
if NM3signatot_maxabs_record: out.append(NM3signatot_maxabs_record)
if NMsignatot_maxabs_record: out.append(NMsignatot_maxabs_record)


if Vtot_maxabs_record: out.append(Vtot_maxabs_record)






col_name = ['Case' ,"Frame", "LC", "StepType", "ObjSta", "P[kN]", "V2[kN]", "V3[kN]", "T[kNm]", "M2[kNm]", "M3[kNm]"]
print('\n\n')
try:
    print(f'Beam group {group_name} (b={b} x h={h} [m])')
except:
    pass

if END_ONLY:
    print('(Member ends analysis only - for connection design purpose)')
else:
    print('(Entire member length included for analysis)')


print(tabulate(out, headers=col_name, tablefmt='psql', floatfmt=".2f"))







# Save results to CSV file
# csv_filename = "ETABS_Frame_Forces.csv"
# with open(csv_filename, "w", newline="") as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(["Frame", "LC", "StepType", "ElmSta", "P", "V2", "V3", "T", "M2", "M3"])
#     writer.writerows(frame_results)

#print(f"Frame force results saved to {csv_filename}")

# Disconnect from ETABS
#ETABSObject.ApplicationExit(False)