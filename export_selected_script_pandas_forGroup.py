import comtypes.client
import pandas as pd

# Connect to ETABS API
ETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
SapModel = ETABSObject.SapModel

# Define the group name
group_name = "MyGroup"

# Get all frame elements in the group
_, group_frames = SapModel.GroupDef.GetGroupAssignments(group_name)

# Extract forces for selected frames
data = []
for frame in group_frames:
    _, _, _, P, V2, V3, T, M2, M3 = SapModel.Results.FrameForce(frame, 0)
    data.append([frame, P, V2, V3, T, M2, M3])

# Create Pandas DataFrame
columns = ["Frame", "Axial Force (P)", "Shear Force V2", "Shear Force V3", "Torsion (T)", "Moment M2", "Moment M3"]
df = pd.DataFrame(data, columns=columns)

# Save to CSV
csv_filename = "ETABS_Group_Results.csv"
df.to_csv(csv_filename, index=False)

print(f"Results for group '{group_name}' saved to {csv_filename}")

# Disconnect from ETABS
ETABSObject.ApplicationExit(False)

