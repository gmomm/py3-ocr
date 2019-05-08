#!/usr/bin/python3
import cv2
import numpy as np
import imutils
import pytesseract
import re 

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
 
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
 
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
 
    # return the ordered coordinates
    return rect

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

##(1) read into  bgr-space
#image = cv2.imread("./cnh/0000229005335348035291076304670271.tif")
#image = cv2.imread("./cnh/0008900000535576002339302504670271.tif")
#image = cv2.imread("./cnh/0000682008998691668814587104670271.tif")

image = cv2.imread("./cnh/0003048004174180485339480004670271.tif")

img3 = image.copy()
img3 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB )

resized = imutils.resize(image, width=200)
ratio = image.shape[0] / float(resized.shape[0])

gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
median = cv2.medianBlur(gray, 5)

edged = cv2.Canny(median, 2, 10, apertureSize=5)

dilated = cv2.dilate(edged, np.ones((5, 5)))
eroded = cv2.erode(dilated, np.ones((5, 5)))

(cnts, _) = cv2.findContours(eroded.copy(), cv2.RETR_TREE,
    cv2.CHAIN_APPROX_SIMPLE)
sortedc = sorted(cnts, key = cv2.contourArea, reverse = True)
c = sortedc[0]
# compute the rotated bounding box of the largest contour
c = c.astype("float")
c *= ratio
c = c.astype("int")
    
rect = cv2.minAreaRect(c)	
box = np.int0(cv2.boxPoints(rect))

# apply the four point tranform to obtain a "birds eye view" of
# the image
warped = four_point_transform(img3, box)
cv2.imwrite("warped.jpg", warped)

height, width, channels = warped.shape
print("width={} height={}".format(width, height) )

minHeight = np.int0(height * 0.04)
minWidth = 2 * minHeight 

#resized = imutils.resize(warped, width= np.int0(width / 2) )
#ratio = image.shape[0] / float(resized.shape[0])


print("minWidth={} minHeight={}".format(minWidth, minHeight) )

gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

(thresh, img_bin) = cv2.threshold(gray, 127, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU )


#img_bin = cv2.resize(img_bin, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# Invert the image
#img_bin = 255-img_bin 
cv2.imwrite("Image_bin.jpg",img_bin)

contours,hierarchy = cv2.findContours(img_bin,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#CHAIN_APPROX_SIMPLE

idx=0
# Define config parameters.
# '-l eng'  for using the English language
# '--oem 1' for using LSTM OCR Engine
baseconfig = ('-l por --oem 1 --psm 3')

#warped = cv2.resize(warped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

rectangles = warped.copy()
for contour in contours:   
    (x,y,w,h) = cv2.boundingRect(contour)
    if h > minHeight and w > h*2 : 
       print("x={} y={} w={} h={}".format(x, y, w, h))
       cv2.rectangle(warped, (x,y), (x+w,y+h), (0,255,0), 2)
       idx += 1
       eh=0
       eh = np.int0( h * 0.1 )
       new_img = rectangles[y-eh:y+h+eh, x:x+w]
       ret,new_img = cv2.threshold(new_img,127,255,cv2.THRESH_BINARY)
       new_img = cv2.resize(new_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
       
       cv2.imwrite("img-"+str(idx) + '.png', new_img)
       print("img-"+str(idx)+'.png')
       image_text = pytesseract.image_to_string(new_img, config=baseconfig )
       #image_text = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in image_text.split("\n")]
       image_text = re.sub(r"[^a-zA-Z0-9 \/\n]+", '', image_text) 
       image_text = image_text.strip()
       if len(image_text) > 1 :
          with open("img-"+str(idx)+'.txt', 'w+', encoding='utf-8') as f:
               f.write(image_text)
           

cv2.imwrite("result.jpg", warped)

exit()

