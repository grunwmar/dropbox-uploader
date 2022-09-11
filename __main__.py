import os
import logging
import sys
import traceback
import dropbox # pip install dropbox
from dropbox.files import WriteMode


logFormatterTxt = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logFormatterConsole = logging.Formatter("%(asctime)s [\033[1;32m%(levelname)-5.5s\033[0m]  %(message)s")

log = logging.getLogger()
log.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("./log_file.log")
fileHandler.setFormatter(logFormatterTxt)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatterConsole)
log.addHandler(consoleHandler)


class DropboxUploader:
    """Simple class to easily upload directory to Dropbox."""

    def __init__(self, target_dir:str, db_token:str):
        self._target_dir = target_dir

        if db_token is not None:
            log.debug('Connecting to Dropbox...')
            self._dbx = dropbox.Dropbox(db_token)
        else:
            raise ValueError('None is not valid token')
        log.debug('Connected.')


    def __enter__(self):
        return self


    def __exit__(self, *params):
        self._dbx.close()
        log.debug('Connection closed.')


    def upload(self, local_file:str, remote_file:str):
        try:
            with open(local_file, 'rb') as file:
                try:
                    remote_file = os.path.join(self._target_dir, remote_file)
                    self._dbx.files_upload(file.read(), remote_file, mode=WriteMode('overwrite'))
                except Exception as exc2:
                    print(exc2)
                    traceback.print_exc()
        except Exception as exc1:
            print(exc1)
            traceback.print_exc()


def main(uploaded_dir_path:str):
    """Main function."""

    # access token to authorize in Dropbox is given through env. variable
    # var DB_ACCESS_TOKEN needs to be set, else ValueError is raised
    with DropboxUploader(target_dir=os.environ.get('DB_TARGET_DIR'),
                         db_token=os.environ.get('DB_ACCESS_TOKEN')) as db:

        source_dir = os.path.normpath(uploaded_dir_path)
        base_dir = os.path.basename(source_dir)

        for subdir, dirs, files in os.walk(source_dir):
            for file in files:
                dir_path = subdir.replace(source_dir, "")
                dir_path = os.path.join(base_dir + "//" + dir_path)

                remote_filepath = os.path.normpath(os.path.join(dir_path, file))
                local_filepath = os.path.normpath(os.path.join(subdir, file))

                log.info(remote_filepath)

                db.upload(local_filepath, remote_filepath)


if __name__ == "__main__":

    if len(sys.argv) > 1:
        uploaded_dir_path = sys.argv[1]
        if os.path.isdir(uploaded_dir_path):
            main(uploaded_dir_path)
        else:
            log.error(f"Directory '{uploaded_dir_path}' does not exists.")
    else:
        log.error(f"No input")
