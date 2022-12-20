# this script generates the base program for the Powered Up City & Technic Hubs from the MINDSTORMS base program

with open("mindstorms_51515.py", "r+") as f:
    lines = f.readlines()

# delete the LightMatrix part
foundLightMatrixStart = False
foundLightMatrixEnd = False
filteredLines = []
for line in lines:

    if "class LightMatrix():" in line:
        foundLightMatrixStart = True
    if "class SwitchController():" in line:
        foundLightMatrixEnd = True

    if not (foundLightMatrixStart ^ foundLightMatrixEnd):
        if "display" not in line:
            filteredLines.append(line)

filteredLines = [l.replace("system.buttons", "system.button") for l in filteredLines]
for hub in ["CityHub", "TechnicHub"]:
    with open("%s.py" % hub, "w+") as f:
        hubFilteredLines = [l.replace("PrimeHub", hub) for l in filteredLines]
        f.writelines(hubFilteredLines)