import os

def get_documents_directory():
    home_directory = os.path.expanduser('~')

    if os.name == 'nt':
        documents_directory = os.path.join(home_directory, 'Documents')
    else:
        documents_directory = os.path.join(home_directory, 'Documents')

    return documents_directory