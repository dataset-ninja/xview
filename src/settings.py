from typing import Dict, List, Optional, Union

from dataset_tools.templates import (
    AnnotationType,
    Category,
    CVTask,
    Domain,
    Industry,
    License,
    Research,
)

##################################
# * Before uploading to instance #
##################################
PROJECT_NAME: str = "xView 2018"
PROJECT_NAME_FULL: str = "DIUx xView: Objects in Context in Overhead Imagery 2018 Challenge"
HIDE_DATASET = False  # set False when 100% sure about repo quality

##################################
# * After uploading to instance ##
##################################
LICENSE: License = License.CC_BY_NC_SA_4_0()
APPLICATIONS: List[Union[Industry, Domain, Research]] = [Domain.Geospatial()]
CATEGORY: Category = Category.Aerial(extra=Category.Satellite())

CV_TASKS: List[CVTask] = [
    CVTask.ObjectDetection(),
]
ANNOTATION_TYPES: List[AnnotationType] = [AnnotationType.ObjectDetection()]

RELEASE_DATE: Optional[str] = None  # e.g. "YYYY-MM-DD"
if RELEASE_DATE is None:
    RELEASE_YEAR: int = 2018

HOMEPAGE_URL: str = "https://challenge.xviewdataset.org"
# e.g. "https://some.com/dataset/homepage"

PREVIEW_IMAGE_ID: int = 3352644
# This should be filled AFTER uploading images to instance, just ID of any image.

GITHUB_URL: str = "https://github.com/dataset-ninja/xview"
# URL to GitHub repo on dataset ninja (e.g. "https://github.com/dataset-ninja/some-dataset")

##################################
### * Optional after uploading ###
##################################
DOWNLOAD_ORIGINAL_URL: Optional[
    Union[str, dict]
] = "https://challenge.xviewdataset.org/download-links"
# Optional link for downloading original dataset (e.g. "https://some.com/dataset/download")

CLASS2COLOR: Optional[Dict[str, List[str]]] = {
    "fixed-wing aircraft": [230, 25, 75],
    "small aircraft": [60, 180, 75],
    "cargo plane": [255, 225, 25],
    "helicopter": [0, 130, 200],
    "passenger vehicle": [245, 130, 48],
    "small car": [145, 30, 180],
    "bus": [70, 240, 240],
    "pickup truck": [240, 50, 230],
    "utility truck": [210, 245, 60],
    "truck": [250, 190, 212],
    "cargo truck": [0, 128, 128],
    "truck w/box": [220, 190, 255],
    "truck tractor": [170, 110, 40],
    "trailer": [255, 250, 200],
    "truck w/flatbed": [128, 0, 0],
    "truck w/liquid": [170, 255, 195],
    "crane truck": [128, 128, 0],
    "railway vehicle": [255, 215, 180],
    "passenger car": [0, 0, 128],
    "cargo car": [230, 25, 75],
    "flat car": [60, 180, 75],
    "tank car": [255, 225, 25],
    "locomotive": [0, 130, 200],
    "maritime vessel": [245, 130, 48],
    "motorboat": [145, 30, 180],
    "sailboat": [70, 240, 240],
    "tugboat": [240, 50, 230],
    "barge": [210, 245, 60],
    "fishing vessel": [250, 190, 212],
    "ferry": [0, 128, 128],
    "yacht": [220, 190, 255],
    "container ship": [170, 110, 40],
    "oil tanker": [255, 250, 200],
    "engineering vehicle": [128, 0, 0],
    "tower crane": [170, 255, 195],
    "container crane": [128, 128, 0],
    "reach stacker": [255, 215, 180],
    "straddle carrier": [0, 0, 128],
    "mobile crane": [230, 25, 75],
    "dump truck": [60, 180, 75],
    "haul truck": [255, 225, 25],
    "scraper/tractor": [0, 130, 200],
    "front loader/bulldozer": [245, 130, 48],
    "excavator": [145, 30, 180],
    "cement mixer": [70, 240, 240],
    "ground grader": [240, 50, 230],
    "hut/tent": [210, 245, 60],
    "shed": [250, 190, 212],
    "building": [0, 128, 128],
    "aircraft hangar": [220, 190, 255],
    "damaged building": [170, 110, 40],
    "facility": [255, 250, 200],
    "construction site": [128, 0, 0],
    "vehicle lot": [170, 255, 195],
    "helipad": [128, 128, 0],
    "storage tank": [255, 215, 180],
    "shipping container lot": [0, 0, 128],
    "shipping container": [230, 25, 75],
    "pylon": [60, 180, 75],
    "tower": [255, 225, 25],
}


# If specific colors for classes are needed, fill this dict (e.g. {"class1": [255, 0, 0], "class2": [0, 255, 0]})

# If you have more than the one paper, put the most relatable link as the first element of the list
PAPER: Optional[Union[str, List[str]]] = "https://arxiv.org/abs/1802.07856"
BLOGPOST: Optional[Union[str, List[str]]] = None
CITATION_URL: Optional[str] = "https://challenge.xviewdataset.org/rules"
AUTHORS: Optional[List[str]] = [
    "Darius Lam",
    "Richard Kuzma",
    "Kevin McGee",
    "Samuel Dooley",
    "Michael Laielli",
    "Matthew Klaric",
    "Yaroslav Bulatov",
    "Brendan McCord",
]

ORGANIZATION_NAME: Optional[Union[str, List[str]]] = "Defense Innovation Unit (DIU), USA"
ORGANIZATION_URL: Optional[Union[str, List[str]]] = "https://www.diu.mil/"

# Set '__PRETEXT__' or '__POSTTEXT__' as a key with value:str to add custom text. e.g. SLYTAGSPLIT = {'__POSTTEXT__':'some text}
SLYTAGSPLIT: Optional[Dict[str, Union[List[str], str]]] = {
    "__PRETEXT__":"Additionally, objects contain information about ***parent*** classes and ***coordinates***. Explore them in supervisely"
}
TAGS: Optional[List[str]] = None


SECTION_EXPLORE_CUSTOM_DATASETS: Optional[List[str]] = None

##################################
###### ? Checks. Do not edit #####
##################################


def check_names():
    fields_before_upload = [PROJECT_NAME]  # PROJECT_NAME_FULL
    if any([field is None for field in fields_before_upload]):
        raise ValueError("Please fill all fields in settings.py before uploading to instance.")


def get_settings():
    if RELEASE_DATE is not None:
        global RELEASE_YEAR
        RELEASE_YEAR = int(RELEASE_DATE.split("-")[0])

    settings = {
        "project_name": PROJECT_NAME,
        "project_name_full": PROJECT_NAME_FULL or PROJECT_NAME,
        "hide_dataset": HIDE_DATASET,
        "license": LICENSE,
        "applications": APPLICATIONS,
        "category": CATEGORY,
        "cv_tasks": CV_TASKS,
        "annotation_types": ANNOTATION_TYPES,
        "release_year": RELEASE_YEAR,
        "homepage_url": HOMEPAGE_URL,
        "preview_image_id": PREVIEW_IMAGE_ID,
        "github_url": GITHUB_URL,
    }

    if any([field is None for field in settings.values()]):
        raise ValueError("Please fill all fields in settings.py after uploading to instance.")

    settings["release_date"] = RELEASE_DATE
    settings["download_original_url"] = DOWNLOAD_ORIGINAL_URL
    settings["class2color"] = CLASS2COLOR
    settings["paper"] = PAPER
    settings["blog"] = BLOGPOST
    settings["citation_url"] = CITATION_URL
    settings["authors"] = AUTHORS
    settings["organization_name"] = ORGANIZATION_NAME
    settings["organization_url"] = ORGANIZATION_URL
    settings["slytagsplit"] = SLYTAGSPLIT
    settings["tags"] = TAGS

    settings["explore_datasets"] = SECTION_EXPLORE_CUSTOM_DATASETS

    return settings
