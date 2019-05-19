from imutils import paths
import face_recognition
import os
from imutils.video import VideoStream
import imutils
import pickle
import time
import cv2

## Acknowledgement
## This code is adapted from:
## https://www.hackster.io/mjrobot/real-time-face-recognition-an-end-to-end-project-a10826


class FacialRecognition:

    def __init__(self, encodings, classifier, dataset, detection_method, resolution, output, display):
        self.encodings = encodings
        self.classifier = classifier
        self.dataset = dataset
        self.detection_method = detection_method
        self.resolution = resolution
        self.output = output
        self.display = display

    def capture(self, username):
        folder = '{}/{}'.format(self.dataset, username)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Start the camera
        cam = cv2.VideoCapture(0)
        # Set video width
        cam.set(3, 640)
        # Set video height
        cam.set(4, 480)
        # Get the pre-built classifier that had been trained on 3 million faces
        face_detector = cv2.CascadeClassifier(self.classifier)

        img_counter = 0
        while img_counter <= 10:
            key = input("Press q to quit or ENTER to continue: ")
            if key == 'q':
                break

            ret, frame = cam.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                print("No face detected, please try again")
                continue

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                img_name = "{}/{:04}.jpg".format(folder, img_counter)
                cv2.imwrite(img_name, frame[y:y + h, x:x + w])
                print("{} written!".format(img_name))
                img_counter += 1

        cam.release()
        cv2.destroyAllWindows()

    def encode(self):
        # grab the paths to the input images in our dataset
        print("[INFO] quantifying faces...")
        image_paths = list(paths.list_images(self.dataset))

        # initialize the list of known encodings and known names
        known_encodings = []
        known_names = []

        # loop over the image paths
        for (i, image_path) in enumerate(image_paths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                                                         len(image_paths)))
            name = image_path.split(os.path.sep)[-2]

            # load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                                                    model=self.detection_method)

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                known_encodings.append(encoding)
                known_names.append(name)

        # dump the facial encodings + names to disk
        print("[INFO] serializing encodings...")
        data = {"encodings": known_encodings, "names": known_names}
        f = open("encodings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()

    def recognise(self):
        # load the known faces and embeddings
        print("[INFO] loading encodings...")
        data = pickle.loads(open(self.encodings, "rb").read())

        # initialize the video stream and pointer to output video file, then
        # allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        writer = None
        time.sleep(2.0)

        # loop over frames from the video file stream
        while True:
            # grab the frame from the threaded video stream
            frame = vs.read()

            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width=self.resolution)
            r = frame.shape[1] / float(rgb.shape[1])

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb,
                                                    model=self.detection_method)
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                                                         encoding)
                name = "Unknown"

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matched_idxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matched_idxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

                # update the list of names
                names.append(name)

            # loop over the recognized faces
            for ((_, _, _, _), name) in zip(boxes, names):
                return name

            # if the video writer is None *AND* we are supposed to write
            # the output video to disk initialize the writer
            if writer is None and self.output is not None:
                four_cc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(self.output, four_cc, 20, (frame.shape[1], frame.shape[0]), True)

            # if the writer is not None, write the frame with recognized
            # faces to disk
            if writer is not None:
                writer.write(frame)

            # check to see if we are supposed to display the output frame to
            # the screen
            if self.display > 0:
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    cv2.destroyAllWindows()
                    vs.stop()
                    if writer is not None:
                        writer.release()
                    return ""

