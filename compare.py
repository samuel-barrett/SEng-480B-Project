import os
import re

def get_num_lines_for_file_type(folder_name: str, file_types: [str]):
    num_lines = 0
    for file_type in file_types:
        read_obj = os.popen("( find ./{} -name '{}' -print0 | xargs -0 cat ) | wc -l".format(folder_name, file_type), 'r')
        num_lines += int(read_obj.read())
    return num_lines

def get_line_numbers_for_folder(version: int, folder_name: str, out_file_name: str, already_found: bool):

    if already_found:
        write_mode = 'a'
    else:
        write_mode = 'w'


    with open(out_file_name, write_mode) as out_file:

        if not already_found:
            print("Version Name,JavaScript,Java, C++ source, C source,C/C++ Header,Ruby,Shell,BUCK,XML", file=out_file)

        #print("Finding info for for version {}".format(folder_name))
        print("{}".format(version), end=',', file=out_file)

        #Javascript lines of code
        javascript_lines = get_num_lines_for_file_type(folder_name, ['*.js'])
        print("{}".format(javascript_lines), end=",", file=out_file)

        #Java lines of code
        java_lines = get_num_lines_for_file_type(folder_name, ['*.java'])
        print("{}".format(java_lines), end=",", file=out_file)

        #C++ source lines of code
        cpp_source_lines = get_num_lines_for_file_type(folder_name, ['*.cpp'])
        print("{}".format(cpp_source_lines), end=",", file=out_file)

        #C source lines of code
        c_source_lines = get_num_lines_for_file_type(folder_name, ['*.c'])
        print("{}".format(c_source_lines), end=",", file=out_file)

        #C header lines of code
        c_cpp_header_lines = get_num_lines_for_file_type(folder_name, ['*.h', '*.hpp']) #Data set does not have .hpp files but included for completeness
        print("{}".format(c_cpp_header_lines), end=",", file=out_file)

        #Ruby lines of code
        ruby_lines = get_num_lines_for_file_type(folder_name, ['*.rb'])
        print("{}".format(ruby_lines), end=",", file=out_file)

        #Shell lines of code
        shell_lines = get_num_lines_for_file_type(folder_name, ['*.sh', '*.bash','*.zsh','*.command'])
        print("{}".format(shell_lines), end=",", file=out_file)

        #BUCK lines of code
        buck_lines = get_num_lines_for_file_type(folder_name, ['BUCK'])
        print("{}".format(buck_lines), end=",", file=out_file)

        #XML lines of code
        xml_lines = get_num_lines_for_file_type(folder_name, ['*.xml'])
        print("{}".format(xml_lines), file = out_file)

def main():
    VERSIONS_RANGE = range(5, 66)


    stats_folder_name = "stats"
    os.system("mkdir ./{}".format(stats_folder_name))

    folder_names_found = []
    already_found = False

    for i in VERSIONS_RANGE:
        version_name = '0.{}-stable'.format(i)

        read_obj = os.popen("file {}/* | grep directory".format(version_name), 'r')
        folders = read_obj.read().split(' ')
        
        #Get name of subdirecotory in folders using regex
        for folder in folders:
            group = re.search(r'((?<=\/)[^\/]*):$', folder)
            if not group:
                continue
            folder_name = group.group(1)

            #Check if folder in list of folders found
            if folder_name in folder_names_found:
                already_found = True
            else :
                folder_names_found.append(folder_name)
                already_found = False

            #print("Finding info for folder_name:{}".format(folder_name))
            get_line_numbers_for_folder(i, "./{}/{}".format(version_name, folder_name), './{}/{}.csv'.format(stats_folder_name, folder_name), already_found)


if __name__ == "__main__":
    main()