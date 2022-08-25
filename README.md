# Polygonal-Image-Cropper
A simple cropping program to crop and display a section of an image.

2 cropping functions are included in main.py, a polygonal crop and rectangular cropping. Uncomment the imwrite line to save image.

Once the cropping points are defined, the coordinates will be stored in a pickle file, delete the pickle file if you wish to redefine the ROI

**Polygonal Crop**
- LMB to define points
- RMB to close polygon (do not move mouse once at last point)
- MMB to undo last, you can only undo the most recent last action
- Q button to finish cropping
- ESC button to fully reset points

**Rectangular Crop**
- LMB to define points
- Only 2 points are needed, the top left corner and bottom right corner of the rectangle
- RMB within the drawn rectangle to delete
- Q button to finish cropping
