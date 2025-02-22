import os, sys

sys.path.append('/sise/home/reutme/muscle-formation-diff')
sys.path.append(os.path.abspath('..'))
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from data_layer.utils import *
from configuration import consts



def concat_files(data_files):
    """
    Concatenates multiple files containing DataFrame chunks into a single DataFrame.
    :param data_files: (list) List of file paths.
    :return: df_all_chunks (pd.DataFrame) Concatenated DataFrame.
    Prints:
        - Exception message if an error occurs during loading or concatenation.
    """
    df_all_chunks = pd.DataFrame()
    for file in data_files:
        try:
            chunk_df = pickle.load(open(file, 'rb'))
            chunk_df = downcast_df(chunk_df)
            if chunk_df.shape[0] > 0:
                df_all_chunks = pd.concat([df_all_chunks, chunk_df], ignore_index=True)
        except Exception as e:
            print(e)
            continue

    return df_all_chunks


def delete_temporery_files(data_files, txt_path_file):
    """
    Deletes temporary files and a text file.
    :param data_files: (list) List of file paths to be deleted.
    :param txt_path_file: (str) Path of the text file to be deleted.
    :return: None
    Prints:
        - Deletion status messages.
        - Exception message if an error occurs during file deletion.
    """
    try:
        for file in data_files:
            os.remove(file)
        os.remove(txt_path_file)
        print("finished to delete files, deleting txt file")
    except Exception as e:
        print(e)


def concat_data_portions(files_location_path, saving_path):
    """
    Concatenates data portions of transformed tsfresh data from multiple files into a single DataFrame.
    :param files_location_path: (str) location of data portaions.
    :param saving_path: (str) path to save the new concatenated file to.

    :return: None
    :prints:
        - Running information, including the modality and video name.
        - Directory path where the files are located.
        - Information about deleting temporary files, including file deletion status.
    """

    def read_txt_file(path):
        with open(path, 'r') as f:
            data_files = f.read().splitlines()
        return data_files

    # concat dfs
    txt_path_file = f"{files_location_path}files_dict.txt"
    data_files = read_txt_file(txt_path_file)
    df_all_chunks = concat_files(data_files)

    # save data
    if not df_all_chunks.empty:
        pickle.dump(df_all_chunks, open(saving_path, 'wb'))
    else:
        print("no data to save")

    delete_temporery_files(data_files, txt_path_file)


if __name__ == '__main__':
    modality = sys.argv[1]
    vid_info = consts.vid_info_dict[os.getenv('SLURM_ARRAY_TASK_ID')]
    files_path = consts.storage_path + f"data/mastodon/ts_transformed/{modality}/{consts.IMPUTE_METHOD}_{consts.IMPUTE_FUNC}/{vid_info['name']}/"
    data_save_csv_path = files_path + f"merged_chunks_reg={consts.REG_METHOD},local_den=False,win size={consts.WIN_SIZE}.pkl"

    concat_data_portions(files_path, data_save_csv_path)
