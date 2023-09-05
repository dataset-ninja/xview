# http://xviewdataset.org/

import os
from collections import defaultdict

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
    dataset_path = "/mnt/d/datasetninja-raw/xview"
    geojson_path = "/mnt/d/datasetninja-raw/xview/train_labels/xView_train.geojson"
    images_folder = "train_images"
    batch_size = 1
    images_ext = ".tif"
    ds_to_split = {"train": "train_images", "val": "val_images"}

    def create_ann(image_path):
        labels = []
        tags = [sly.Tag(tag_reference, value="OGC:1.3:CRS84")]

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        bboxes_data = name_to_data[get_file_name_with_ext(image_path)]

        for curr_data in bboxes_data:
            label_tags = []
            bbox = list(map(int, curr_data[1].split(",")))
            obj_class = idx_to_class.get(int(curr_data[0]))
            if obj_class is None:
                continue

            parent_value = class_to_parents.get(obj_class.name)
            if parent_value is not None:
                tag_parent = sly.Tag(tag_parents, value=parent_value)
                label_tags.append(tag_parent)

            left = bbox[0]
            right = bbox[2]
            top = bbox[1]
            bottom = bbox[3]
            rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)

            tag_geo = sly.Tag(tag_geo_coords, value=curr_data[2])
            label_tags.append(tag_geo)
            label = sly.Label(rectangle, obj_class, tags=label_tags)
            labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    name_to_data = defaultdict(list)
    with open(geojson_path) as f:
        gj = geojson.load(f)["features"]
        for curr_gj in gj:
            geo_coords = curr_gj["geometry"]["coordinates"][0]
            str_geo_coords = str(geo_coords)[1:-1]
            curr_data = curr_gj["properties"]
            name_to_data[curr_data["image_id"]].append(
                (curr_data["type_id"], curr_data["bounds_imcoords"], str_geo_coords)
            )

    idx_to_class_name = {
        11: "fixed-wing aircraft",
        12: "small aircraft",
        13: "cargo plane",
        15: "helicopter",
        17: "passenger vehicle",
        18: "small car",
        19: "bus",
        20: "pickup truck",
        21: "utility truck",
        23: "truck",
        24: "cargo truck",
        25: "truck w/box",
        26: "truck tractor",
        27: "trailer",
        28: "truck w/flatbed",
        29: "truck w/liquid",
        32: "crane truck",
        33: "railway vehicle",
        34: "passenger car",
        35: "cargo car",
        36: "flat car",
        37: "tank car",
        38: "locomotive",
        40: "maritime vessel",
        41: "motorboat",
        42: "sailboat",
        44: "tugboat",
        45: "barge",
        47: "fishing vessel",
        49: "ferry",
        50: "yacht",
        51: "container ship",
        52: "oil tanker",
        53: "engineering vehicle",
        54: "tower crane",
        55: "container crane",
        56: "reach stacker",
        57: "straddle carrier",
        59: "mobile crane",
        60: "dump truck",
        61: "haul truck",
        62: "scraper/tractor",
        63: "front loader/bulldozer",
        64: "excavator",
        65: "cement mixer",
        66: "ground grader",
        71: "hut/tent",
        72: "shed",
        73: "building",
        74: "aircraft hangar",
        76: "damaged building",
        77: "facility",
        79: "construction site",
        83: "vehicle lot",
        84: "helipad",
        86: "storage tank",
        89: "shipping container lot",
        91: "shipping container",
        93: "pylon",
        94: "tower",
    }

    class_to_parents = {
        "small aircraft": "fixed-wing aircraft",
        "cargo plane": "fixed-wing aircraft",
        "small car": "passenger vehicle",
        "bus": "passenger vehicle",
        "hut/tent": "building",
        "shed": "building",
        "aircraft hangar": "building",
        "damaged building": "building",
        "facility": "building",
        "pickup truck": "truck",
        "utility truck": "truck",
        "cargo truck": "truck",
        "truck w/box": "truck",
        "truck tractor trailer": "truck",
        "truck w/flatbed": "truck",
        "truck w/liquid": "truck",
        "passenger car": "railway vehicle",
        "cargo car": "railway vehicle",
        "flat car": "railway vehicle",
        "tank car": "railway vehicle",
        "locomotive": "railway vehicle",
        "motorboat": "maritime vessel",
        "sailboat": "maritime vessel",
        "tugboat": "maritime vessel",
        "barge": "maritime vessel",
        "fishing vessel": "maritime vessel",
        "ferry": "maritime vessel",
        "yacht": "maritime vessel",
        "container ship": "maritime vessel",
        "oil tanker": "maritime vessel",
        "tower crane": "engineering vehicle",
        "container crane": "engineering vehicle",
        "reach stacker": "engineering vehicle",
        "straddle carrier": "engineering vehicle",
        "mobile crane": "engineering vehicle",
        "dump truck": "engineering vehicle",
        "haul truck": "engineering vehicle",
        "scraper/tractor": "engineering vehicle",
        "front loader/bulldozer": "engineering vehicle",
        "excavator": "engineering vehicle",
        "cement mixer": "engineering vehicle",
        "ground grader": "engineering vehicle",
        "crane truck": "engineering vehicle",
    }

    idx_to_class = {}
    for idx, name in idx_to_class_name.items():
        idx_to_class[idx] = sly.ObjClass(name, sly.Rectangle)

    tag_reference = sly.TagMeta(
        "coordinate reference system",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["OGC:1.3:CRS84"],
    )
    tag_geo_coords = sly.TagMeta("coordinates", sly.TagValueType.ANY_STRING)

    tag_parents = sly.TagMeta("parents", sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    meta = sly.ProjectMeta(
        obj_classes=list(idx_to_class.values()),
        tag_metas=[tag_reference, tag_geo_coords, tag_parents],
    )
    api.project.update_meta(project.id, meta.to_json())

    for ds_name, images_folder in ds_to_split.items():
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        images_path = os.path.join(dataset_path, images_folder)

        images_names = [
            im_name for im_name in os.listdir(images_path) if im_name[0] != "."
        ]  # check hidden files in folder

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

        for images_names_batch in sly.batched(images_names, batch_size=batch_size):
            images_pathes_batch = [
                os.path.join(images_path, im_name) for im_name in images_names_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, images_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in images_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))
    return project
