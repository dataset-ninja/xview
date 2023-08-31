# http://xviewdataset.org/

import os
import shutil
from collections import defaultdict
from urllib.parse import unquote, urlparse

import geojson
import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import (
    dir_exists,
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "DIUx xView 2018 Detection"
    dataset_path = "/mnt/d/datasetninja/xview"
    geojson_path = "/mnt/d/datasetninja/xview/train_labels/xView_train.geojson"
    images_folder = "train_images"
    batch_size = 3
    ds_name = "ds"
    images_ext = ".tif"

    def create_ann(image_path):
        labels = []

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        bboxes_data = name_to_data[get_file_name_with_ext(image_path)]

        for curr_data in bboxes_data:
            bbox = list(map(int, curr_data[1].split(",")))
            obj_class = idx_to_class.get(int(curr_data[0]))
            if obj_class is None:
                continue

            left = bbox[0]
            right = bbox[2]
            top = bbox[1]
            bottom = bbox[3]
            rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
            label = sly.Label(rectangle, obj_class)
            labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    name_to_data = defaultdict(list)
    with open(geojson_path) as f:
        gj = geojson.load(f)["features"]
        for curr_gj in gj:
            curr_data = curr_gj["properties"]
            name_to_data[curr_data["image_id"]].append(
                (curr_data["type_id"], curr_data["bounds_imcoords"])
            )

    idx_to_class_name = {
        11: "Fixed-wing Aircraft",
        12: "Small Aircraft",
        13: "Cargo Plane",
        15: "Helicopter",
        17: "Passenger Vehicle",
        18: "Small Car",
        19: "Bus",
        20: "Pickup Truck",
        21: "Utility Truck",
        23: "Truck",
        24: "Cargo Truck",
        25: "Truck w/Box",
        26: "Truck Tractor",
        27: "Trailer",
        28: "Truck w/Flatbed",
        29: "Truck w/Liquid",
        32: "Crane Truck",
        33: "Railway Vehicle",
        34: "Passenger Car",
        35: "Cargo Car",
        36: "Flat Car",
        37: "Tank car",
        38: "Locomotive",
        40: "Maritime Vessel",
        41: "Motorboat",
        42: "Sailboat",
        44: "Tugboat",
        45: "Barge",
        47: "Fishing Vessel",
        49: "Ferry",
        50: "Yacht",
        51: "Container Ship",
        52: "Oil Tanker",
        53: "Engineering Vehicle",
        54: "Tower crane",
        55: "Container Crane",
        56: "Reach Stacker",
        57: "Straddle Carrier",
        59: "Mobile Crane",
        60: "Dump Truck",
        61: "Haul Truck",
        62: "Scraper/Tractor",
        63: "Front loader/Bulldozer",
        64: "Excavator",
        65: "Cement Mixer",
        66: "Ground Grader",
        71: "Hut/Tent",
        72: "Shed",
        73: "Building",
        74: "Aircraft Hangar",
        76: "Damaged Building",
        77: "Facility",
        79: "Construction Site",
        83: "Vehicle Lot",
        84: "Helipad",
        86: "Storage Tank",
        89: "Shipping container lot",
        91: "Shipping Container",
        93: "Pylon",
        94: "Tower",
    }

    idx_to_class = {}
    for idx, name in idx_to_class_name.items():
        idx_to_class[idx] = sly.ObjClass(name, sly.Rectangle)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    meta = sly.ProjectMeta(obj_classes=list(idx_to_class.values()))
    api.project.update_meta(project.id, meta.to_json())

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    images_path = os.path.join(dataset_path, images_folder)

    images_names = [
        im_name for im_name in os.listdir(images_path) if im_name[0] != "."
    ]  # check hidden files in folder

    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

    for images_names_batch in sly.batched(images_names, batch_size=batch_size):
        images_pathes_batch = [os.path.join(images_path, im_name) for im_name in images_names_batch]

        img_infos = api.image.upload_paths(dataset.id, images_names_batch, images_pathes_batch)
        img_ids = [im_info.id for im_info in img_infos]

        anns = [create_ann(image_path) for image_path in images_pathes_batch]
        api.annotation.upload_anns(img_ids, anns)

        progress.iters_done_report(len(images_names_batch))
    return project
