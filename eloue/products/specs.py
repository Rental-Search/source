# -*- coding: utf-8 -*-
import math
from imagekit import processors
from imagekit.lib import Image, ImageColor
from imagekit.specs import ImageSpec


class CenteredResize(processors.Resize):
    @classmethod
    def process(cls, img, fmt, obj):
        current_width, current_height = img.size
        ratio_width, ratio_height = (current_width/cls.width, current_height/cls.height)
        
        if ratio_width <= ratio_height:
            resize_ratio = ratio_width
        else:
            resize_ratio = ratio_height
        
        if resize_ratio == 0:
            resize_ratio = 1
        
        new_dimensions = (int(math.ceil(current_width/resize_ratio)), int(math.ceil(current_height/resize_ratio)))
        img = img.resize(new_dimensions, Image.ANTIALIAS)
        
        resized_width, resized_height = img.size
        center_width, center_height = (resized_width/2, resized_height/2)
        
        top_x = int(center_width - int(cls.width/2))
        top_y = int(center_height - int(cls.height/2))
        
        new_img = Image.new('RGB', (cls.width, cls.height), ImageColor.getcolor('white', 'RGB'))
        new_img.paste(img, (-top_x, -top_y))
        
        return new_img, fmt
    

class ResizeThumb(CenteredResize):
    width = 90
    height = 90
    crop = True

class ResizeDisplay(processors.Resize):
    width = 450

class Rotate(processors.Transpose):
    method = 'auto'

class Enhance(processors.Adjustment):
    contrast = 1.2
    sharpness = 1.1

class Thumbnail(ImageSpec):
    pre_cache = False
    access_as = 'thumbnail'
    processors = [Rotate, ResizeThumb, Enhance]

class Display(ImageSpec):
    pre_cache = False
    access_as = 'display'
    processors = [Rotate, ResizeDisplay, Enhance]
