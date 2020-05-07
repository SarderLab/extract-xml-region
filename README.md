# extract_xml_region
Code for extracting ROI from annotated structures in whole slide images (WSIs) using Aperio Imagescope

Place 'extract_xml_region.py' in a directory containing the .svs WSI and .xml annotation files before running. 
This code contains options for extraction at the top:
  - save_dir ==> output directory name - created
  - size_thresh ==> size threshold in pixels - excludes small objects
  - final_image_size ==> size of the output ROI patches
  - white_background ==> mask the structure - set the background to white (set to False for whole ROI)
  - extract_one_region ==> include only one annotation per ROI (white_background must be set to True) 
  
Code that can be trained to segment WSIs and produce XML annotations is avalable [here](https://github.com/SarderLab/H-AI-L)

This code was created by [Brendon Lutnick](https://github.com/brendonlutnick)
