# AIY-vision-kit-DRONE
In this project, I studied and experimented the capabilities of the AIY vision kit of Google for AI application embedded in drone. 
This small shield provides huge image processing capacity thanks to its Movidius unit. In addition to its small size and weight it is a very viable solution of AI on edge for small UAV both Cloud or Onboard application:

<p align="center">
  <img src="/images/advantages.PNG" width="500">
</p>
<p align="center">
  <img src="/images/usecase.PNG" width="500">
</p>
<p align="center">
  <img src="/images/cloud.PNG" width="500">
</p>

A complet description of my work is available [HERE](https://github.com/BenbenIO/AIY-vision-kit-DRONE/blob/master/AIY_test_presentation.pdf)

I am currently working on 2 usecases:

## 1] Crack detection
Implementing an on-board crack detection-classification system, and integrate the solution into a small U.A.V.
Current state:
- [x] Crack detection classifier
- [ ] U.A.V implementaion
I used [this data](https://data.mendeley.com/datasets/5y9wdsg2zt/1) for training a MobileNet V1 (160X160, 0.5) to classify crack image.
On [this youtube link](https://www.youtube.com/watch?v=e4FoHp6COhM)you can see a video of the implemented solution.

## 2] Cloud facial recognition
Facial recogniton use heavy computional algorithm and currently solve by two solution:
* full on-board system: using powerfull computer like Jetson TX2 (quite big and expensive)
* full cloud: cheaper but may bring latency

My idea is to use AIY kit to divide the task, I achieved face detection on board, and sent the cropped face to the cloud for recognition. 
<p align="center">
  <img src="/images/face_reco.PNG" width="500">
</p>
In this case, we save bandwidtch and minimize the latency but still using a small board such as Raspberry Zero.
Current state:

- [x] Face detection - Cropped face solution -Cloud
- [x] Face recogntion using facenet or OpenCV
- [ ] U.A.V implementaion and face tracking
