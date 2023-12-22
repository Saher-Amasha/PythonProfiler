import os
import re

class MetaAdder:
    def add_metaclass_to_files(self,root_folder):
        # Loop through all files and subfiles in the current folder
        for foldername, subfolders, filenames in os.walk(root_folder):
            for filename in filenames:
                # Check if the file has a .py extension
                if filename.endswith('.py'):
                    file_path = os.path.join(foldername, filename)

                    # Read the content of the file
                    with open(file_path, 'r') as file:
                        content = file.read()

                    # Use regular expression to find and add metaclass to class definitions
                    content_with_metaclass = re.sub(r'class\s+(\w+)\(([^)]*)\)\s*:', r'class \1(\2, metaclass=MyMeta):', content)

                    # Write the modified content back to the file
                    with open(file_path, 'w') as file:
                        file.write(content_with_metaclass)

        print("Metaclass added to all class definitions.")

    def remove_metaclass_from_files(self,root_folder):
        # Loop through all files and subfiles in the current folder
        for foldername, subfolders, filenames in os.walk(root_folder):
            for filename in filenames:
                # Check if the file has a .py extension
                if filename.endswith('.py'):
                    file_path = os.path.join(foldername, filename)

                    # Read the content of the file
                    with open(file_path, 'r') as file:
                        content = file.read()

                    # Use regular expression to remove metaclass from class definitions
                    content_without_metaclass = re.sub(r'class\s+(\w+)\([^)]*,\s*metaclass=MyMeta\)\s*:', r'class \1:', content)

                    # Write the modified content back to the file
                    with open(file_path, 'w') as file:
                        file.write(content_without_metaclass)

        print("Metaclass removed from all class definitions.")

# # Ask the user whether to add or remove the metaclass
# action = input("Do you want to add or remove the metaclass? (Type 'add' or 'remove'): ").lower()

# # Specify the root folder (current directory in this case)
# root_folder = os.getcwd()

# if action == 'add':
#     add_metaclass_to_files(root_folder)
#     input("Metaclass added. Press Enter to continue.")
# elif action == 'remove':
#     remove_metaclass_from_files(root_folder)
#     input("Metaclass removed. Press Enter to continue.")
# else:
#     print("Invalid action. Please type 'add' or 'remove'.")
        


        # Finished
        # def[ ]+class[ ]+(.*)(:) ,     def class \1 (metaclass=MyMeta):
        # def( )+class([ ]+.*?[ ]*)[ ]*([\)]*:)    ,     def class \1 \2,metaclass=MyMeta):

        