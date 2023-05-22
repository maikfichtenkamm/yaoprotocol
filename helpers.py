""" Module containing helper functions for a simple Yao protocol
"""


def get_inputs(upper_bound, error_msg):
    """ Extracts the user input from console

    Args:
        upper_bound (int): The restriction of the circuit: for example, the circuit can process just 4 bit numbers
        error_msg (string): error message of incorrect input

    Raises:
        Exception: if user enters a number which is larger than 15

    Returns:
        int: input of the user
    """
    inputs = input("Enter your values (in the form: 0,1,2,3,4,..): ")
    inputs = [int(x) for x in inputs.split(",")]
    final_input = sum(inputs)
    if final_input > upper_bound:
        raise Exception(error_msg)
    return final_input


def get_inputs_from_file(path, upper_bound, error_msg):
    """Extracts the user input from a textfile

    Args:
        path (str): path to the input file
        upper_bound (int): The restriction of the circuit: for example, the circuit can process just 4 bit numbers
        error_msg (str): error message of incorrect input

    Raises:
        Exception: if user enters a number which is larger than 15

    Returns:
        int: input of the user
    """
    with open(path) as file:
        inputs = file.readline()
        final_input = sum(list(map(int, inputs.split(","))))
    if final_input > upper_bound:
        raise Exception(error_msg)
    return final_input


def verify_output(path_alice, path_bob, result):
    """  function to verify whether the output from the Yao protocol is correct. 
        The function is computed non-multiparty way. 
        If computation is true: prints "Successful computation!"
        If computation is false: prints "Incorrect computation!"

    Args:
        path_alice (str): path to input file of Alice
        path_bob (str): path to input file of Bob
        result (int): the result of the Yao protocol   
    """
    input_alice = get_inputs_from_file(
        path=path_alice, upper_bound=15, error_msg="only numbers smaller than 16 are supported! Enter smaller numbers")
    input_bob = get_inputs_from_file(
        path=path_bob, upper_bound=15, error_msg="only numbers smaller than 16 are supported! Enter smaller numbers")
    print("Successful computation!") if ((input_alice + input_bob)
                                         == result) else print("Incorrect computation!")


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


def circuit_2_result(result):
    """ Convert the result of the Yao protocol to integer
        Therefore, first the order of the array is swapped because of the representation of the circuit and its specific output
        
    Args:
        result (dict): result dict after the evaluation of yao protocol

    Returns:
        int: the reversed bit list as int
    """
    output = list(result.values())
    output = output[::-1]
    return bits_to_integer(output)
