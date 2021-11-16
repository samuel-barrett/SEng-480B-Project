import os
import re
from contextlib import ExitStack

def get_number_of_lines_for_folder(version: int, subsystem_name: str, subsystem_already_found: bool, folder_types: list):

    read_obj = os.popen("cloc 0.{}-stable/{} -T=5".format(version,subsystem_name), 'r')
    lines = read_obj.read().split('\n')

    if subsystem_already_found:
        write_mode = 'a'
    else:
        write_mode = 'w'

    stats_folder = "stats"


    filenames = ["./{}/{}/{}.csv".format(stats_folder, folder_type, subsystem_name) for folder_type in folder_types]


    #Dictionary to store line information
    #Values contain the number of file, number of blank lines, number of 
    #commented lines, and number of code lines respectively
    line_info_for_code_type = {
        "JavaScript":[0,0,0,0],
        "Java":[0,0,0,0], 
        "C++":[0,0,0,0], 
        "C":[0,0,0,0],
        "C + C++ Header":[0,0,0,0],
        "Objective-C":[0,0,0,0],
        "Ruby":[0,0,0,0],
        "BUCK":[0,0,0,0],
        "XML":[0,0,0,0],
        "Markdown":[0,0,0,0],
        "JSON":[0,0,0,0],
        "Makefile":[0,0,0,0],
        "Bash":[0,0,0,0],
        "HTML":[0,0,0,0],
        "CSS":[0,0,0,0],
        "Bourne Shell":[0,0,0,0],
        "Bourne Again Shell":[0,0,0,0],
        "YAML":[0,0,0,0],
        "Objective-C++":[0,0,0,0],
        "make":[0,0,0,0],
        "Gradle":[0,0,0,0],
        "ProGuard":[0,0,0,0],
        "awk":[0,0,0,0],
        "Python":[0,0,0,0],
        "DOS Batch":[0,0,0,0],
        "Assembly":[0,0,0,0],
        "JSX":[0,0,0,0],
        "Sass":[0,0,0,0],
        "Dockerfile":[0,0,0,0],
        "Kotlin":[0,0,0,0],
        "Starlark":[0,0,0,0],
        "CMake":[0,0,0,0],
        "Aggregate stats":[0,0,0,0]
    }

    with ExitStack() as stack:
        #Open all file that will be written to this iteration in scope of ExitStack() object
        files = [stack.enter_context(open(filename, write_mode)) for filename in filenames]

        #Get number of lines for each code type broken down into different types
        language_line_found = False
        for line in lines:
            if line.startswith("Language"):
                language_line_found = True
                continue
            
            if not language_line_found:
                continue

            #Check if line is a bunch of dashes
            if line.startswith("----"):
                continue

            #Get the type of file, which is the first word in the line
            #Also get the number of files which is the second word and a number
            #Get the number of blank lines which is the third word and a number
            #Get the number of comment lines which is the fourth word and a number
            #Get the number of code lines which is the fifth word and a number
            group = re.search(r'^([^\s]+(\s[^\s]+)*)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)', line)
            if not group: 
                continue

            file_type = group.group(1)
            #num_files = group.group(3)
            #num_blank_lines = group.group(4)
            #num_comment_lines = group.group(5)
            #num_code_lines = group.group(6)

            if file_type == "C/C++ Header": #Not a valid folder name because of the /
                file_type = "C+C++ Header" 
            elif file_type == "SUM:":
                file_type = "Aggregate stats"
            
            #Get the line information for the file type
            #check if file_type in line_info_for_code_type
            if not file_type in line_info_for_code_type:
                raise RuntimeError("File type {} not found in line_info_for_code_type".format(file_type))

            line_info_for_code_type[file_type] = [int(group.group(3)), int(group.group(4)), int(group.group(5)), int(group.group(6))]


        if not subsystem_already_found:
            #Write the header for the file
            #Includes version number, and code types from dictionary
            for file in files:
                print("Version", end='', file=file)
                for code_type in line_info_for_code_type:
                    print(",{}".format(code_type), end='', file=file)
                print("", file=file) #New line 08
    

        #Print the version name and the line information for each file type as a comma seperated list
        #Print the different values to each file one by one
        for (i,f) in enumerate(files):
            print(version, end='', file=f)
            j=0
            for (key, value) in line_info_for_code_type.items():
                j+=1
                print(","+str(value[i]), end='', file=f)
            print("", file=f)

        #Reset the line information for the code type
        for (key, value) in line_info_for_code_type.items():
            line_info_for_code_type[key] = [0,0,0,0]


def main():
    VERSIONS_RANGE = [r for r in range(5, 66) if r != 16] #Version 16 missing
    FOLDER_TYPES = ["Num Files", "Num Blank Lines", "Num Commented Lines", "Num Code Lines"]
    STATS_FOLDER = "stats"

    [os.system("mkdir -p \'./{}/{}\'".format(STATS_FOLDER, FOLDER_TYPE)) for FOLDER_TYPE in FOLDER_TYPES]
 
    stats_folder = "stats"
    os.system("mkdir ./{}".format(stats_folder))

    subsystem_names_found = []
    subsystem_already_found = False

    for i in VERSIONS_RANGE:
        version_name = '0.{}-stable'.format(i)
        print("Getting stats for {}".format(version_name))

        read_obj = os.popen("file {}/* | grep directory".format(version_name), 'r')
        folders = read_obj.read().split(' ')
        
        #Get name of subdirecotory in folders using regex
        for folder in folders:
            group = re.search(r'((?<=\/)[^\/]*):$', folder)
            if not group:
                continue
            subsystem_name = group.group(1)

            #Check if folder in list of folders found
            if subsystem_name in subsystem_names_found:
                subsystem_already_found = True
            else:
                subsystem_names_found.append(subsystem_name)
                subsystem_already_found = False

            get_number_of_lines_for_folder(i, subsystem_name, subsystem_already_found, FOLDER_TYPES)

if __name__ == "__main__":
    main()