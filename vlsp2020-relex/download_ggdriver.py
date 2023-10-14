# Install the package before using
# pip install googledrivedownloader
import argparse
from google_drive_downloader import GoogleDriveDownloader as gdd


def save_at_folder(file_id, save_path, unzip=False):
    gdd.download_file_from_google_drive(file_id=file_id,
                                        dest_path=save_path,
                                        unzip=unzip)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file_id',
        type=str,
        help='Google file id'
    )
    parser.add_argument(
        'save_path',
        type=str,
        help='Path to save the file'
    )
    parser.add_argument(
        '--unzip',
        action='store_true',
        help='If --unzip is specify, unzip the file'
    )
    args = parser.parse_args()
    unzip = True if args.unzip else False
    
    save_at_folder(args.file_id, args.save_path, unzip=unzip)


if __name__ == '__main__':
    main()
