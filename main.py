import os
import shutil
import zipfile
from settings import Config
from constants import crown_file_prc_zip_constants
from fastapi import FastAPI, UploadFile, File, Depends


logger = Config.setup_logging()
app = FastAPI()


def extract_files(zip_file):
    bot_folder = None
    hand_folder = None
    data_folder = f'{crown_file_prc_zip_constants.DATA}'
    for file_name in os.listdir(data_folder):
        if file_name.endswith('.zip'):
            zip_file = os.path.join(data_folder, file_name)
            zip_file_name = os.path.splitext(file_name)[0]
            bot_folder = f'{crown_file_prc_zip_constants.OUTPUT}/{zip_file_name}/bot'
            hand_folder = f'{crown_file_prc_zip_constants.OUTPUT}/{zip_file_name}/hand'
    logger.info(f"Read {zip_file} zip file to get list of files inside")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_names = zip_ref.namelist()

        logger.info("check if the directory exists or not")
        if not os.path.exists(bot_folder):
            os.makedirs(bot_folder)

        if not os.path.exists(hand_folder):
            os.makedirs(hand_folder)

        # Dictionary to track base names and their file types
        base_name_dict = {}

        for file_name in file_names:
            base_name, extension = os.path.splitext(file_name)
            if extension in ['.pdf', '.xml']:
                if base_name in base_name_dict:
                    base_name_dict[base_name].append(file_name)
                else:
                    base_name_dict[base_name] = [file_name]
            else:
                base_name_dict[base_name] = [file_name]

            # Extract files based on the presence of both .pdf and .xml extensions
            count_bot = 0
            count_hand = 0
        for base_name, files in base_name_dict.items():
            if len(files) > 1:
                for file_name in files:
                    count_bot += 1
                    zip_ref.extract(file_name, bot_folder)
            else:
                count_hand += 1
                zip_ref.extract(files[0], hand_folder)
    logger.info(f"in bot have : {count_bot} ")
    logger.info(f"in hand have: {count_hand}")
    result_dict = {
        "count_bot": count_bot,
        "root_pth_boot": bot_folder,
        "count_hand": count_hand,
        "root_pth_hand": hand_folder
    }
    logger.info(f'{result_dict}')
    return result_dict


@app.post("/upload/")
async def upload_files(file: UploadFile = File(...)):
    return extract_files(file)
