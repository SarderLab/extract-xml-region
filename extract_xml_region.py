import numpy as np
import os
import cv2
import openslide
import lxml.etree as ET
import matplotlib.pyplot as plt
from glob import glob
from skimage.io import imsave, imread
from skimage.transform import resize
from PIL import Image
from xml_to_mask import xml_to_mask
from PIL import Image

cwd = os.getcwd()
save_dir = cwd + '/extracted/'
size_thresh = None # not saved is uder this px area
final_image_size = 1200 # final_image_size
white_background = True # mask the structure
extract_one_region = True # include only one structure per patch (ignore other structures in ROI)

WSIs_ = glob(cwd + '/*.svs')
WSIs = []
XMLs = []

for WSI in WSIs_:
    xml_ = glob(WSI.split('.')[0] + '.xml')
    if xml_ != []:
        print('including: ' + WSI)
        XMLs.append(xml_[0])
        WSIs.append(WSI)

def main():
    # go though all WSI
    for idx, XML in enumerate(XMLs):
        bounds, masks = get_annotation_bounds(XML,1)
        basename = os.path.basename(XML)
        basename = os.path.splitext(basename)[0]

        print('opening: ' + WSIs[idx])
        pas_img = openslide.OpenSlide(WSIs[idx])

        for idxx, bound in enumerate(bounds):
            if extract_one_region:
                mask = masks[idxx]
            else:
                mask=(xml_to_mask(XML,(bound[0],bound[1]), (final_image_size,final_image_size), downsample_factor=1, verbose=0))

            if size_thresh == None:
                PAS = pas_img.read_region((int(bound[0]),int(bound[1])), 0, (final_image_size,final_image_size))
                PAS = np.array(PAS)[:,:,0:3]

            else:
                size=np.sum(mask)
                if size >= size_thresh:
                    PAS = pas_img.read_region((bound[0],bound[1]), 0, (final_image_size,final_image_size))
                    PAS = np.array(PAS)[:,:,0:3]

            if white_background:
                for channel in range(3):
                    PAS_ = PAS[:,:,channel]
                    PAS_[mask == 0] = 255
                    PAS[:,:,channel] = PAS_

            subdir = '{}/{}/'.format(save_dir,basename)
            make_folder(subdir)
            imsave(subdir + basename + '_' + str(idxx) + '.jpg', PAS)


def get_annotation_bounds(xml_path, annotationID=1):
    # parse xml and get root
    tree = ET.parse(xml_path)
    root = tree.getroot()

    Regions = root.findall("./Annotation[@Id='" + str(annotationID) + "']/Regions/Region")

    bounds = []
    masks = []
    for Region in Regions:
        Vertices = Region.findall("./Vertices/Vertex")
        x = []
        y = []

        for Vertex in Vertices:
            x.append(int(np.float32(Vertex.attrib['X'])))
            y.append(int(np.float32(Vertex.attrib['Y'])))

        x_center = min(x) + ((max(x)-min(x))/2)
        y_center = min(y) + ((max(y)-min(y))/2)

        bound_x = x_center-final_image_size/2
        bound_y = y_center-final_image_size/2
        bounds.append([bound_x, bound_y])

        points = np.stack([np.asarray(x), np.asarray(y)], axis=1)
        points[:,1] = np.int32(np.round(points[:,1] - bound_y ))
        points[:,0] = np.int32(np.round(points[:,0] - bound_x ))
        mask = np.zeros([final_image_size, final_image_size], dtype=np.int8)
        cv2.fillPoly(mask, [points], 1)
        masks.append(mask)

    return bounds, masks

def make_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory) # make directory if it does not exit already # make new directory


if __name__ == '__main__':
    main()
