import subprocess
import json
import os
import glob
import re
import argparse
import sys
from pathlib import Path
from tabulate import tabulate

# Define a custom argument type for a list of strings
def list_of_strings(arg:str) -> list:
    '''Return a list of the words of the string
    '''
    return arg.split(',')

def Filter(data:list, keyword:str):
    """
    Filter a list of nested lists to include only sublists containing the specified keyword.

    Parameters:
    - data (list): A list of nested lists to be filtered.
    - keyword (str): The keyword to search for within the nested sublists.

    Returns:
    - filtered_data (list): A new list containing only the sublists that contain the keyword.

    Example:
    >>> data = [['openmpi/4.1.6', 'openmpi/1.0.0'], ['matlab/2022', 'matlab/2023'], ['afni/1.0', 'afni/2.0']]
    >>> keyword = 'mpi'
    >>> filtered_data = Filter(data, keyword)
    >>> print(filtered_data)
    [['openmpi/4.1.6', 'openmpi/1.0.0']]
    """
    return list(filter(lambda x: any(keyword in item for sublist in x for item in sublist), data))

def list_pkgs_tabulate(dict:dict, collections:list) -> None:
    """
    Print a tabulated representation of package data using the tabulate library.

    Parameters:
    - data_dict (dict): A dictionary containing package data to be tabulated.
    - headers (list): A list of column headers for the tabulated data.

    This function takes a dictionary of package data and a list of headers,
    and it uses the 'tabulate' library to format and print the data in a
    tabular form.

    Example:
    >>> package_data = {
    ...     "Package": ["pkg1", "pkg2", "pkg3"],
    ...     "Dependency": ["1.0", "2.0", "1.5"],
    ... }
    >>> column_headers = ["Package", "Dependency"]
    >>> list_pkgs_tabulate(package_data, column_headers)
    Package    Dependency  
    ---------  --------- 
    pkg1       1.0        
    pkg2       2.0        
    pkg3       1.5        
    """
    print(tabulate(dict, collections, tablefmt="simple"))

def gather_collections(directory:str) -> list:
    """
    Get a list of collection names present in the specified directory.

    This function searches for subdirectories within the given 'directory' and
    returns a list of collection names found, excluding the '.git' directory.

    Parameters:
    - directory (str): The path to the directory where collections are located.

    Returns:
    - collection_names (list): A list of collection names (subdirectory names).

    Example:
    >>> directory_path = '/path/to/collections'
    >>> collections = gather_collections(directory_path)
    >>> print(collections)
    ['collection1', 'collection2', 'collection3']

    Note:
    - If an error occurs during the directory listing process, such as a permission
      issue or the 'directory' not existing, an OSError is raised, and the function
      returns None.
    """
    try:
        collection_names = [name for name in os.listdir(directory) 
            if os.path.isdir(os.path.join(directory, name)) and name != ".git"]
        return collection_names

    except OSError as e:
        print(f"Error: {e}")
        return None

def get_module_dependency(path:str, pkg_name:str, pattern:str='*.lua') -> list:
    """
    Read each module file in the specified directory and gather dependency information.

    This function searches for module files with the given 'pattern' (default '*.lua')
    in the specified 'path' and analyzes them to find dependencies using a regular
    expression. It then returns a list of lists, where each inner list contains
    information about a module's dependencies.

    Parameters:
    - path (str): The path to the directory containing module files.
    - pkg_name (str): The name of the package to which the modules belong.
    - pattern (str, optional): The file pattern to match for module files (default '*.lua').

    Returns:
    - output (list): A list of lists, where each inner list contains the following:
      - Module version (e.g., "pkg_name/version")
      - Comma-separated list of module dependencies.

    Example:
    >>> directory_path = '/path/to/modules'
    >>> package_name = 'my_package'
    >>> module_dependencies = get_module_dependency(directory_path, package_name)
    >>> print(module_dependencies)
    [['my_package/module1', 'dependency1, dependency2'],
     ['my_package/module2', ''],
     ...]

    Note:
    - If a file specified by 'pattern' does not exist, a message is printed, but the
      function continues processing other files.
    - Any unexpected exceptions during file reading or parsing are caught and printed.
    """
    # Instantiate empty list
    output = list()

    for file in glob.glob(os.path.join(path,pattern)):
        try:
            with open(file, 'r') as lua_file:

                lua_contents = lua_file.read()
                pkg_ver = os.path.splitext(file)
                pkg_ver = Path(file).stem

                # Use a regular expression to find "depends_on" and capture the string inside parentheses
                matches = re.findall(r'^\s*depends_on\("([^"]+)"\)', lua_contents, re.MULTILINE)
 
                if len(matches) > 0:
                    output.append([f"{pkg_name}/{pkg_ver}", ", ".join(matches)])

                else:
                    output.append([f"{pkg_name}/{pkg_ver}",""])

        # Error handling
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")


    return output

def get_module_names(directory:str, collection:str) -> list:
    """
    Get a list of module names inside a specified collection directory.

    This function searches for subdirectories within the specified 'collection' directory
    inside the given 'directory' and returns a list of module names found.

    Parameters:
    - directory (str): The path to the root directory containing collections.
    - collection (str): The name of the collection directory for which to retrieve module names.

    Returns:
    - module_list (list): A list of module names (subdirectory names) found within the collection.

    Example:
    >>> root_directory = '/path/to/collections'
    >>> collection_name = 'my_collection'
    >>> modules = get_module_names(root_directory, collection_name)
    >>> print(modules)
    ['module1', 'module2', 'module3']

    Note:
    - If an error occurs during the directory listing process, such as a permission issue
      or the specified 'directory' or 'collection' not existing, an OSError is raised,
      and the function returns None.
    """
    try:
        module_list = [module for module in os.listdir(os.path.join(directory, collection)) 
                    if os.path.isdir(os.path.join(directory, collection))]

        return module_list
        
    # Error handling
    except OSError as e:
        print(f"Error: {e}")
        return None   

def stacked_get_module_names(directory:str, collection:str) -> list:
    """
    Get a list of module names inside a specified collection directory.

    This function searches for subdirectories within the specified 'collection' directory
    inside the given 'directory' and returns a list of module names found.

    Parameters:
    - directory (str): The path to the root directory containing collections.
    - collection (str): The name of the collection directory for which to retrieve module names.

    Returns:
    - module_list (list): A list of module names (subdirectory names) found within the collection.

    Example:
    >>> root_directory = '/path/to/collections'
    >>> collection_name = 'my_collection'
    >>> modules = get_module_names(root_directory, collection_name)
    >>> print(modules)
    ['module1', 'module2', 'module3']

    Note:
    - If an error occurs during the directory listing process, such as a permission issue
      or the specified 'directory' or 'collection' not existing, an OSError is raised,
      and the function returns None.
    """

    # Instantiate empty list
    output = list()

    try:
        for root, dirs, files in os.walk(os.path.join(directory, collection)):
        # Print the current directory being scanned
            output.append(root)
        return output
    
    # Error handling
    except OSError as e:
        print(f"Error: {e}")

        return None    

def stacked_module_path_cleanup(modules:list, collection:str) -> list:
    """
    Filter module paths based on the specified collection type.

    This function takes a list of module paths and a 'collection' type as input and
    filters the module paths based on the collection type. It returns a filtered list
    of module paths that match the expected structure for the given collection type.

    Parameters:
    - modules (list): A list of module paths to be filtered.
    - collection (str): The collection type for which the filtering is performed.
      Expected values are "MPI," "Python," or "Compilers."

    Returns:
    - filtered_modules (list): A filtered list of module paths that match the expected
      structure for the specified collection type.

    Example:
    >>> module_paths = [
    ...     '/path/to/collections/Python/module1',
    ...     '/path/to/collections/Python/module2',
    ...     '/path/to/collections/MPI/module3',
    ...     '/path/to/collections/Compilers/module4',
    ... ]
    >>> collection_type = "Python"
    >>> filtered_paths = stacked_module_path_cleanup(module_paths, collection_type)
    >>> print(filtered_paths)
    ['/path/to/collections/Python/module1', '/path/to/collections/Python/module2']

    Note:
    - The 'modules' parameter is expected to be a list of strings representing module paths.
    - The function filters module paths based on the number of directory components in the path,
      which is determined by the 'collection' type.
    - If the 'collection' type is not one of the expected values ("MPI," "Python," or "Compilers"),
      the function will return an empty list.
    """
    if collection == "MPI":
        return [mod for mod in modules if len(mod.split('/')) == 7]

    elif collection == "Python":
        return [mod for mod in modules if len(mod.split('/')) == 6]

    elif collection == "Compilers":
        return [mod for mod in modules if len(mod.split('/')) == 7]
    
    else:
        return sys.exit(1)

def stacked_case(directory:str, collection:str, filter:bool=False, keyword:str='') -> None:
    """
    Analyze and print module information for different collection types.

    This function analyzes modules within the specified 'collection' and prints their
    dependency information in a tabulated format. The behavior of the function depends
    on the 'collection' type, and optionally, it can filter the output based on a 'keyword'.

    Parameters:
    - directory (str): The root directory containing collections and modules.
    - collection (str): The type of collection to analyze. Expected values are "MPI,"
      "Python," or "Compilers."
    - filter (bool, optional): Whether to filter the output based on a 'keyword' (default False).
    - keyword (str, optional): The keyword used for filtering the output (default '').

    Returns:
    - None: The function prints the analyzed information but does not return a value.

    Example:
    >>> root_directory = '/path/to/collections'
    >>> collection_type = "Python"
    >>> stacked_case(root_directory, collection_type, filter=True, keyword="dependency1")

    Note:
    - The 'directory' parameter should point to the root directory containing the collections.
    - The 'collection' parameter determines the type of collection to analyze.
    - The function uses various helper functions to gather module information and dependencies.
    - If 'filter' is True, the output is filtered based on the 'keyword.'
    - The function prints the analyzed information in a tabulated format.
    """
    # Instantiate empty dictionary and list
    dict = {}
    output = []

    _x = stacked_get_module_names(directory, collection)

    if len(_x) > 0:
        dict[collection] = stacked_module_path_cleanup(_x, collection)
        
        if collection == "MPI":
            for module in dict[collection]:

                # Full path string to module
                path = os.path.join(directory,collection,module)
                
                # specifics
                _pkg_name = module.split('/')
                _mpi = _pkg_name[4]
                _compiler = _pkg_name[5]
                _y = get_module_dependency(path=path, pkg_name=_pkg_name[6])

                if len(_y) > 0:

                    # required because list returned from get_module_dependency is a nested list of kind [[[]]
                    for idx,item in enumerate(_y):
                        _y[idx] = [_mpi, _compiler] + item
                    output.append(_y)

                else:
                    continue

            # for filtering list displayed
            if filter:
                    output = Filter(output, keyword)

            if len(output) > 0:
                print("\n")   
                print(tabulate([x for item in output for x in item]
                    ,["MPI Ver.","Compiler",f"{collection} Packages", "Dependency"], 
                    tablefmt="simple"))
            else:
                    print(f"0 softwares found for {collection}")

        elif collection == "Python":
            for module in dict[collection]:

                path = os.path.join(directory,collection,module)

                _pkg_name = module.split('/')
                _python_ver = '/'.join(_pkg_name[3:5:1])
                _y = get_module_dependency(path=path, pkg_name=_pkg_name[5])

                if len(_y) > 0:
                    for idx,item in enumerate(_y):
                        _y[idx] = [_python_ver] + item
                    output.append(_y)

                else:
                    continue

            if filter:
                    output = Filter(output, keyword)

            if len(output) > 0:
                print("\n")   
                print(tabulate([x for item in output for x in item]
                    ,["Python Version", f"{collection} Packages", "Dependency"], 
                    tablefmt="simple"))
            else:
                    print(f"0 softwares found for {collection}")
                
        elif collection == "Compilers":
            for module in dict[collection]:

                path = os.path.join(directory,collection,module)

                _pkg_name = module.split('/')
                _compiler_ver = '/'.join(_pkg_name[4:6:1])
                _y = get_module_dependency(path=path, pkg_name=_pkg_name[6])

                if len(_y) > 0:
                    for idx,item in enumerate(_y):
                        _y[idx] = [_compiler_ver] + item
                    output.append(_y)

                else:
                    continue

            if filter:
                    output = Filter(output, keyword)
            
            if len(output) > 0:
                print("\n")
                print(tabulate([x for item in output for x in item]
                    ,["Compiler Version", f"{collection} Packages", "Dependency"], 
                    tablefmt="simple"))
            else:
                    print(f"0 softwares found for {collection}")

def main():
    """
    Main function for the Software Dependency Check program.

    This function serves as the entry point for the program. It parses command-line arguments
    to customize the behavior of the program, including the root directory for collections,
    filtering based on keywords, and selecting specific collections for analysis.

    The program can analyze various types of collections and their module dependencies, and it
    can optionally filter the results based on a specified keyword.

    Command-Line Arguments:
    - '-o', '--output': Output file name (not currently used).
    - '-d', '--dir': Root directory containing collections and modules (default: '/sw/modules').
    - '-c', '--collection': List of specific collections to analyze (default: all available).
    - '-t', '--tree': Display module dependencies in a tree-like structure (not currently used).
    - '-f', '--filter': Filter the results based on a specified keyword (default: '').

    Returns:
    - None: The function processes command-line arguments, analyzes collections, and prints results.

    Example Usage:
    $ python main.py -d /path/to/collections -c Python -f dependency1

    Note:
    - The program supports the analysis of various collection types, such as "Python," "MPI,"
      and "Compilers," and can display module dependencies accordingly.
    - It can also filter the results to include only modules with specific dependencies using
      the '-f' or '--filter' option.
    """

    # Define command-line arguments and their default values
    parser = argparse.ArgumentParser(description='Software Dependency Check')
    parser.add_argument('-o', '--output', type=str, default='')
    parser.add_argument('-d', '--dir', type=str, default='/sw/modules')
    parser.add_argument('-c', '--collection', type=list_of_strings)
    parser.add_argument('-t', '--tree', type=str, default=False)
    parser.add_argument('-f', '--filter', type=str, default='')
    args = parser.parse_args()

    # Extract values from command-line arguments
    directory = args.dir
    tree = args.tree
    keyword = args.filter
    collections = gather_collections(directory)

    # Remove any bad eggs.
    collections = [col for col in collections if col != "Collections"]

    # Check if a keyword filter is provided
    if len(keyword) > 0:
        filter = True
    else:
        filter = False

    if args.collection is not None:
        flag = 0

        # Check if provided collections are valid
        if all(x in collections for x in args.collection):
            flag = 1
        else:
            flag = 0

        if flag == 1:
            collections = args.collection
        else:
            print("Invalid Collection Name")
            sys.exit(1)

    # Initialize an empty dictionary to store package information
    dict = {}

    for collection in collections:
        if collection not in ["Python", "MPI", "Compilers"]: # The special stacked cases
            # Get a list of all package names inside a collection
            _x = get_module_names(directory, collection)
            if len(_x) > 0:
                dict[collection] = _x
                output = []
                for module in dict[collection]:

                    path = os.path.join(directory, collection, module)

                    _y = get_module_dependency(path=path, pkg_name=module)
                    if _y is not None:
                        output.append(_y)
                    else:
                        continue

                if filter:
                    output = Filter(output, keyword)

                if len(output) > 0:
                    print("\n")
                    print(tabulate([x for item in output for x in item],
                                [f"{collection} Packages", "Dependency"],
                                tablefmt="simple"))
                else:
                    print(f"0 softwares found for {collection}")
        else:
            # Handle special collections (Python, MPI, Compilers)
            if filter:
                stacked_case(directory, collection, filter=filter, keyword=keyword)
            else:
                stacked_case(directory, collection)

if __name__ == "__main__":
   main()
    
