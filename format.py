#!/usr/bin/env python3
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
            return self.print(circuit, input)

    def print(self, entry, input):
        """Print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        inputs = util.bits(input, 5)
        print("Input normale Reihenfolge!",inputs)
        inputs = inputs[::-1]
        print("Input verkehrte Reihenfolge!",inputs)
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
        # Send Alice's encrypted inputs and keys to Bob
        result = self.ot.get_result(a_inputs, b_keys)
        print(result)
        # Format output
        #str_bits_a = ' '.join(bits[:len(a_wires)])
        #str_bits_b = ' '.join(bits[len(a_wires):])
        #str_result = ' '.join([str(result[w]) for w in outputs])
        
        #print(f"  Alice{a_wires} = {str_bits_a} "
        #          f"Bob{b_wires} = {str_bits_b}  "
        #          f"Outputs{outputs} = {str_result}")
        output = list(result.values())
        print("output verkehrte Reihenfolge", output)
        output = output[::-1]
        print("output richtige Reihenfolge", output)
        print(type(output))
        result = util.bits_to_integer(output)
        print("The common sum of Bob and Alices inputs are: ", )
        print()
        return result


class My_Bob(Bob):

    def __init__(self):
        super().__init__()

    def listen(self, input):
        """Start listening for Alice messages."""
        logging.info("Start listening MyBob")
        inputs = util.bits(input, 4)
        
        print("Bob normale reiheoflge inputs", inputs)
        inputs = inputs[::-1]
        print("Bob verkerhte reiheoflge inputs", inputs)

        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                self.send_evaluation(entry, inputs)
                break
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
        self.ot.send_result(circuit, garbled_tables, pbits_out,
                                b_inputs_clear)
        print("Evaluation ends")
        return 

def main():
    loglevel = logging.DEBUG
    logging.getLogger().setLevel(loglevel)
    if sys.argv[1] == 'alice': 
        result, input_alice = alice_to_bob()
    # Your scipt should at least have the following functions to show the output
    if sys.argv[1] == 'bob': 
        input_bob = bob_to_alice()
    # Assume that two parties involved are Alice and Bob
    # This function should print the necessary output from Alice that she wants to send to Bob.
    # This ouput from Alice should be printed in a file e.g. file_name
    # The output format and how to read it should be described in the report document.
    # E.g. if you want to output in table format then describe how to read and interpret the tables. 

    verfiy_output(input_alice, input_bob, result)

def alice_to_bob(): 
    alice_input = input("Enter your values (in the form: 0,1,2,3,4,..): ")
    alice_input = [ int(x) for x in alice_input.split(",") ]
    alice_sum = sum(alice_input)
    print(alice_sum)
    if alice_sum > 15:
        raise Exception("only 4bit numbers supported! Enter smaller numbers")
    circuit_path='4bit-adder.json'
    alice = My_Alice(circuit_path)
    return alice.start(alice_sum), alice_input

def bob_to_alice():
    bob_input = input("Enter your values (in the form: 0,1,2,3,4,..): ")
    bob_input = [ int(x) for x in bob_input.split(",") ]
    bob_sum = sum(bob_input)
    print(bob_sum)
    if bob_sum > 15:
        raise Exception("only 4bit numbers supported! Enter smaller numbers")
    bob = My_Bob()
    bob.listen(bob_sum)
    return bob_input


def verfiy_output(alice_input, bob_input, output):
    print("Successful") if ((alice_input + bob_input) == output) else print("Wrong result!")

if __name__ == '__main__':
    main()  

