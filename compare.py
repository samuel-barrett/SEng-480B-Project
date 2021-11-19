import os
import re
from contextlib import ExitStack

#Dictionary to store line information
#Values contain the number of file, number of blank lines, number of 
#commented lines, and number of code lines respectively
primary_file_types_stats = {
    "JavaScript":[0,0,0,0,0,0],
    "Java":[0,0,0,0,0,0], 
    "C&C++":[0,0,0,0,0,0],
    "Objective-C&C++":[0,0,0,0,0,0],
    "Markdown":[0,0,0,0,0,0],
    "Other":[0,0,0,0,0,0],
    "Sum":[0,0,0,0,0,0]
}

subsystem_names = {
    "ContainerShip":0,
    "Examples":0,
    "IntegrationTests":0,
    "JSCLegacyProfiler":0,
    "Libraries":0,
    "RNTester":0,
    "React":0,
    "ReactAndroid":0,
    "ReactCommon":0,
    "ReactNative":0,
    "Tools":0,
    "aggregate":0,
    "babel-preset":0,
    "blog":0,
    "bots":0,
    "danger":0,
    "docs":0,
    "flow-github":0,
    "flow-typed":0,
    "flow":0,
    "gradle":0,
    "jest":0,
    "jestSupport":0,
    "keystores":0,
    "lib":0,
    "lint":0,
    "local-cli":0,
    "packager":0,
    "packages":0,
    "private-cli":0,
    "react-native-cli":0,
    "react-native-git-upgrade":0,
    "react-native-gradle":0,
    "repo-config":0,
    "scripts":0,
    "template":0,
    "third-party-podspecs":0,
    "website":0,
    "tools":0
}


def process_line(line:str):

    #Check if line is a bunch of dashes
    if line.startswith("----"):
        return

    #Get the type of file, which is the first word in the line
    #Also get the number of files which is the second word and a number
    #Get the number of blank lines which is the third word and a number
    #Get the number of comment lines which is the fourth word and a number
    #Get the number of code lines which is the fifth word and a number
    group = re.search(r'^([^\s]+(\s[^\s]+)*)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)', line)
    if not group: 
        return

    file_type = group.group(1)
    num_files = int(group.group(3))
    num_blank_lines = int(group.group(4))
    num_comment_lines = int(group.group(5))
    num_code_lines = int(group.group(6))
    num_total_lines = num_blank_lines + num_comment_lines + num_code_lines
    num_non_empty_lines = num_code_lines + num_comment_lines

    if file_type == "C/C++ Header": #Not a valid folder name because of the /
        file_type = "C&C++ Header" 
    elif file_type == "SUM:":
        file_type = "Sum"

    #Group C/C++ Code together
    if file_type == "C/C++ Header" or file_type == "C" or file_type == "C++":
        file_type = "C&C++"
    
    #Group Objective-C and Objective-C++ together
    if file_type == "Objective-C" or file_type == "Objective-C++":
        file_type = "Objective-C&C++"
    
    #Get the line information for the file type
    #check if file_type in line_info_for_code_type
    if not file_type in primary_file_types_stats:
        file_type = "Other"
    
    return [file_type, num_files, num_blank_lines, num_comment_lines, num_code_lines, num_total_lines, num_non_empty_lines]


def get_number_of_lines_for_folder(version: int, subsystem_name: str, subsystem_already_found: bool, folder_types: list):

    #Get stats about file line counts using cloc
    read_obj = os.popen("cloc 0.{}-stable/{} -T=5".format(version,subsystem_name), 'r')
    lines = read_obj.read().split('\n')

    if subsystem_already_found:
        write_mode = 'a'
    else:
        write_mode = 'w'
    stats_folder = "stats"

    filenames = ["./{}/{}/{}.csv".format(stats_folder, folder_type, subsystem_name) for folder_type in folder_types]

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
            
            line_data = process_line(line)
            if not line_data:
                continue

            

            #Write information to a file about how many file types were found for this subsystem
            if subsystem_name != "*":
                subsystem_names[subsystem_name] += 1
                

            #Key is first value in line list and value is the rest of the list
            code_type = line_data[0]
            line_data = line_data[1:]
            for i,data in enumerate(line_data):
                primary_file_types_stats[code_type][i] += int(data)

        
        #Print primary_file_type_stats to console
        #for file_type in primary_file_types_stats:
        #    print("{}: {}".format(file_type, primary_file_types_stats[file_type]))

        if not subsystem_already_found:
            #Write the header for the file
            #Includes version number, and code types from dictionary
            for file in files:
                print("Version", end='', file=file)
                for code_type in primary_file_types_stats:
                    print(",{}".format(code_type), end='', file=file)
                print("", file=file) #New line 08
    

        #Print the version name and the line information for each file type as a comma seperated list
        #Print the different values to each file one by one
        for (i,f) in enumerate(files):
            print(version, end='', file=f)
            for (key, value) in primary_file_types_stats.items():
                print(","+str(value[i]), end='', file=f)
            print("", file=f)

        #Reset the line information for the code type
        for (key, value) in primary_file_types_stats.items():
            primary_file_types_stats[key] = [0,0,0,0,0,0]


def main():

    VERSIONS_RANGE = [r for r in range(5, 66) if r != 16] #Version 16 missing
    FOLDER_TYPES = ["num_files", "num_blank_lines", "num_commented_lines", "num_code_lines", "num_total_lines", "num_non_empty_lines"]
    STATS_FOLDER = "stats"


    #Make the necessary folders
    stats_folder = "stats"
    os.system("mkdir ./{}".format(stats_folder))

    [os.system("mkdir -p \'./{}/{}\'".format(STATS_FOLDER, FOLDER_TYPE)) for FOLDER_TYPE in FOLDER_TYPES]

    subsystem_names_found = []
    subsystem_already_found = False

    #Write header of subsystem counts by iterating over dictionary and printing to csv
    with open("count_of_subsystem_num_languages.csv", 'w') as f:
        print("Version", end='', file=f)
        for subsystem in subsystem_names:
            print(",{}".format(subsystem), end='', file=f)
        print("", file=f)

    #Iterate through each version of code
    for version_num in VERSIONS_RANGE:
        version_name = '0.{}-stable'.format(version_num)
        print("Getting stats for {}".format(version_name))

        #Get subsystem names for version
        read_obj = os.popen("file {}/* | grep directory".format(version_name), 'r')
        folders = read_obj.read().split(' ')

        #Get overall stats for each version
        aggregate_stats_name = "*"
        if aggregate_stats_name in subsystem_names_found:
            subsystem_already_found = True
        else:
            subsystem_already_found = False
            subsystem_names_found.append(aggregate_stats_name)
        get_number_of_lines_for_folder(version_num, aggregate_stats_name, subsystem_already_found, FOLDER_TYPES)
        
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

            get_number_of_lines_for_folder(version_num, subsystem_name, subsystem_already_found, FOLDER_TYPES)

        #Print subsystem names found to csv
        with open("count_of_subsystem_num_languages.csv", 'a') as f:
            print(version_name, end='', file=f)
            for subsystem in subsystem_names:
                if subsystem == "*":
                    continue
                print(","+str(subsystem_names[subsystem]), end='', file=f)
            print("", file=f)

        #Reset subsystem names found
        for subsystem in subsystem_names:
            subsystem_names[subsystem] = 0

        
    #For stats type, change the aggregate data name from '*.csv' to aggregate":0,
    for folder_type in FOLDER_TYPES:
        os.system("mv \'./{}/{}/*.csv\' ./{}/{}/aggregate.csv".format(STATS_FOLDER, folder_type, STATS_FOLDER, folder_type))


if __name__ == "__main__":
    main()