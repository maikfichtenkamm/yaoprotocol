#!/usr/bin/env python3
import helpers
import util
import yao
import ot
from main import *
import sys


class My_Alice(Alice):
    """ My_Alice is an adapted version of the ALice class of given Python library "Secure Multi-Party Computation" by Olivier Ruques and Emmanuelle Risson, available at https://github.com/ojroques/garbled-circuit
    In particular, I renamed the print method to alice_mpc_compute and added the print_alice_to_bob method:

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice prints the contents she sends to the evaluator (Bob): the overview of the circuit, the garbled tables and the external values
    Alice receives the result of the computation and prints it.

    Args:
        Alice (YaoGarbler): The Alice class of the Python library Secure Multi-Party Computation with similar functionality
    """    
    

    def start(self, input):
        """ Starts the yao protocol and sends Alice contents to Bob: the overview of the circuit, the garbled tables and the external values

        Args:
            input (int): The input of Alice for the computation read from a file or typed in console

        Returns:
            int: The result of the computation
        """        
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
        """Prints the contents Alice sends to the evaluator (Bob) at the beginning of the yao protocol: the overview of the circuit, the garbled tables and the external values

        Args:
            circuit (_type_): _description_
            input (_type_): _description_
            a_inputs (_type_): _description_
        """ 

        original_stdout = sys.stdout
        with open('alice_to_bob.py', 'w') as f:

        # print input
            f.write(f"Alice input is the accumulated sum {input}!")
        # print the circuit
            f.write("Alice and Bob use the circuit of a 4-bit full adder. The circuit representation is printed in the following. Refer to the documentation for a better overview")
            #f.write(circuit["circuit"])
            # print the send garbled tables
            f.write("Alice sends the following garbled tables to Bob.")
            f.write("The gates are shown in the order in which they are evaluated. In addition, all combinations of the external values of input wires of a gate are transmitted and their encrypted contents.")
            f.write(
                "These are shown in the form: [input_wire_a, e_value_a][input_wire_b, e_value_b]: encrypted content of output")
            # print the garbled tables: 
            garbled_circuit = circuit["garbled_circuit"]
            for gate in garbled_circuit.gates:
                print(f"Gate number {gate.id} of type {gate.type}:")
                for k, v in self.clear_garbled_table.items():
                    print(f"[{gate.input[0]}, {k[0]}] [{gate.input[1]}, {k[1]}]: {v}")
                garbled_gate = yao.GarbledGate(gate, garbled_circuit.keys, garbled_circuit.pbits)
                print("Table REAL", garbled_gate.garbled_table)
                break

            circuit["garbled_circuit"].print_garbled_tables()


            f.write("Also the e values are public and especially the e values of the output are important for evaluation by Bob")
            #f.write("PBITSOUT", circuit["pbits_out"])
            f.write("Finally, Alice sends the keys for all her inputs and the corresponding e values")
            for wire, content in a_inputs.items():
                f.write(
                    f"Alice sends for wire {wire} the key {content[0]} and the e value {content[1]}")
            

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
        result = self.ot.get_result(a_inputs, b_keys)

        # get the output and print it also for Alice
        return helpers.print_correct_result(result)


def main():
    if len(sys.argv) > 1:
        input = helpers.get_inputs_from_file(
            path=sys.argv[1], upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    else:
        input = helpers.get_inputs(
            upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    print(input)
    alice = My_Alice(circuits='4bit-adder.json')
    result = alice.start(input)
    print("The common sum of Bob and Alice is: ", result)
    helpers.verify_output(path_alice='alice_inputs.txt',
                          path_bob='bob_inputs.txt', result=result)


if __name__ == '__main__':
    main()
