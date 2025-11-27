import os

def format_file_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{round(size_in_bytes / 1024, 2)} KB"
    else:
        return f"{round(size_in_bytes / (1024 * 1024), 2)} MB"

def get_file_info_list(directory):
    files = []
    if os.path.exists(directory):
        for f in os.listdir(directory):
            path = os.path.join(directory, f)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                files.append({
                    "name": f, 
                    "size": format_file_size(size)
                })
    return files