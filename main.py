import numpy as np
import cv2
import copy
import pickle
import os

# ---------------------------------------------------------------------------------- #
# -------------------------------- Global variables -------------------------------- #
# ---------------------------------------------------------------------------------- #
# We define this for the cropping functions to work

# Edge coordinates for boxing
globalTop = 0
globalBtm = 0
globalLeft = 0
globalRight = 0

# To keep track of last point when drawing polygon
ix, iy, sx, sy = -1, -1, -1, -1
polygon = []


# ---------------------------------------------------------------------------------- #
# ---------------------------- Drawing Functions ----------------------------------- #
# ---------------------------------------------------------------------------------- #

# Helper function, Returns cropped mask with black background
def cropImg(image, point_array, original):
    height = original.shape[0]
    width = original.shape[1]
    blank_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(blank_mask, point_array, 255)
    result = cv2.bitwise_and(image, image, mask=blank_mask)

    return result

# Draws rectangles for template selection
def draw_rec(event, x, y, flags, param):
    global pointLst, cirList, recList
    # Connect the points determined by LMB
    if event == cv2.EVENT_LBUTTONDOWN:
        pointLst.append((x, y))
        cirList.append((x, y))

        if len(pointLst) == 2:
            rec = copy.deepcopy(pointLst)
            recList.append(rec)
            pointLst = []
            cirList = []

    # Undo last
    elif event == cv2.EVENT_RBUTTONDOWN:
        for token, pos in enumerate(recList):
            (x1, y1), (x2, y2) = pos
            if x1 < x < x2 and y1 < y < y2:
                recList.pop(token)

    with open("rectangles.pickle", "wb") as f2:
        pickle.dump(recList, f2)


# Polygonal Cropping
def draw_lines(event, x, y, flags, param):
    # updates the cache with every mouse action
    global ix, iy, sx, sy, polygon, posList, imgCache, pointsCache, polygonCache, posListCache, img_base2
    # Connect the points determined by LMB
    if event == cv2.EVENT_LBUTTONDOWN:
        pointsCache = [copy.deepcopy(ix), copy.deepcopy(iy)]
        imgCache = copy.deepcopy(img_base2)
        polygonCache = copy.deepcopy(polygon)
        posListCache = copy.deepcopy(posList)

        # draw circle at point
        cv2.circle(img_base2, (x, y), 3, (0, 200, 0), -1)

        if ix != -1:  # if ix and iy are not first points, then draw a line
            cv2.line(img_base2, (ix, iy), (x, y), (0, 200, 0), 2, cv2.LINE_AA)
        else:  # if ix and iy are first points, store as starting points
            sx, sy = x, y
            pointsCache = [-1, -1]  # reset cache

        ix, iy = x, y
        polygon.append([ix, iy])

    # Undo Last
    elif event == cv2.EVENT_MBUTTONDOWN:
        prev_points = copy.deepcopy(pointsCache)
        ix, iy = prev_points[0], prev_points[1]
        img_base2 = copy.deepcopy(imgCache)
        polygon = copy.deepcopy(polygonCache)
        posList = copy.deepcopy(posListCache)

    # complete the polygon (DO NOT MOVE MOUSE AT LAST DRAWN POINT)
    elif event == cv2.EVENT_RBUTTONDOWN:
        imgCache = copy.deepcopy(img_base2)
        pointsCache = [copy.deepcopy(x), copy.deepcopy(y)]
        polygonCache = copy.deepcopy(polygon)
        posListCache = copy.deepcopy(posList)

        # draw line to start
        cv2.line(img_base2, (x, y), (sx, sy), (0, 200, 0), 2, cv2.LINE_AA)
        ix, iy = -1, -1  # reset ix and iy
        posList.append(polygon)
        polygon = []

    with open("polygon.pickle", "wb") as f1:
        pickle.dump(posList, f1)


# ---------------------------------------------------------------------------------- #
# --------------------------------- Driver Code ------------------------------------ #
# ---------------------------------------------------------------------------------- #

img_base_path = "img.jpg"  # Set to relevant path
img_base = cv2.imread(img_base_path)
img_base2 = copy.deepcopy(img_base)  # used to display lines and boxes drawn
img_base_name = os.path.splitext(img_base_path)[0]

try:
    with open("polygon.pickle", "rb") as f:
        posList = pickle.load(f)
        pts1 = np.array([posList[0]])
        display = cropImg(img_base, pts1, img_base)
        # cv2.imwrite("polygonROI.jpg", display)
        cv2.imshow("Cropped Polygon", display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

except FileNotFoundError:
    print("Current defining region of interest ...")
    posList = []

    # Caching so we can undo last (only most recent action) or reset completely
    imgCache = copy.deepcopy(img_base2)
    imgOriginal = copy.deepcopy(img_base)
    pointsCache = [-1, -1]
    polygonCache = []
    posListCache = []

    # Draw the user-defined polygonal region of interest (deck area)
    while True:
        for poly in posList:
            points = np.array(poly, np.int32)
            points = points.reshape((-1, 1, 2))
            img_base2 = cv2.polylines(img_base2, [points], isClosed=True, color=(0, 200, 0), thickness=2)

        # Undo all using ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            img_base2 = copy.deepcopy(imgOriginal)
            posList = []
            ix, iy, sx, sy = -1, -1, -1, -1
            polygon = []

        # set exit key as Q
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            print("You have successfully drawn the bounding area for {image}".format(image=img_base_name))
            break

        cv2.imshow("Image", img_base2)
        cv2.setMouseCallback("Image", draw_lines)

    cv2.destroyAllWindows()

try:
    with open("rectangles.pickle", "rb") as f:
        recList = pickle.load(f)
        pts2 = recList[0]
        x1 = pts2[0][0]
        x2 = pts2[1][0]
        y1 = pts2[0][1]
        y2 = pts2[1][1]
        display2 = img_base[y1:y2, x1:x2]  # note the axis
        # cv2.imwrite("rectangleROI.jpg", display2)
        cv2.imshow("Cropped Rectangle", display2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

except FileNotFoundError:
    print("Currently selecting floor templates ...")
    recList = []
    pointLst = []
    cirList = []

    # Select floor tiles as templates (more is better, but will slow the algorithm down)
    while True:
        img_aux = cv2.imread(img_base_path)  # we have to import every loop to enable deleting
        for circs in cirList:
            # draw circle as reference point
            cv2.circle(img_aux, (circs[0], circs[1]), 3, (30, 200, 15), -1)

        for recs in recList:
            (x_top, y_top), (x_btm, y_btm) = recs
            cv2.rectangle(img_aux, (x_top, y_top), (x_btm, y_btm), (30, 200, 15), 2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("You have successfully defined the floor template for {image}".format(image=img_base_name))
            break

        cv2.imshow("img", img_aux)
        cv2.setMouseCallback("img", draw_rec)
        cv2.waitKey(1)

    cv2.destroyAllWindows()