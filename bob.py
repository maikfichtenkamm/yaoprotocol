#!/usr/bin/env python3
import util
import yao
import ot
import helpers
from main import *
import sys


class My_Bob(Bob):

    def __init__(self):
        super().__init__()

    def listen(self, input):
        """Start listening for Alice messages."""
        logging.info("Start listening MyBob")
        inputs = util.bits(input, 4)
        
        inputs = inputs[::-1]

        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                result = self.send_evaluation(entry, inputs)
                return result
        except KeyboardInterrupt:
            logging.info("Stop listening")

    def send_evaluation(self, entry, inputs):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
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
        print("Evaluation ends")
        return result

def main():
    if len(sys.argv) > 1: # read inputs from a textfile
        input = helpers.get_inputs_from_file(path=sys.argv[1], upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    else: # read inputs from a textfile 
        input = helpers.get_inputs(upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    print("The accumulated sum of Bob is ", input, " and is used as input for MPC")
    bob = My_Bob()
    result = bob.listen(input)
    output = helpers.print_correct_result(result)
    print("The common sum of Bob and Alice is: ", output)

if __name__ == '__main__':
    main()  