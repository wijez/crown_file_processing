import os
import shutil
import zipfile
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile
from constant import CrownFileProcessingConstant

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.post("/process-zip/")
async def process_zip(file: UploadFile):
    return extract_and_process_zip(file)


def extract_and_process_zip(file):
    try:
        os.makedirs(CrownFileProcessingConstant.DATA_PATH, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # Save the uploaded file
        zip_path = os.path.join(CrownFileProcessingConstant.DATA_PATH, timestamp + file.filename)
        with open(zip_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract the ZIP file
        extract_dir_name = os.path.splitext(timestamp + file.filename)[0]
        extract_path = os.path.join(CrownFileProcessingConstant.OUTPUT_PATH, extract_dir_name)
        bot_path = os.path.join(extract_path, CrownFileProcessingConstant.BOT_PATH)
        hand_path = os.path.join(extract_path, CrownFileProcessingConstant.HAND_PATH)

        os.makedirs(bot_path, exist_ok=True)
        os.makedirs(hand_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        file_dict = {}
        for item in os.listdir(extract_path):
            item_path = os.path.join(extract_path, item)
            if os.path.isfile(item_path):
                base_name, ext = os.path.splitext(item)
                file_dict.setdefault(base_name, []).append(ext)

        for base_name, exts in file_dict.items():
            xml_file = f"{base_name}.xml"
            pdf_file = f"{base_name}.pdf"
            xml_path = os.path.join(extract_path, xml_file)
            pdf_path = os.path.join(extract_path, pdf_file)

            if ".xml" in exts and ".pdf" in exts:
                shutil.move(xml_path, bot_path)
                shutil.move(pdf_path, bot_path)
            else:
                for ext in exts:
                    shutil.move(os.path.join(extract_path, f"{base_name}{ext}"), hand_path)

        result = {
            'count_bot': len(os.listdir(bot_path)),
            'root_pt_bot': os.path.abspath(bot_path),
            'count_hand': len(os.listdir(hand_path)),
            'root_pt_hand': os.path.abspath(hand_path),
        }

        return result
    except Exception as e:
        logging.error(f"Error processing {file.filename}: {e}")
        return {"error": str(e)}
