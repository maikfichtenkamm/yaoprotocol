#!/usr/bin/python3


def main():

    # Your scipt should at least have the following functions to show the output

    # Assume that two parties involved are Alice and Bob

    # This function should print the necessary output from Alice that she wants to send to Bob.
    # This ouput from Alice should be printed in a file e.g. file_name
    # The output format and how to read it should be described in the report document.
    # E.g. if you want to output in table format then describe how to read and interpret the tables. 
    print_alice_to_bob()
        #alice.start
        #

    # Alice and Bob OT
    # This function should print (in a file/console) the OT between Alice and Bob that takes place in Yao's protocol
    alice_bob_OT()
        # just the ot until yao.evaluate
    
    # This function should print the output the function that Bob wants to compute on the combined data
    # For example this could be one of the three functions decribed in the project slide
    bob_mpc_compute(bobs_data_input)
        # then yao.evaluate

    alice_mpc_compute(alices_data_input)

    # This function should vefiry whether the output from bob_mpc_compute is same as the ouput
    # from a function which is computed non-multiparty way
    verfiy_output()
    

    

    # If you decide to deviate from this format then you must document the functionality of your script very well so that different steps
    # can be verified. 
