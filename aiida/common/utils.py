import os, os.path
import string

from aiida.common.exceptions import ConfigurationError

CONFIG_FNAME = 'config.json'

def backup_config():   
    import shutil
    aiida_dir    = os.path.expanduser("~/.aiida")
    conf_file   = os.path.join(aiida_dir, CONFIG_FNAME)
    if (os.path.isfile(conf_file)):
        shutil.copy(conf_file, conf_file+"_bk")
    
def get_config():
    import json
    
    aiida_dir    = os.path.expanduser("~/.aiida")
    conf_file   = os.path.join(aiida_dir, CONFIG_FNAME)
    try:
        with open(conf_file,"r") as json_file:
            return json.load(json_file)
    except IOError:
        # No configuration file
        raise ConfigurationError("No configuration file found")

def store_config(confs):
    import json
    
    aiida_dir    = os.path.expanduser("~/.aiida")
    conf_file   = os.path.join(aiida_dir, CONFIG_FNAME)
    with open(conf_file,"w") as json_file:
        json.dump(confs, json_file)
   
def load_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'aiida.djsite.settings.settings'

def get_repository_folder():
    """
    Return the top folder of the local repository.
    """
    try:
        from aiida.djsite.settings.settings import LOCAL_REPOSITORY
        if not os.path.isdir(LOCAL_REPOSITORY):
            raise ImportError
    except ImportError:
        raise ConfigurationError(
            "The LOCAL_REPOSITORY variable is not set correctly.")
    return os.path.realpath(LOCAL_REPOSITORY)

def escape_for_bash(str_to_escape):
    """
    This function takes any string and escapes it in a way that
    bash will interpret it as a single string.
    
    Explanation:

    At the end, in the return statement, the string is put within single
    quotes. Therefore, the only thing that I have to escape in bash is the
    single quote character. To do this, I substitute every single
    quote ' with '"'"' which means:
                 12345
    1: exit from the enclosing single quotes
    234: "'" is a single quote character, escaped by double quotes
    5: reopen the single quote to continue the string
    Finally, note that for python I have to enclose the string '"'"'
    within triple quotes to make it work, getting finally: the complicated
    string found below.
    """
    escaped_quotes = str_to_escape.replace("'","""'"'"'""")
    return "'{}'".format(escaped_quotes)

def get_suggestion(provided_string,allowed_strings):
    """
    Given a string and a list of allowed_strings, it returns a string to print
    on screen, with sensible text depending on whether no suggestion is found,
    or one or more than one suggestions are found.

    Args:
        provided_string: the string to compare
        allowed_strings: a list of valid strings
    
    Returns:
        A string to print on output, to suggest to the user a possible valid
        value.
    """
    import difflib
    
    similar_kws = difflib.get_close_matches(provided_string,
                                            allowed_strings)
    if len(similar_kws)==1:
        return "(Maybe you wanted to specify {0}?)".format(similar_kws[0])
    elif len(similar_kws)>1:
        return "(Maybe you wanted to specify one of these: {0}?)".format(
            string.join(similar_kws,', '))
    else:
        return "(No similar keywords found...)"


def validate_list_of_string_tuples(val, tuple_length):
    """
    Check that:
    1. val is a list or tuple
    2. each element of the list:
      a. is a list or tuple
      b. is of length equal to the parameter tuple_length
      c. each of the two elements is a string

    Return if valid, raise ValidationError if invalid
    """
    from aiida.common.exceptions import ValidationError

    err_msg = ("the value must be a list (or tuple) "
               "of length-N list (or tuples), whose elements are strings; "
               "N={}".format(tuple_length))
    if not isinstance(val,(list,tuple)):
        raise ValidationError(err_msg)
    for f in val:
        if (not isinstance(f,(list,tuple)) or
              len(f)!=tuple_length or
              not all(isinstance(s,basestring) for s in f)):
            raise ValidationError(err_msg)

    return True

def conv_to_fortran(val):
    """
    val: the value to be read and converted to a Fortran-friendly string.
    """   
    # Note that bool should come before integer, because a boolean matches also
    # isinstance(...,int)
    if (isinstance(val,bool)):
        if val:
            val_str='.true.'
        else:
            val_str='.false.'
    elif (isinstance(val,int)): 
        val_str = "{:d}".format(val)
    elif (isinstance(val,float)):
        val_str = ("{:18.10e}".format(val)).replace('e','d')
    elif (isinstance(val,basestring)):
        val_str="'{!s}'".format(val)
    else:
        raise ValueError("Invalid value passed, accepts only bools, ints, "
                         "floats and strings")

    return val_str

def get_unique_filename(filename, list_of_filenames):
    """
    Return a unique filename that can be added to the list_of_filenames.
    
    If filename is not in list_of_filenames, it simply returns the filename
    string itself. Otherwise, it appends a integer number to the filename
    (before the extension) until it finds a unique filename.

    Args:
        filename: the filename to add
        list_of_filenames: the list of filenames to which filename
            should be added, without name duplicates
    Returns:
        Either filename or its modification, with a number appended between
        the name and the extension.
    """
    if filename not in list_of_filenames:
        return filename

    basename, ext = os.path.splitext(filename)

    # Not optimized, but for the moment this should be fast enough
    append_int = 1
    while True:
        new_filename = "{:s}-{:d}{:s}".format(basename, append_int, ext)
        if new_filename not in list_of_filenames:
            break
        append_int += 1
    return new_filename

def md5_file(filename, block_size_factor=128):
    """
    Open a file and return its md5sum (hexdigested).

    Args:
        filename: the filename of the file for which we want the md5sum
        block_size_factor: the file is read at chunks of size
            block_size_factor * md5.block_size,
        where md5.block_size is the block_size used internally by the
        hashlib module.

    Returns:
        a string with the hexdigest md5.

    Raises:
        No checks are done on the file, so if it doesn't exists it may
        raise IOError.
    """
    import hashlib
    md5 = hashlib.md5()
    with open(filename,'rb') as f:
        # I read 128 bytes at a time until it returns the empty string b''
        for chunk in iter(
            lambda: f.read(block_size_factor*md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()
