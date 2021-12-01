
import os
import re


def get_loc(subsystem, version):
    """
    Get the total line of code for this version and subsystem using cloc command and os.popen
    """

    with open("stats/num_total_lines/{}.csv".format(subsystem), "r") as f:
        lines = f.readlines()
        for line in lines:
            if re.search(r"^{}".format(version), line):
                sum = line.split(",")[11]
                return int(sum)
                #return int(line.split(",")[11]) #Sum is on 11th line
    return 0




def main():
    # List of subsystem names
    # Where a subsystem refers to a specific subfolder in react
    # 
    subsystem_names = [
        "ContainerShip",
        "Examples",
        "IntegrationTests",
        "JSCLegacyProfiler",
        "Libraries",
        "RNTester",
        "React",
        "ReactAndroid",
        "ReactCommon",
        "ReactNative",
        "Tools",
        "aggregate",
        "babel-preset",
        "blog",
        "bots",
        "danger",
        "docs",
        "flow-github",
        "flow-typed",
        "flow",
        "gradle",
        "jest",
        "jestSupport",
        "keystores",
        "lib",
        "lint",
        "local-cli",
        "packager",
        "packages",
        "private-cli",
        "react-native-cli",
        "react-native-git-upgrade",
        "react-native-gradle",
        "repo-config",
        "scripts",
        "template",
        "third-party-podspecs",
        "website",
        "tools"
    ]

    VERSIONS_RANGE = [r for r in range(5, 66) if r != 16] #Version 16 missing
    STATS_FOLDER = "stats"
    file_name = "growth_metric.csv"

    #Write file header
    with open(os.path.join(STATS_FOLDER, file_name), "w") as f:
        f.write("subsystem,growth_rate, num_languages\n")

    num_subsystems= 0
    #open the count_of_subsystems.csv for reading and add number of subsystems for version 65
    with open("stats/count_of_subsystem_num_languages.csv", "r") as f2:
        #Find line that starts with 65
        for line in f2:
            if re.search(r"^5", line):
                #Get a list of the number of files for each subsystem
                num_subsystems = line.split(",")


    #Iterate over subsystems
    for i, subsystem in enumerate(subsystem_names):
        #Iterate over versions
        #Get the total number of loc for each version
        next_version_loc = 0
        total_ratio_increase = 0
        number_of_versions_with_loc = 0
        for version in VERSIONS_RANGE:
            #Get the stats for the current version
            loc = get_loc(subsystem, version)

            if loc != 0:
                number_of_versions_with_loc += 1

            delta_loc = loc - next_version_loc
            next_version_loc = loc

            if loc + next_version_loc == 0:
                continue

            total_ratio_increase += delta_loc / (loc+next_version_loc)

        if number_of_versions_with_loc == 0:
            growth_metric = 0
            print("Subsystem {} has no versions with loc".format(subsystem))
        else:
            growth_metric = total_ratio_increase / number_of_versions_with_loc

        #Write the growth metric to file
        with open(os.path.join(STATS_FOLDER, file_name), "a") as f:
            f.write(subsystem + "," + str(growth_metric) + "," + str(num_subsystems[i+1]) +"\n")




if __name__ == "__main__":
    main()