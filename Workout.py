import cv2
import time
import numpy as np
# import imageio

# MPI
protoFile = "mpi/pose_deploy_linevec_faster_4_stages.prototxt"
weightsFile = "mpi/pose_iter_160000.caffemodel"

# Points
nPoints = 8
POSE_PAIRS = [[0,1], [1,2], [2,3], [3,4], [1,5], [5,6], [6,7] ]

# Set
inWidth = 368
inHeight = 368
threshold = 0.1

# Flags
fix_right_arm = False
fix_left_arm = False
keep_head_still = False
arms_arent_even = False
count_reps = 0
errors_right_arm = 0
errors_left_arm = 0
errors_even = 0
count_top = False
count_bottom = True
done = False

# List of cordinates
x_cor = [-1] * 8
y_cor = [-1] * 8

# Menu
key = input("Please enter d for demo and l for live feed: ") 
print (key)
if key == 'd':
	vid = input("editOfGood.mp4(1) or 1rep.mp4(2) or mix.mp4(3): ")
	if vid == 1:
		input_source = "editOfGood.mp4"
	elif vid == 2:
		input_source = "1rep.mp4"
	else:
		input_source = "mix.mp4"
	cap = cv2.VideoCapture(input_source)
	# clip = VideoFileClip(input_source)
else:
	cap = cv2.VideoCapture(0)

# Frame
hasFrame, frame = cap.read()
vid_writer = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame.shape[1],frame.shape[0]))
# out = cv2.VideoWriter('out.avi',fourcc, 20.0, (640,480))
frame_counter = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))



net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

# Main loop
while cv2.waitKey(1) < 0 and done == False:
	# Output to consul
	print(frame_counter)

	t = time.time()
	hasFrame, frame = cap.read()
	frameCopy = np.copy(frame)
	if not hasFrame:
		cv2.waitKey()
		break

	frameWidth = frame.shape[1]
	frameHeight = frame.shape[0]

	inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)
	net.setInput(inpBlob)
	output = net.forward()

	H = output.shape[2]
	W = output.shape[3]
	# Empty list to store the detected keypoints
	points = []

	for i in range(nPoints):
		# confidence map of corresponding body's part.
		probMap = output[0, i, :, :]

		# Find global maxima of the probMap.
		minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
		
		# Scale the point to fit on the original image
		x = (frameWidth * point[0]) / W
		y = (frameHeight * point[1]) / H

		if prob > threshold : 
			# Change back to framecopy to get rid of nums
			cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
			cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

			# Add the point to the list if the probability is greater than the threshold
			points.append((int(x), int(y)))

			# # Check Form
			# if i == :
			# 	print (int(x), int(y), i)

			# Update List
			x_cor[i] = int(x)
			y_cor[i] = int(y)

			# print (y_cor[i], i)
	

		else :
			points.append(None)


	# Draw Skeleton
	for pair in POSE_PAIRS:
		partA = pair[0]
		partB = pair[1]

		if points[partA] and points[partB]:
			cv2.line(frame, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
			cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
			cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

	# Check for form
	# Check that hands are even: about 35 pixel diff
	if abs(y_cor[7]-y_cor[4]) > 20:
		arms_arent_even = True
	if abs(x_cor[4] - x_cor[3]) > 35:
		fix_right_arm = True
		# print (abs(x_cor[4] - x_cor[3]))
	if abs(x_cor[7]-x_cor[6] ) > 35:
		fix_left_arm = True
	if abs(y_cor[7]-y_cor[4] > 35):
		keep_head_still = True

	# at top
	if y_cor[7]-y_cor[0] <= -40 and count_bottom == True:
		count_reps += 1
		count_bottom = False
		count_top = True
	if y_cor[7]-y_cor[0] >= 40 and count_top == True:
		count_bottom = True
		count_top = False

	

	# Output to user
	# Check if it is a post workout or live
	cv2.putText(frame, "Real time Suggestions: ", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 50, 0), 1, cv2.LINE_AA)
	if arms_arent_even == True:
		cv2.putText(frame, "Make sure hands and arms are even(dif): "+str(abs(y_cor[7]-y_cor[4])), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 50, 0), 1, cv2.LINE_AA)
		errors_even +=1
	cv2.putText(frame, "Arms aren't even: "+str(errors_even), (50, 40), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 0), 1, cv2.LINE_AA)		
	if fix_right_arm == True:
		cv2.putText(frame, "Right forearm is not straight(dif): "+str(abs(x_cor[4] - x_cor[3])), (50, 220), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 50, 0), 1, cv2.LINE_AA)
		errors_right_arm +=1
	cv2.putText(frame, "Fix right forearm: "+str(errors_right_arm), (50, 60), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 0), 1, cv2.LINE_AA) 
	if fix_left_arm == True:
		cv2.putText(frame, "Left forearm is not straight(dif): "+str(abs(x_cor[7]-x_cor[6])), (50, 240), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 50, 0), 1, cv2.LINE_AA)
		errors_left_arm +=1
	cv2.putText(frame, "Fix left forearm: "+str(errors_left_arm), (50, 80), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 0), 1, cv2.LINE_AA)
		
	cv2.putText(frame, "Total errors: "+str(errors_left_arm+errors_even+errors_right_arm), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, .3, (0, 0, 0), 1, cv2.LINE_AA)
	cv2.putText(frame, "Reps: "+str(count_reps), (50, 140), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1, cv2.LINE_AA)
	cv2.imshow('Output-Skeleton', frame)
	
	# Reset
	x_cor = [-1] * 8
	y_cor = [-1] * 8
	arms_arent_even = False
	fix_left_arm = False
	fix_right_arm = False
	# keep_head_still = False

	# Decrease frame counter
	frame_counter -= 1
	if frame_counter == 1:
		done = True
	
	vid_writer.write(frame)
	# vid_writer.release()

	

# Output errors individually at end

cap.release()
vid_writer.release()
cv2.destroyAllWindows()

print ("done")