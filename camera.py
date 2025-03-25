import cv2

# Initialize the webcam
cap = cv2.VideoCapture(0)  # 0 represents the default camera (usually the built-in webcam)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Display the frame in a window
    cv2.imshow('Webcam Capture', frame)

    # Wait for a key press (1 in this case)
    key = cv2.waitKey(1) & 0xFF

    # Check if the key pressed is '1'
    if key == ord('1'):
        # Save the captured frame as an image
        cv2.imwrite('captured_image.jpg', frame)
        print("Image captured!")

    # If the 'q' key is pressed, exit the loop
    elif key == ord('q'):
        break

# Release the webcam and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
