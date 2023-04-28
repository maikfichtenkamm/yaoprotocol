def get_inputs(upper_bound, error_msg):
    """ Extracts the user input from console

    Args:
        upper_bound (int): THe restriction of the circuit: for example: the circuit can process just 4 bit numbers
        error_msg (string): error message of incorrect input

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """    
    inputs = input("Enter your values (in the form: 0,1,2,3,4,..): ")
    inputs = [ int(x) for x in inputs.split(",") ]
    final_input = sum(inputs)
    if final_input > upper_bound:
        raise Exception(error_msg)
    return final_input

def bits_to_integer(bitlist):
    """Convert bits in a list to an integer using bitshifting from stackoverflow: https://stackoverflow.com/questions/12461361/bits-list-to-integer-in-python

    Args:
        bitlist (array): bits of the output of the circuit as list

    Returns:
        int: the integer value of the bit array
    """    
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out

def print_correct_result(result):
    """ Convert the result to integer
        Therefore, first the order of the array is swapped because of the representation of the circuit and its specific output

    Args:
        result (dict): result dict after the evaluation of yao protocol

    Returns:
        int: the reversed bit list as int
    """    
    output = list(result.values())
    output = output[::-1]
    return bits_to_integer(output)