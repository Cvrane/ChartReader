# ChartReader
Image Processing and Data Mining for scientific figures from research papers. 

## Image set
Bar plots (after cropping and pre-processing) used are here: https://drive.google.com/drive/u/1/folders/1aBQT_r22TNLmb4h3azOqS2VtMRxmhDUZ

## Axes Detection
1. Firstly, the image is converted into bw image (black and white), then the max-continuous ones along each row and each column are obtained.
2. Next, for all columns, the maximum value of the max-continuous 1s is picked.
3. A certain threshold (=10) is assumed, and the first column where the max-continuous 1s falls in the region [max - threshold, max + threshold] is the y-axis.
4. Similar approach is followed for the x-axis, but the last row is picked where the max-continuous 1s fall in the region [max - threshold, max + threshold]

140/162 images got their x and y-axis accurate with the above described approach.

<h3 align="center">
  <img src="images/AxesDetectionExample1.png" width="800">
</h3>
<h3 align="center">
  <img src="images/AxesDetectionExample2.png" width="800">
</h3>

## Text detection
Pytesseract python module is used to detect text from the images.
Tesseract is now run on this image to get the bounding boxes for the text. 
An option of `bw` is provided. When this is `True`, then since the text would be in black, the image is converted to HSV and only the black color is filtered. But this leads to inaccurate text. Hence whiten the original image except these bounding boxes and run tesseract again to get the text. The difference between bounding boxes on actual image and the HSV image is shown below.

Bounding boxes for normal image.

<h3 align="center">
  <img src="images/TextDetectionExample1-1.png" width="800">
</h3>

Bounding boxes when `bw` is set to `True`.

<h3 align="center">
  <img src="images/TextDetectionExample1-2.png" width="800">
</h3>

## Label Detection
### X-labels:
1. Filter the text boxes which are below the x-axis(, and to the right of y-axis).
2. Run a sweeping line from x-axis to the bottom of the image, and check when the sweeping line intersects with the maximum number of text boxes.
3. This maximum intersection gives all the bounding boxes for all the x-labels.
    
![](images/LabelDetectionExample.gif)

### Y-labels:
1. Run a sweeping line in the reverse direction, i.e., y-axis and start moving towards the left. Stop when the line has all white pixels (This makes sure you have crossed the ticks)
2. Process the image with the following steps:
   a. Convert to binary image (black and white), using OTSU threshold
   b. Use a rectangle kernel of (1, 15) and apply morphological operations
   c. Use a rectangle kernel of (5, 1) and apply morphological operations
   d. Run a contour detection using opencv and get the bounding rectangles
3. Run a sweeping line from y-axis and start moving towards the left, and check when the sweeping line intersects with the maximum number of text boxes.
4. Whiten the image and keep only these text boxes where there was maximum intersection.
5. Run tesseract to detect only numeric values.

### Y-axis text:
1. Pick the whitened image above, and whiten the bounding boxes for the numeric y-labels detected above.
2. Rotate the image by 90 degree, since the text on y-axis would be vertical.
3. Run tesseract to get the text

<h3 align="center">
  <img src="images/LabelDetectionExample1.png" width="800">
</h3>

## Label detection/finalization
For each bounding rectangle obtained, it is checked whether there is a text box to the immediate right of the rectangle.

### Legend text: 
The immediate rectangle to the right gives the corresponding legend.

## Cluster count estimation
1. This is done by determining the number of items in the legend.
2. Check only the text boxes right to the y-axis and top of x-axis
3. Filter further by considering text boxes which have non-numeric text
4. Run the sweeping line algorithm twice now - Once in the x-direction and the second time in the y-direction (because the legends can be stacked in the x-direction or y-direction)
5. The maximum intersection gives all the legend texts and the number of legends.
6. Now, these rectangles (or bounding boxes) are merged. The final number of rectangles gives the number of legends and the image colors are clustered into these many groups.

## Color detection
1. All the pixel values of the image are divided into clusters. The number of clusters are determined by the above described procedure. Also, prior to clustering, all the white pixels are removed.
2. We then simplify the given plot into multiple plots (one per each cluster). These plots would be a simple bar plot. i.e.., by clustering we convert a stacked bar chart into multiple simpler bar plots.
3. We then get the contours for the plot, and subsequently bounding rectangles for the contours determined.
The noise is removed by determining if the number of bounding rectangles are either 0 or abnormally high.

## Data extraction
### Value-tick ratio calculation: 
This ratio is used to calculate the y-values from each bar-plot using the pixel projection method.
Y-axis Ticks are detected by left-bounding boxes to the y-axis.

Once the pixel values for the ticks are stored, the mean distance between the ticks is calculated.
Further, the mean value of the actual y-label ticks is calculated.
Finally, the value-tick ratio is calculated by
 ``:= normalize_ratio =ticks_diff.mean() / y-ticks.mean()``.
The height of each bounding box is recorded by the help of the merging rectangles during Cluster count estimation method. 
  
This ratio is then used to calculate the y_values.
``:=  v_value = normalize_ratio x    height of bounding box``.

## Reporting results
The results (axes, legends, labels, values, captions and file-names) are written to the Excel sheet.
