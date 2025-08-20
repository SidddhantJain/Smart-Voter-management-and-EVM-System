// Camera Driver (C++)
// Handles camera initialization and image capture for VoteGuard Pro EVM
#include <opencv2/opencv.hpp>
#include <iostream>

class Camera {
public:
    bool initialize() {
        std::cout << "[HW] Initializing camera..." << std::endl;
        // Open the default camera
        cap.open(0);
        if (!cap.isOpened()) {
            std::cerr << "[HW] Error: Unable to access the camera." << std::endl;
            return false;
        }
        std::cout << "[HW] Camera initialized successfully." << std::endl;
        return true;
    }

    bool captureImage() {
        std::cout << "[HW] Capturing image..." << std::endl;
        if (!cap.isOpened()) {
            std::cerr << "[HW] Error: Camera is not initialized." << std::endl;
            return false;
        }
        cv::Mat frame;
        cap >> frame; // Capture a frame
        if (frame.empty()) {
            std::cerr << "[HW] Error: Captured frame is empty." << std::endl;
            return false;
        }
        cv::imwrite("captured_image.jpg", frame); // Save the captured image
        std::cout << "[HW] Image captured and saved as 'captured_image.jpg'." << std::endl;
        return true;
    }

private:
    cv::VideoCapture cap;
};
