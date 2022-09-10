# Blender Labelling Tool

## What's it?

It's a anotation tool made on top of Blender (3+).

## What can it do?

For now it's possible to annotate bounding boxes on videos and export them in YOLO format.

## How to use

1. Import a video

2. Create a class collection

3. Select this collection in the outliner

4. Add a bounding box

5. Animate the bounding box

6. Export

## Future plans

1. Short-term goals

    - COCO and Pascal VOC support

    - Bounding box data import (Yolo, Coco, Pascal voc)

    - 2d joints, skeleton data

2. Long-term goals

   - Segmentation labelling

   - Rotated bounding boxes

   - 3d data labelling (point clouds, etc)

## Motivation

I always wanted a simple annotation tool that one can just open and start annotating. Should be simple, easy to use, cross-platform and lightweight. Here are the requirements:

   1. Easy to install and cross-platform

   2. Decent playback speed and overall performance

   3. Extendability

   4. Free and open source

From Blender, we get many cool things for free in video annotation. Support of multiple video formats, video proxies, different types of interpolation, keyframing and curve system, collection system, etc. So it's just a matter of the creation of simple functions to populate our scene with labelling data - bounding boxes, skeleton joints, etc. It is also possible to add 3d data labelling (which is a task for the future though).