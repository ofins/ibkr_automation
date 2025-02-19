import os


def delete_all_files(folder_path):
    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):  # Ensure it's a file
            os.remove(file_path)
            print(f"Deleted: {file_path}")


delete_all_files("dist/images")
