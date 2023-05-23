# Secure Multi-Party Computation with the Yao protocol
## General
The goal of the project was to implement the Yao protocol between the two parties Alice (Garbler) and Bob (Evaluator). The implementation of the Github repository “Secure Multi-Party Computation” was used (Roques und Risson 2020)

## Circuit
I implemented a circuit to compute the function of the sum of a set of values. The requirement for the circuit was to deal with at least 4-bit numbers as input. The scripts Bob.py and Alice.py accept as input up to the highest 4-bit number 1111_2  (15_2). The circuit outputs 5-bit numbers. 
The 4-bit adder is constructed for the binary input as follows. Figure 1 visualizes a half-adder, which can be used to add the least significant bits since there is no carry input for them. 
![image](https://github.com/maikfichtenkamm/yaoprotocol/assets/62957774/0993a18c-a39f-4b7c-8b12-7cf976d24411)
Figure 1: Half adder (Saini 2022) 
Figure 2 depicts a full adder used to add the remaining binary numbers and their potential carry inputs.
 
Figure 2: Full adder (Saini 2022)
This results in the following process shown by figure 3: first a half adder is used for the inputs A1 and B1, then three full adders can be used for the remaining inputs.
 
Figure 3: A 4-bit adder
For instance, assume that Alice’s input is 4_10 und Bob’s 5_10. 4_10 is as binary 4-bit number 0100_2 and 5_10 0101_2. For the summation, the individual bits are encoded in the following way:
A4	A3	A2	A1
0	1	0	0
Figure 4: Mapping Alice's input to wires
B4	B3	B2	B1
0	1	0	1
Figure 5: Mapping Bob's input to variables
Since the summation goes from less to the most significant bits, the representation and the flow of figure 3 are reversed. In the JSON format of the circuit, the bits can also be mapped to the wires.
A4	A3	A2	A1
2	12	22	32
Figure 6: Mapping Alice’s inputs to wires
B4	B3	B2	B1
3	13	23	33
Figure 7: Mapping Bob's input to wires
Thus, a 2 as the last digit represents an input from Alice, a 3 an input from Bob, a 1 a carry input bit, and a 5 an output. This representation is aligned to the JSON format of the given Python library (Roques und Risson 2020).

## Functionalities
From the given GitHub repository (Roques und Risson 2020), I reused the modules main.py, ot.py, util.py, and yao.py. In contrast to the library, I have separated the functionality of the creator (Alice) and evaluator (Bob) into the Python scripts alice.py and bob.py. In the following, I will summarize the functions of the implemented modules. 
•	alice.py: implements the garbler (Alice) side of the Yao protocol.
o	My_Alice(): main class for the garbler.
	start(): starts the Yao protocol and send the circuit, garbled tables, external values.
	print_alice_to_bob(): prints the contents Alice sends to Bob at the beginning of the Yao protocol in the file alice_to_bob.txt.
	alice_mpc_compute(): sends the inputs of Alice to Bob, to call the function get_result() of the ot.py module (which contains the garbler OT), and to get the result of the Yao circuit evaluation.
o	main(): gets the inputs of Alice, initializes My_Alice() and calls the verify_output() function.
•	alice_inputs.txt: specifies the inputs of Alice.
•	alice_to_bob.txt: storing the contents Alice sends to Bob at the beginning of the Yao protocol before the evaluation.
•	bob.py: implements the evaluator (Bob) side of the Yao protocol.
o	My_Bob(): main class for the evaluator.
	listen(): listens for the contents of Alice at the beginning of the Yao protocol and then calls bob_mpc_compute().
	bob_mpc_compute(): calls the function get_result() of the ot.py module (which contains the evaluator OT and evaluates the Yao circuit), and gets the result of the Yao circuit evaluation.
o	main(): gets inputs of Bob, initializes My_Bob() and calls the function verify_output().
•	bob_inputs.txt: specifies the inputs of Bob.
•	helpers.py: containing helper functions.
o	get_inputs(): extracts user input from console.
o	get_inputs_from_file(): extracts the user input from a textfile.
o	verify_output(): verifies the output of the MPC in a non-multiparty way.
o	bits_to_integer(): converts bits in a list to an integer.
•	4bit-adder.json: the circuit in JSON format.

## Installation
The project depends on the packages ZeroMQ, Fernet and SymPy. Install all dependencies with:
```pip3 install --user pyzmq cryptography sympy```

## Usage
The participants Alice and Bob can provide input via the console or a specified text file. The inputs can be inserted in the corresponding input files alice_inputs.txt and bob_inputs.txt. New input files can also be specified, but the numbers should be in the format: 2, 3, 6, …
To start the script, open two terminals and run in the first for the evaluator
•	for input by file: ```./bob.py <path/to/textfileOfBob>```
•	for input via terminal: ```./bob.py ```
and in the second for the garbler:
•	for input by file: ```./alice.py <path/to/textfileOfAlice>```
•	for input via terminal: ```./alice.py```
Then, The communication of the OT, the result of the evaluated circuit and the correctness of the computation is printed in both consoles. It should be noted that error messages may occur due to incorrect input and input as textfile should be prioritized since the result can then be verified in a non-multiparty way. The contents Alice sends to Bob will be printed into the file alice_to_bob.txt.

## Communication
### Alice to Bob
![image](https://github.com/maikfichtenkamm/yaoprotocol/assets/62957774/8725b692-10eb-4c23-a734-e30e3f00be16)
### Bob to Alice
![image](https://github.com/maikfichtenkamm/yaoprotocol/assets/62957774/c13320bc-b766-4024-83f5-fb3725cdf9bb)

## References

Roques, Olivier; Risson, Emmanuelle (2020): Secure Multi-Party Computation. A two-party secure function evaluation using Yao's garbled circuit protocol. Version v2.0. Online verfügbar unter https://github.com/ojroques/garbled-circuit.
Saini, Manish (2022): Difference between Half Adder and Full Adder. Hg. v. tutorialspoint. Online verfügbar unter https://www.tutorialspoint.com/difference-between-half-adder-and-full-adder.


