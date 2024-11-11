# Sample Labelizer
This project consist in the developpement of a small software to help with the visualization and manual modification of samples with the [vegroof-project](https://github.com/swiss-territorial-data-lab/proj_vegroofs_DL).

It can achieve two different tasks:
- the labelization of a dataset. This mode consist in labelizing from scratch a set of polygons.
- the correction of a dataset. This mode allows to change the value of the predicted class for each sample.

## Tutorial
Here is a small step-by-step to labelize or correct your first dataset:

1) When launching the software, the following window will appear.
![](src/images_tuto/labelizer_tuto_panel_0.png)

2) The first step is going to be to load rasters and polygons from the tab `load`. When loading the polygons, the following form will appear. There, you are asked to choose the mode between the two following options:
  - Labelizer: this mode is planned for processing binary predictions (or non-categorized files) and choosing a category for each sample. When selecting this mode, you will be asked to choose a `class name` that correspond to the binary categorization. Once this class name is chosen, you will be ask to map the corresponding values for `bare` and `vegetated` in the "Values mapping" section before being able to click on `OK`.
  - Correcter: this mode is to correct the prediction of a multi-class classification model. You will be asked to choose a `class name` but the last part will stay disabled and you will be able to directly click on the `OK button`

![](src/images_tuto/img_1.png)

3) Once the poylgon file and the raster location are given, you will now be able to start working on the dataset:
![](src/images_tuto/labelizer_tuto_panel_1.png)

4) In order 
![](src/images_tuto/labelizer_tuto_panel_2.png)
![](src/images_tuto/img_4.png)



