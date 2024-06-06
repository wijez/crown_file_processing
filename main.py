import os
import shutil
import zipfile
import logging

from constant import CrownFileProcessingConstant

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_and_process_zip(file_name):
    try:
        extract_dir_name = os.path.splitext(file_name)[0]
        extract_path = os.path.join(CrownFileProcessingConstant.OUTPUT_PATH, extract_dir_name)
        bot_path = os.path.join(extract_path, CrownFileProcessingConstant.BOT_PATH)
        hand_path = os.path.join(extract_path, CrownFileProcessingConstant.HAND_PATH)

        os.makedirs(bot_path, exist_ok=True)
        os.makedirs(hand_path, exist_ok=True)

        logging.info(f'Starting to extract {file_name} to {extract_path}...')
        with zipfile.ZipFile(os.path.join(CrownFileProcessingConstant.DATA_PATH, file_name), 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        logging.info(f'Finished extracting {file_name} to {extract_path}.')

        # Process files
        files = [f for f in os.listdir(extract_path) if os.path.isfile(os.path.join(extract_path, f))]

        file_dict = {}
        for file in files:
            base_name, ext = os.path.splitext(file)
            if base_name not in file_dict:
                file_dict[base_name] = []
            file_dict[base_name].append(ext)

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
                    file_path = os.path.join(extract_path, f"{base_name}{ext}")
                    shutil.move(file_path, hand_path)

        # Logging and printing results
        result = {
            'count_bot': len(os.listdir(bot_path)),
            'root_pt_bot': os.path.abspath(bot_path),
            'count_hand': len(os.listdir(hand_path)),
            'root_pt_hand': os.path.abspath(hand_path),
        }
        logging.info(result)
        print(result)

    except Exception as e:
        logging.error(f"Error processing {file_name}: {e}")


# List all zip files in data path
zip_files = [f for f in os.listdir(CrownFileProcessingConstant.DATA_PATH) if f.endswith('.zip')]

# Process each zip file
for zip_file in zip_files:
    extract_and_process_zip(zip_file)

logging.info('Completed!')
