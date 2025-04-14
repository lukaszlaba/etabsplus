import comtypes.client
import csv
from tabulate import tabulate

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

for name in combinations:
    number = None
    try:
        number = int(name.split(':')[0])
        #print(number)
        if number < 6033:
            print(name)
            filtered_combinations.append(name)
    except:
        pass

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
for each in list(filtered_combinations):
    SapModel.Results.Setup.SetComboSelectedForOutput(each)

#SapModel.Results.Setup.SetComboSelectedForOutput("EQ_Y_rsa_mod_39")
#SapModel.Results.Setup.SetComboSelectedForOutput("5083: +1.50(11. DL-FLOOR_EQP_PIP)+1.00(66.[TL-])+0.45(91.EQD_Z(VER))-1.50(92.EQD_X_E+(HOR))")

#--------------------------------------------------

# Get selected frame elements
#number_selected, object_types, object_names, _  = SapModel.SelectObj.GetSelected()

# Get selected frame elements
group_name = 'L30_W6'
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

M3_max = 0
M3_max_record = None

M3_min = 0
M3_min_record = None


frame_results = []
total = len(selected_frames)
n = 0
for frame in selected_frames:
    #print(frame)
    #print(SapModel.Results.FrameForce(frame, 0))
    print(f'{n} of {total}')
    n += 1
    NumberResults,Obj, ObjSta,Elm,ElmSta,LoadCase,StepType, StepNum, P, V2, V3, T, M2, M3, _ = SapModel.Results.FrameForce(frame, 0)
    for i in range(len(P)):
        #print(i)
        p = P[i]
        v2 = V2[i]
        v3 = V3[i]
        t = T[i]
        m2 = M2[i]
        m3 = M3[i]
        #frame_results.append([frame, LoadCase[i], StepType[i], ElmSta[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])
        this_record = ([frame, LoadCase[i], StepType[i], ElmSta[i], P[i], V2[i], V3[i], T[i], M2[i], M3[i]])

        if p > P_max:
            P_max = p
            P_max_record = [f'P_max={round(p,2)}'] + this_record
        if p < P_min:
            P_min = p
            P_min_record = [f'P_min={round(p,2)}'] + this_record

        if abs(v2) > abs(V2_maxabs):
            V2_maxabs = abs(v2)
            V2_maxabs_record = [f'V2_maxabs={round(v2,2)}'] + this_record


        if abs(v3) >abs(V3_maxabs):
            V3_maxabs = abs(v3)
            V3_maxabs_record = [f'V3_maxabs={round(v3,2)}'] + this_record


        if abs(t) >abs(T_maxabs):
           T_maxabs = abs(t)
           T_maxabs_record = [f'T_maxabs={round(t,2)}'] + this_record


        if abs(m2) >abs(M2_maxabs):
            M2_maxabs = abs(m2)
            M2_maxabs_record = [f'M2_maxabs={round(m2,2)}'] + this_record


        if m3 > M3_max:
            M3_max = m3
            M3_max_record = [f'M3_max={round(m3,2)}'] + this_record
        if m3 < M3_min:
            M3_min = m3
            M3_min_record = [f'M3_min={round(m3,2)}'] + this_record


#--------------------------------------------------


out = []
if P_max_record: out.append(P_max_record)
if P_min_record: out.append(P_min_record)
if V2_maxabs_record: out.append(V2_maxabs_record)
if V3_maxabs_record: out.append(V3_maxabs_record)
if T_maxabs_record: out.append(T_maxabs_record)
if M2_maxabs_record: out.append(M2_maxabs_record)
if M3_max_record: out.append(M3_max_record)
if M3_min_record: out.append(M3_min_record)



col_name = ['Case' ,"Frame", "LC", "StepType", "ElmSta", "P", "V2", "V3", "T", "M2", "M3"]
print('\n\n')
try:
    print(f'Beam group {group_name}')
except:
    pass
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