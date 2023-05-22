""" Module which is copied from the Python library "Secure Multi-Party Computation" by Olivier Ruques and Emmanuelle Risson,
     available at https://github.com/ojroques/garbled-circuit.
"""
import hashlib
import logging
import pickle
import util
import yao


class ObliviousTransfer:
    def __init__(self, socket, enabled=True):
        self.socket = socket
        self.enabled = enabled

    def get_result(self, a_inputs, b_keys):
        """Send Alice's inputs and retrieve Bob's result of evaluation.

        Args:
            a_inputs: A dict mapping Alice's wires to (key, encr_bit) inputs.
            b_keys: A dict mapping each Bob's wire to a pair (key, encr_bit).

        Returns:
            The result of the yao circuit evaluation.
        """
        print("Sending inputs to Bob")
        self.socket.send(a_inputs)

        for _ in range(len(b_keys)):
            w = self.socket.receive()  # receive gate ID where to perform OT
            print(f"Received gate ID {w} where to perform OT")

            if self.enabled:  # perform oblivious transfer
                pair = (pickle.dumps(b_keys[w][0]), pickle.dumps(b_keys[w][1]))
                self.ot_garbler(pair)
            else:
                to_send = (b_keys[w][0], b_keys[w][1])
                self.socket.send(to_send)
        result =  self.socket.receive()
        #bob_input = self.socket.receive()
        
        return result

    def send_result(self, circuit, g_tables, pbits_out, b_inputs):
        """Evaluate circuit and send the result to Alice.

        Args:
            circuit: A dict containing circuit spec.
            g_tables: Garbled tables of yao circuit.
            pbits_out: p-bits of outputs.
            b_inputs: A dict mapping Bob's wires to (clear) input bits.
        """
        # map from Alice's wires to (key, encr_bit) inputs
        a_inputs = self.socket.receive()
        # map from Bob's wires to (key, encr_bit) inputs
        b_inputs_encr = {}

        print("Received Alice's inputs")

        for w, b_input in b_inputs.items():
            print(f"Sending gate ID {w} where to perform OT")
            self.socket.send(w)

            if self.enabled:
                b_inputs_encr[w] = pickle.loads(self.ot_evaluator(b_input))
            else:
                pair = self.socket.receive()
                print(f"Received key pair, key {b_input} selected")
                b_inputs_encr[w] = pair[b_input]
        result = yao.evaluate(circuit, g_tables, pbits_out, a_inputs,
                              b_inputs_encr)
        
        print("Sending circuit evaluation")
        self.socket.send(result)
        #self.socket.send(b_inputs)
        return result

    def ot_garbler(self, msgs):
        """Oblivious transfer, Alice's side.

        Args:
            msgs: A pair (msg1, msg2) to suggest to Bob.
        """
        print("OT protocol started")
        G = util.PrimeGroup()
        self.socket.send_wait(G)

        # OT protocol based on Nigel Smart’s "Cryptography Made Simple"
        c = G.gen_pow(G.rand_int())
        h0 = self.socket.send_wait(c)
        h1 = G.mul(c, G.inv(h0))
        k = G.rand_int()
        c1 = G.gen_pow(k)
        e0 = util.xor_bytes(msgs[0], self.ot_hash(G.pow(h0, k), len(msgs[0])))
        e1 = util.xor_bytes(msgs[1], self.ot_hash(G.pow(h1, k), len(msgs[1])))

        self.socket.send((c1, e0, e1))
        print("OT protocol ended")

    def ot_evaluator(self, b):
        """Oblivious transfer, Bob's side.

        Args:
            b: Bob's input bit used to select one of Alice's messages.

        Returns:
            The message selected by Bob.
        """
        print("OT protocol started")
        G = self.socket.receive()
        self.socket.send(True)

        # OT protocol based on Nigel Smart’s "Cryptography Made Simple"
        c = self.socket.receive()
        x = G.rand_int()
        x_pow = G.gen_pow(x)
        h = (x_pow, G.mul(c, G.inv(x_pow)))
        c1, e0, e1 = self.socket.send_wait(h[b])
        e = (e0, e1)
        ot_hash = self.ot_hash(G.pow(c1, x), len(e[b]))
        mb = util.xor_bytes(e[b], ot_hash)

        print("got correct key OT protocol ended")
        return mb

    @staticmethod
    def ot_hash(pub_key, msg_length):
        """Hash function for OT keys."""
        key_length = (pub_key.bit_length() + 7) // 8  # key length in bytes
        bytes = pub_key.to_bytes(key_length, byteorder="big")
        return hashlib.shake_256(bytes).digest(msg_length)
