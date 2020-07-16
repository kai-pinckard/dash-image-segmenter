"""
This script will prompt the user for the version tag of
the new docker image container they are building. The user
should determine what this tag is by checking the latest tag
on dockerhub and then incrementing it. The script will then
automatically build the new docker container for both the
seeserver and the seesegment containers. The script will then
push these containers to dockerhub so that they can be used
by kubenretes.The script will then update the yaml files so
that kubernetes will use the newly created docker images with
the version tag specified.
"""


import os
import sys

privilege_modifier = ""
# This check is here because sudo is required on linux and does not work on windows.
# Note all versions of windows report as win32 even 64 bit versions.
if sys.platform == "win32":
    privilege_modifier = ""
else:
    privilege_modifier = "sudo "

# Get the new version tag from the user.
print("Please enter the version tag you want to use.")
print("(Check what the latest is on Dockerhub first and increment it)")
print("(An example version tag is \"0.0.9\")")
version_tag = raw_input("version tag: ")

print("Building the images.")

# Create the build commands.
build_segmenter_command = privilege_modifier + "docker build -t seesegment/seesegment:" + str(version_tag) + " " + os.path.join(os.getcwd(), "see_segment")
build_server_command = privilege_modifier + "docker build -t seesegment/seeserver:" + str(version_tag) + " " + os.path.join(os.getcwd(), "see_server")

# Execute the build commands.
os.system(build_segmenter_command)
os.system(build_server_command)

print("Pushing the images to Dockerhub.")

# Create the push commands.
push_segmenter_command = privilege_modifier + "docker push seesegment/seesegment:" + str(version_tag)
push_server_command = privilege_modifier + "docker push seesegment/seeserver:"+ str(version_tag)

# Execute the push commands.
os.system(push_segmenter_command)
os.system(push_server_command)

print("Updating the yaml files to use version:", version_tag)

"""
yaml_file: the yaml file to be updated
location: a substring that can be used to locate the version_tags location
version_tag: the new version tag to replace the old one with.

This could have been done more easily with sed however sed is not present on 
windows machines.
"""
def update_yaml_tag_version(yaml_file, location, version_tag):
    # Read the yaml file
    with open(yaml_file, "r") as yaml:
        contents = yaml.read()

    # Update the version tag
    index = contents.find(location)

    if index == -1:
        print("error could not find version tag in yaml_file")
        print("has the file format recently changed?")
        sys.exit(1)
    else:
        start_index = index + len(location)
        end_index = start_index + len(version_tag)

        contents = contents[:start_index] + str(version_tag) + contents[end_index:]
        print(contents)

    # Write the updated yaml file contents
    with open(yaml_file, "w") as yaml:
        yaml.write(contents)
    
# Get the paths to the yaml files
server_yaml = os.path.join(os.getcwd(), "kube_commands", "server.yaml")
segment_yaml = os.path.join(os.getcwd(), "kube_commands", "segmentation_job.yaml")

# Specify the location of the version tags in the files
server_tag_location = "image: seesegment/seeserver:"
segment_tag_location = "image: seesegment/seesegment:"

# Update the version tags
update_yaml_tag_version(server_yaml, server_tag_location, version_tag)
update_yaml_tag_version(segment_yaml, segment_tag_location, version_tag)