import os
import shutil
from datetime import datetime, time

def recursive_copy(source_dir, destination_dir):
    modified_files = []
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() != 'upload']

        if root == source_dir:
            continue

        for file in files:
            if file.startswith('.'):
                continue

            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, source_dir)
            new_file_name = "_".join(relative_path.split(os.sep) + [file])
            destination_path = os.path.join(destination_dir, new_file_name)
            
            shutil.copy2(source_path, destination_path)
            source_stat = os.stat(source_path)
            os.utime(destination_path, (source_stat.st_atime, source_stat.st_mtime))
            print(f"Copied: {source_path} -> {destination_path}")

            if new_file_name.startswith("Public"):
                modified_files.append((new_file_name, datetime.fromtimestamp(source_stat.st_mtime)))

    return modified_files

def clean_destination(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    print(f"All files in {directory} have been removed.")

def update_readme_changelog(readme_path, modified_files):
    with open(readme_path, 'r') as file:
        content = file.readlines()

    changelog_index = content.index("## Changelog\n")
    latest_date = datetime.strptime(content[changelog_index + 1].strip("### \n"), "%d-%m-%Y")
    # Create a new datetime object with the time set to the end of the day
    latest_date = datetime.combine(latest_date.date(), time(23, 59, 59))

    new_entries = []
    for file, mod_date in modified_files:
        if mod_date > latest_date:
            new_entries.append(f"- Updated {file}\n")

    if new_entries:
        new_date = max(mod_date for _, mod_date in modified_files).strftime("%d-%m-%Y")
        new_changelog = [f"### {new_date}\n"] + new_entries + ["\n"]
        content = content[:changelog_index+1] + new_changelog + content[changelog_index+1:]

        with open(readme_path, 'w') as file:
            file.writelines(content)
        print(f"Updated README.md with new changelog entries.")

# Example usage
source_directory = "./"
destination_directory = "upload"
readme_path = "./README.md"

os.makedirs(destination_directory, exist_ok=True)
clean_destination(destination_directory)
modified_files = recursive_copy(source_directory, destination_directory)
# update_readme_changelog(readme_path, modified_files)