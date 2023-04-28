#!/usr/bin/env python3
import helpers
import util
import yao
import ot
from main import *
import sys

class My_Alice(Alice):

    def __init__(self, circuits, oblivious_transfer=True):
        super().__init__(circuits, oblivious_transfer)

    def start(self, input):
        """Start Yao protocol."""
        for circuit in self.circuits:
            to_send = {
                "circuit": circuit["circuit"],
                "garbled_tables": circuit["garbled_tables"],
                "pbits_out": circuit["pbits_out"],
            }
            
            logging.debug(f"Sending {circuit['circuit']['id']}")
            self.socket.send_wait(to_send)
            return self.alice_mpc_compute(circuit, input)
        
    def print_alice_to_bob(self, circuit, input, a_inputs):
        # print input
        print("Alice input is the accumulated sum ", input, " !")
        # print the circuit
        print("Alice and Bob use the circuit of a 4-bit full adder. The circuit representation is printed in the following. Refer to the documentation for a better overview")
        print(circuit["circuit"])
        # print the send garbled tables
        print("Alice sends the following garbled tables to Bob.")
        print("The gates are shown in the order in which they are evaluated. In addition, all combinations of the external values of input wires of a gate are transmitted and their encrypted contents.")
        print("These are shown in the form: [input_wire_a, e_value_a][input_wire_b, e_value_b]: encrypted content of output")
        circuit["garbled_circuit"].print_garbled_tables()
        print("Also the e values are public and especially the e values of the output are important for evaluation by Bob")
        print("PBITSOUT", circuit["pbits_out"])
        print("Finally, Alice sends the keys for all her inputs and the corresponding e values")
        for wire, content in a_inputs.items():
            print(f"Alice sends for wire {wire} the key {content[0]} and the e value {content[1]}")

    def alice_mpc_compute(self, entry, input):
        """ Renamed Print to alice mpc compute
        print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        inputs = util.bits(input, 5)
        inputs = inputs[::-1]
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }

        bits_a = inputs
        # Map Alice's wires to (key, encr_bit)
        for i in range(len(a_wires)):
            a_inputs[a_wires[i]] = (keys[a_wires[i]][bits_a[i]],
                                    pbits[a_wires[i]] ^ bits_a[i])
        # print alice to bob
        self.print_alice_to_bob(entry, input, a_inputs)
        # Send Alice's encrypted inputs and keys
        output = self.ot.get_result(a_inputs, b_keys)
        result, input_bob = output
        input_bob = helpers.print_correct_result(input_bob)
       
        # get the output and print it also for Alice
        return helpers.print_correct_result(result), input_bob
    
def main():
    input = helpers.get_inputs(upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    alice = My_Alice(circuits='4bit-adder.json')
    result, input_bob = alice.start(input)
    # TODO result, bob_input = alice.start(input)
    # TODO result, bob_input = encrypt()
    print("The common sum of Bob and Alice is: ", result)
    verfiy_output(input, input_bob, result)

def verfiy_output(alice_input, bob_input, output):
    print("Successful computation") if ((alice_input + bob_input) == output) else print("Incorrect result!")

if __name__ == '__main__':
    main()  