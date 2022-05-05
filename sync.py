import hashlib, os, shutil
from pathlib import Path


BLOCKSIZE = 65536 

#This is done in order to sync the file from source to destination. It uses hash functions to inspect the content of the files.

#Hash function with SHA1
def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)

    return hasher.hexdigest()


#Note: Path's URI depends on the OS. Check it before running it.
def sync(source, dest):

    #imperative steps such as gather inputs, call our logic, apply outputs:
    #Gather inputs
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    
    #Call logic
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    #Apply outputs
    for action, *paths in actions:
        if action == 'copy':
            shutil.copyfile(*paths)

        if action == 'move':
            shutil.move(*paths)

#Building up the dictionary of paths and hashes
def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    
    return hashes

#Given the folders which action must be taken
def determine_actions(src_hashes, dst_hashes, src_folder, dst_folder):
    for sha, filename in src_hashes.items():
        if sha not in dst_hashes:
            sourcepath = Path(src_folder) / filename
            destpath = Path(dst_folder) / filename

            yield 'copy', sourcepath, destpath
        
        elif dst_hashes[sha] != filename:
            oldestpath = Path(dst_folder) / dst_hashes[sha]
            newdestpath = Path(dst_folder) / filename
            
            yield 'move', oldestpath, newdestpath

    for sha, filename in dst_hashes.items():
        if sha not in src_hashes:
            
            yield 'delete', dst_folder / filename





    #Before refactoring
    """
    #Build the dictionary of filenames and their hashes as a sourcetree

    source_hashes = {}

    for folder, _, files in os.walk(source):
        for fn in files:
            source_hashes[hash_file(Path(folder) / fn)] = fn

    seen = set()

    #Walk the target and get the names and hashes 
    for folder, _, files in os.walk(dest):
        for fn in files:
            dest_path = Path(folder) / fn
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)

            #Delete the file that is in destination but not in source
            if dest_hash not in source_hashes:
                dest_path.remove()

            #Add the file that is in wrong path 
            elif dest_hash in source_hashes and fn != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])


    #Copy the files that are in the source but not in the target
    for src_hash, fn in source_hashes.items():
        if src_hash not in seen:
            shutil.copy(Path(source) / fn, Path(dest) / fn)


    """
    