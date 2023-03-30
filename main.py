import cv2
import numpy as np


def get_max_contour(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    black = np.zeros((image.shape[0], image.shape[1]), np.uint8)

    if len(contours) == 0:
        return black, []
    c = max(contours, key=cv2.contourArea)
    mask = cv2.drawContours(black, [c], 0, 255, -1)
    return mask, [c]


def draw_contour_rect(image, cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    cv2.drawContours(image, [box], 0, (0, 255, 0), 2)


frame_width, frame_height = 960, 540
cap = cv2.VideoCapture('box_on_track.mp4')
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width, 2*frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if ret is False:
        break

    # Threshold image in HSV color-space
    frame = cv2.resize(frame, (frame_width, frame_height))
    img_blur = cv2.GaussianBlur(frame, (11, 11), 0)
    img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)
    img_th = cv2.threshold(img_hsv[:, :, 1], 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Find Contours
    box_mask, box_contour = get_max_contour(img_th)
    masked_img = cv2.bitwise_and(frame, frame, mask=box_mask)

    if len(box_contour) != 0:
        draw_contour_rect(frame, box_contour[0])

    cv2.imshow("Detections", frame)
    cv2.imshow("Blur frame", img_blur)
    cv2.imshow("Masked frame", masked_img)
    cv2.imshow("Threshold", img_th)

    # Video Saving
    cv2.putText(frame, 'Detection', (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(masked_img, 'Segmentation', (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    img_cat = np.concatenate((frame, masked_img), axis=0)
    cv2.imshow("Cat", img_cat)
    out.write(img_cat)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
