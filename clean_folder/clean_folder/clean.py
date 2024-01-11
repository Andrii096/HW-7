import re
from pathlib import Path
import sys
import shutil



UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", 
               "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")


TRANS = {}
images = list()
documents = list()
audio = list()
video = list()
folders = list()
archives = list()
others = list()
unknown = set()
extensions = set()

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"


registered_extensions = {
    "JPEG": images,
    "PNG": images,
    "JPG": images,
    "DOC": documents,
    "PDF": documents,
    "TXT": documents,
    "DOCX": documents,
    "PPTX": documents,
    "XLSX" : documents,
    "ZIP": archives,
    "MP3": audio,
    "MP4": video
}


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ("JPEG", "JPG", "PNG", "TXT", "DOCX", "DOC", "PDF", "PPTX", "XLSX" "OTHER", "ZIP", "MP3", "MP4"):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))


def handle_archive(path: Path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name.replace(".zip", ''))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)
    path.rename(archive_folder / path.name)
    
    try:
        shutil.unpack_archive(str(path.resolve()), archive_folder)
    except shutil.ReadError:
        return
    except FileNotFoundError as e:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def get_folder_objects(root_path):
    for folder in root_path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
            try:
                folder.rmdir()
            except OSError:
                pass

def main():
    folder_path = Path(sys.argv[1])

    scan(folder_path)

    for file in images:
        handle_file(file, folder_path, "IMAGES")

    for file in audio:
        handle_file(file, folder_path, "AUDIO")

    for file in video:
        handle_file(file, folder_path, "VIDEO")

    for file in documents:
        handle_file(file, folder_path, "DOCUMENTS")

    for file in others:
        handle_file(file, folder_path, "OTHERS")

    for file in archives:
        handle_archive(file, folder_path, "ARCHIVE")

    get_folder_objects(folder_path)

if __name__ == '__main__':
    main()