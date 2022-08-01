import json
import os

yolo_co = {
	1:[0.16536458333333334, 0.5138888888888888, 0.2578125, 0.7888888888888889],
	2:[0.16536458333333334, 0.5143518518518518, 0.2557291666666667, 0.7898148148148149],
	3:[0.16536458333333334, 0.5152777777777777, 0.25364583333333335, 0.7916666666666666],
}

# y = json.dumps(yolo_co)
# print(y)

# cwd = os.getcwd()
# print(cwd)
# cwd = cwd.replace("\\","/")
# with open(cwd, "w+") as f:
#     json.dump(yolo_co, f)
# print(cwd)

# Serializing json
json_object = json.dumps(yolo_co, indent=4)
 
# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)