#!/usr/bin/env python3
""" Python Script for the evaluator (Bob) of the Yao protocol.
    The module is algined to the evaluator Bob of the main.py script of the Python library "Secure Multi-Party Computation" by Olivier Ruques and Emmanuelle Risson, available at https://github.com/ojroques/garbled-circuit.
    The Script gets the inputs of Bob, computes the Yao protocol of an 4-bit-adder circuit, prints out the result and verifies its correct computation
"""
import util
import yao
import ot
import helpers
from main import *
import sys


class My_Bob(Bob):
    """ My_Bob is an adapted version of the Bob class of the given Python library "Secure Multi-Party Computation" 
    by Olivier Ruques and Emmanuelle Risson, available at https://github.com/ojroques/garbled-circuit

    Bob listens for the Yao circuit, garbled tables and inputs of Alice, computes the Yao protocol and sends the result to Alice
    """ 


    def __init__(self):
        super().__init__()

    def listen(self, input):
        """Start listening for Alice messages. Aligned to the Python library "Secure Multi-Party Computation" 

        Args:
            input (int): The input of Bob for the computation read from a file or typed in console

        Returns:
           int: The result of the computation
        """        
        logging.info("Starts listening Bob")
        # tranform int input to bit representation which is algined to the 4-bit adder circuit
        inputs = util.bits(input, 4)
        inputs = inputs[::-1]
        # get the circuit, garbled tables, inputs and external values from ALice
        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                result = self.send_evaluation(entry, inputs)
                return result
        except KeyboardInterrupt:
            logging.info("Stop listening")

    def bob_mpc_compute(self, entry, inputs):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results. Aligned to the Python library "Secure Multi-Party Computation" 

        Args:
            entry: A dict representing the circuit to evaluate.
            inputs (int): The inputs of Bob as bit representation
        """
        print("Evaluation starts")
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        a_wires = circuit.get("alice", [])  # list of Alice's wires
        b_wires = circuit.get("bob", [])  # list of Bob's wires
        
        bits_b = inputs
        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice
        result = self.ot.send_result(circuit, garbled_tables, pbits_out,
                                b_inputs_clear)
        # get the int representation of the result
        result = helpers.circuit_2_result(result)
        print("Evaluation ends")
        print("The common sum of Bob and Alice is: ", result)
        return result

def main():
    """Main function of the Script for the Evaluator (Bob) of the Yao protocol.
        Gets the input of Bob, starts the MPC of Bob, evaluates the circuit, sends results to Alice and verifies the ouput.
    """ 
    # if a textfile is mentioned as parameter to the Terminal, the input is read from the file 
    if len(sys.argv) > 1:
        input = helpers.get_inputs_from_file(path=sys.argv[1], upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    # else the input can be entered in the Terminal
    else: 
        input = helpers.get_inputs(upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    print("The accumulated sum of Bob is ", input, " and is used as input for MPC")
    # start the MPC
    bob = My_Bob()
    result = bob.listen(input)
    # verify the output
    if len(sys.argv) > 1:
        helpers.verify_output(path_alice='alice_inputs.txt',
                          path_bob='bob_inputs.txt', result=result)
        
if __name__ == '__main__':
    main()  
