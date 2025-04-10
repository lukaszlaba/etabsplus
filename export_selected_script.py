import comtypes.client
import csv

# Connect to ETABS API
ETABSObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
SapModel = ETABSObject.SapModel

# Get selected frame elements
_, selected_objects, _ = SapModel.SelectObj.GetSelected()
selected_frames = [obj for obj in selected_objects if "Frame" in obj]

# Extract forces for selected frames
frame_results = []
for frame in selected_frames:
    _, _, _, P, V2, V3, T, M2, M3 = SapModel.Results.FrameForce(frame, 0)
    frame_results.append([frame, P, V2, V3, T, M2, M3])

# Save results to CSV file
csv_filename = "ETABS_Frame_Forces.csv"
with open(csv_filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Frame", "Axial Force (P)", "Shear Force V2", "Shear Force V3", "Torsion (T)", "Moment M2", "Moment M3"])
    writer.writerows(frame_results)

print(f"Frame force results saved to {csv_filename}")

# Disconnect from ETABS
ETABSObject.ApplicationExit(False)