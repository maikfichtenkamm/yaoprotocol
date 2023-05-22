#!/usr/bin/env python3
""" Python Script for the garbler (Alice) of the Yao protocol.
    The module is algined to the garbler Alice of the main.py script of the Python library "Secure Multi-Party Computation" 
    by Olivier Ruques and Emmanuelle Risson, available at https://github.com/ojroques/garbled-circuit.
    The Script gets the inputs of Alice, computes the Yao protocol of an 4-bit-adder circuit, prints out the result and verifies its correct computation
"""
import helpers
import util
import yao
import ot
from main import *
import sys


class My_Alice(Alice):
    """ My_Alice is an adapted version of the Alice class of the given Python library "Secure Multi-Party Computation" 
    by Olivier Ruques and Emmanuelle Risson, available at https://github.com/ojroques/garbled-circuit
    In particular, I renamed the print method to alice_mpc_compute and added the print_alice_to_bob method.

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
        """Prints the contents Alice sends to the evaluator (Bob) at the beginning of the yao protocol to the file alice_to_bob.txt: 
            - the overview of the circuit 
            - the garbled tables
            - the external values

        Args:
            circuit (dict): The 4-bit-adder circuit
            input (int): The input of Alice for the computation read from a file or typed in console
            a_inputs (_type_): map from Alice's wires to (key, encr_bit) inputs
        """ 

        original_stdout = sys.stdout
        with open('alice_to_bob.txt', 'w') as f:

        # print input
            f.write(f"Alice input is the accumulated sum {input}!\n")
        # print the circuit
            f.write("Alice and Bob use the circuit of a 4-bit full adder, which Alice sends to Bob. The circuit json representation is printed in the following. Refer to the documentation for a better overview\n")
            f.write(str(circuit["circuit"]))
            # print the send garbled tables
            f.write("\nAlice sends the following garbled tables to Bob.\n")
            f.write("The gates are shown in the order in which they are evaluated. In addition, all combinations of the external values of input wires of a gate are transmitted and their encrypted contents.\n")
            f.write(
                "These are shown in the form: [input_wire_a, e_value_a][input_wire_b, e_value_b]: encrypted content of output\n")
            garbled_circuit = circuit["garbled_circuit"]
            for gate in garbled_circuit.gates:
                f.write(f"Gate number {gate['id']} of type {gate['type']}:\n")

                garbled_gate = yao.GarbledGate(gate, garbled_circuit.keys, garbled_circuit.pbits)
                # print for combination of input wires their ids, external values and encrypted content
                for k, v in garbled_gate.garbled_table.items():
                    f.write(f"[{gate['in'][0]}, {k[0]}] [{gate['in'][1]}, {k[1]}]: {v}\n")
            
            #print the e values
            f.write("Also the e values are public and especially the e values of the output are important for evaluation by Bob\nE-Values for the output wires: ")
            f.write(str(circuit["pbits_out"]))
            # print input of Alice
            f.write("\nFinally, Alice sends the keys for all her inputs and the corresponding e values\n")
            for wire, content in a_inputs.items():
                f.write(
                    f"Alice sends for wire {wire} the key {content[0]} and the e value {content[1]}\n")
            

    def alice_mpc_compute(self, entry, input):
        """ Modified print function of the Python library "Secure Multi-Party Computation"
            Computes the MPC of ALice: Alice sends her inputs to Bob, does the OT between her and Bob and gets the results

        Args:
            entry: A dict representing the circuit to evaluate.
            input: The input of Alice for the computation read from a file or typed in console

        Returns:
            int: The result of the computation
        """
        # tranform int input to bit representation which is algined to the 4-bit adder circuit
        inputs = util.bits(input, 4)
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
        # Send Alice's encrypted inputs and keys and get the result
        result = self.ot.get_result(a_inputs, b_keys)

        # get the int representation of the result
        result = helpers.circuit_2_result(result)
        print("The common sum of Bob and Alice is: ", result)
        return result


def main():
    """Main function of the Script for the Garbler (Alice) of the Yao protocol.
        Gets the input of Alice, starts the MPC of Alice, gets the result and verifies the ouput.
    """ 
    # if a textfile is mentioned as parameter to the Terminal, the input is read from the file 
    if len(sys.argv) > 1:
        input = helpers.get_inputs_from_file(
            path=sys.argv[1], upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    # else the input can be entered in the Terminal
    else:
        input = helpers.get_inputs(
            upper_bound=15, error_msg="only 4bit numbers supported! Enter smaller numbers")
    print("The accumulated sum of Alice is ", input, " and is used as input for MPC")
    # start the MPC
    alice = My_Alice(circuits='4bit-adder.json')
    result = alice.start(input)
    # verify the output
    if len(sys.argv) > 1:
        helpers.verify_output(path_alice='alice_inputs.txt',
                          path_bob='bob_inputs.txt', result=result)


if __name__ == '__main__':
    main()
