# ChartReader
Fully automated end-to-end framework to extract data from bar plots and other figures in scientific research papers using modules such as OpenCV, AWS-Rekognition for text detection in images.

## Image set
Bar plots used are here: https://drive.google.com/drive/u/1/folders/154sgx3M49NoKOoOjoppsSuvqd2WzqZqX

## Chart classification (Accuracy: 84.08%)
### Data preparation
<b> Step 1: </b> ``google_images_download`` python module is used to download google images for each type of chart: Area chart, Line chart, bar plot, pie chart, venn diagram etc. based on their corresponding keywords.

```
$ git clone https://github.com/Joeclinton1/google-images-download.git
$ cd google-images-download && python setup.py install
```

<b> Step 2: </b> The downloaded images are carefully reviewed and the incorrect images are removed.

The following are the training data used, and model files.
<br>training corpus: https://drive.google.com/drive/u/1/folders/1M8kwdQE7bpjpdT08ldBURFdzLaQR9n5h
<br>model: https://drive.google.com/drive/u/1/folders/1GVW_MtFFYT-Tj44p0_QLKM7hVnn_AcKI

Below is the count of images for each type:
<table>
<tr>
<td>

| Plot type     | Count         |
| ------------- |:-------------:|
| BarGraph      |   528         |
| VennDiagram   |   364         |
| PieChart      |   355         |
| ScatterGraph  |   335         |

</td>
<td>

| Plot type     | Count         |
| ------------- |:-------------:|
| TreeDiagram   |   297         |
| FlowChart     |   293         |
| Map           |   276         |
| ParetoChart   |   329         |

</td>
<td>

| Plot type     | Count         |
| ------------- |:-------------:|
| BubbleChart   |   311         |
| LineGraph     |   300         |
| AreaGraph     |   299         |
| NetworkDiagram|   321         |
| BoxPlot       |   312         |

</td>
</tr>
</table>

### Training phase:
pretrained model VGG19 is used to train the images, and is run on the test images to classify the images to 13 different types such as Bar chart, Line graph, Pie chart etc.

The accuracy is calculated using stratified five-fold cross validation. The accuracy of the model is ``84.08%``. The following are the training accuracy and loss curves captured during the training phase for each fold of cross validation.

<h3 align="center">
  <img src="images/accuracy-curve1.png" width="800">
</h3>

<h3 align="center">
  <img src="images/accuracy-curve2.png" width="800">
</h3>

<h3 align="center">
  <img src="images/accuracy-curve3.png" width="800">
</h3>

<h3 align="center">
  <img src="images/accuracy-curve4.png" width="800">
</h3>

<h3 align="center">
  <img src="images/accuracy-curve5.png" width="800">
</h3>

### Results (predictions on test data)
The following are 100 randonly picked images which are predicted as bar plots. Highlighted images (6 in number out of 100 randomly picked) are incorrectly classified as bar plots.

<h3 align="center">
  <img src="images/BarplotPrediction.png" width="1000">
</h3>

## Axes Detection (Accuracy: 80.22%) [1006/1254 correct]
1. Firstly, the image is converted into black and white image, then the max-continuous ones along each row and each column are obtained.
2. Next, for all columns, the maximum value of the max-continuous 1s is picked.
3. A certain threshold (=10) is assumed, and the first column where the max-continuous 1s falls in the region [max - threshold, max + threshold] is the y-axis.
4. Similar approach is followed for the x-axis, but the last row is picked where the max-continuous 1s fall in the region [max - threshold, max + threshold]

<h3 align="center">
  <img src="images/AxesDetectionExample1.png" width="800">
</h3>
<h3 align="center">
  <img src="images/AxesDetectionExample2.png" width="800">
</h3>

### Results
Both x and y axes are detected correctly for 1006 images out of 1254 images (test data set). Below are some of the failed cases in axes detection.

<h3 align="center">
  <img src="images/AxesDetectionResult.png" width="800">
</h3>

## Text detection
AWS-Rekognition is used to detect text in the image. [DetectText](https://docs.aws.amazon.com/rekognition/latest/dg/API_DetectText.html) API is used for detecting text. Only the text with confidence >= 80 are considered.

### Double-pass algorithm for text detection
To improve text detection algorithm, double-pass algorithm is employed.
1. Text detection using detect_text AWS Rekognition API, and considered only the text boxes for which confidence >= 80
2. Fill the polygons corresponding to these text with white color
3. Run text detection (2nd pass) on the new image, and consider only the ones with confidence >= 80

### Bounding Box calculation
There is an [issue](https://forums.aws.amazon.com/thread.jspa?threadID=325482&tstart=0) with bounding box for vertical text or text with an angle. Therefore, bounding box is calculated from the polygon coordinates (or vertices) from the AWS Rekognition output. 

## Label Detection
### X-labels:
1. Filter the text boxes which are below the x-axis(, and to the right of y-axis).
2. Run a sweeping line from x-axis to the bottom of the image, and check when the sweeping line intersects with the maximum number of text boxes.
3. This maximum intersection gives all the bounding boxes for all the x-labels.
    
![](images/LabelDetectionExample.gif)

### X-text
1. Filter the text boxes which are below the x-labels
2. Run a sweeping line from x-axis to the bottom of the image, and check when the sweeping line intersects with the maximum number of text boxes.
3. This maximum intersection gives all the bounding boxes for all the x-text.

### Y-labels:
1. Filter the text boxes which are to the left of y-axis.
2. Run a sweeping line from y-axis and start moving towards the left, and check when the sweeping line intersects with the maximum number of text boxes.
3. Keep only these text boxes where there was maximum intersection, and use python regex to detect only numeric values.

### Y-text:
1. Filter the text boxes which are to the left of y-axis.
2. Pick the remaining text which are not classified as y-labels as y-text

<h3 align="center">
  <img src="images/LabelDetectionExample1.png" width="800">
</h3>

### Legend detection
1. Filter the text boxes that are above the x-axis, and to the right of y-axis.
2. Clean the text to remove 'I'. These are obtained since error bars in the charts are detected as 'I' by AWS Rekognition OCR API(s).
3. Use an appropriate regex to disregard the numerical values. These are mostly the ones which are there on top of the bars to denote the bar value.
4. Now merge the remaining text boxes (with x-value threshold of 10) to make sure all the multi-word legends are part of a single bounding box.
5. Since legends can be grouped horizontally or vertically, we need to run two sweeping lines to detect legends. 
6. Run a sweeping line from y-axis and start moving towards the right, and check when the sweeping line intersects with the maximum number of text boxes.
7. Continue Step 6 with a sweeping line from x-axis and moving to top of the image and check when the sweeping line intersects with maximum number of text boxes.
8. This maximum intersection gives the bounding boxes for all the legends.

## Label (and legend) detection/finalization
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
This ratio is used to calculate the y-values from each bar-plot using the pixel projection method. Y-axis ticks are detected by left-bounding boxes to the y-axis.

Since the text detection (numeric values) isn't perfect, once the pixel values for the ticks and actual y-label texts are obtained, the outliers are removed by assuming a normal distribution and whether the values deviate very much. Then, the mean distance between the ticks is calculated. Further, the mean value of the actual y-label ticks is calculated. Finally, the value-tick ratio is calculated by :

<h3 align="center">
  <img src="images/equation2.gif">
</h3>

The height of each bounding box is recorded by the help of the merging rectangles during Cluster count estimation method. This ratio is used to further calculate the y-values :

<h3 align="center">
  <img src="images/equation1.gif">
</h3>

Below shows data extraction results on an image.

<h3 align="center">
  <img src="images/DataExtractionExample.png">
</h3>

Note that the highlighted numbers (in red) are related to the legend related bounding boxes and WIP to be further processed and removed.

## Reporting results
The results (axes, legends, labels, values, captions and file-names) are written to the Excel sheet.
