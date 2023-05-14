# experiment1.py
# EXPERIMENT 1

# -----------------------------------------------------------------------------------
# INCLUDE ALL MODULES
# -----------------------------------------------------------------------------------

# Qiskit for Quantum computation
from qiskit import QuantumCircuit, Aer, transpile, execute
from qiskit.providers.aer.noise import NoiseModel, QuantumError, ReadoutError, pauli_error

# PILlow for image generation
from PIL import Image, ImageColor

# Handy math libraries
import numpy as np
import math

# Command line arguments parsing
import argparse

# For saving files in current directory
import os

# -----------------------------------------------------------------------------------
# DEFINE ALL FUNCTIONS
# -----------------------------------------------------------------------------------

# Simulate Quantum computation

def run_qc(circuit, backend, output, n_shots):

    # -------------------------------------------------------------------------------
    
    # Build basic bit-flip error noise model

    # Example error probabilities
    p_reset = 0.03
    p_meas = 0.1
    p_gate1 = 0.05

    # QuantumError objects
    error_reset = pauli_error([('X', p_reset), ('I', 1 - p_reset)])
    error_meas = pauli_error([('X',p_meas), ('I', 1 - p_meas)])
    error_gate1 = pauli_error([('X',p_gate1), ('I', 1 - p_gate1)])
    error_gate2 = error_gate1.tensor(error_gate1)

    # Add errors to noise model
    noise_bit_flip = NoiseModel()
    noise_bit_flip.add_all_qubit_quantum_error(error_reset, "reset")
    noise_bit_flip.add_all_qubit_quantum_error(error_meas, "measure")
    noise_bit_flip.add_all_qubit_quantum_error(error_gate1, ["u1", "u2", "u3"])
    noise_bit_flip.add_all_qubit_quantum_error(error_gate2, ["cx"])
    
    # -------------------------------------------------------------------------------
    
    # Execution and options
    
    # Load simulator (Aer)
    backend_simulate = Aer.get_backend('aer_simulator')
    
    # Execute on Aer
    if (backend == 'sim'):
        run = execute(circuit,
                      backend_simulate,
                      shots = n_shots,
                      memory = True).result()
        if (output == 'count'):
            out = run.get_counts()
        if (output == 'memory'):
            out = run.get_memory()
    
    # Execute on Aer + noise model
    if (backend == 'sim_noise'):
        run = execute(circuit,
                      backend_simulate,
                      noise_model=noise_bit_flip,
                      shots = n_shots,
                      memory = True).result()
        if (output == 'count'):
            out = run.get_counts()
        if (output == 'memory'):
            out = run.get_memory()

    return out

# -----------------------------------------------------------------------------------

# Generate EPISODIC image

def sample_noise_episodic(size, path):
    data_out = []
    
    # Quantum circuit
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()

    # Measurements
    result = run_qc(qc, 'sim', 'memory', size ** 2)
    result = np.reshape(result, (size, size)).astype(float)
    data_out.append(result)
    
    # Image assembling
    a = int(len(data_out) ** (1/2))
    b = int(len(data_out) ** (1/2))
    c = int(len(data_out[0]))
    d = int(len(data_out[0][0]))
    
    img = Image.new('RGB', (a * c, b * d))
    for i in range(a):
        for j in range(b):
            for k in range(c):
                for l in range(d):
                    color = int(data_out[j + (a * i)][k][l] * 255)
                    img.putpixel(((k + (j * c)), l + (i * d)), (color, color, color))
            
    #img.show()
    img.save(path)

# -----------------------------------------------------------------------------------

# Generate CONTINUOUS image

def sample_noise_continous(height, length, path):
    data_out = []
    
    # Quantum circuit
    for i in range(length):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        # Measurements
        result = run_qc(qc, 'sim', 'memory', height)
        data_out.append(result)
    
    # Image assembling
    img = Image.new('RGB', (length, height))
    for j in range(height):
        for k in range(length):
            color = int(int(data_out[k][j]) * 255)
            img.putpixel((k, j), (color, color, color))
    
    #img.show()
    img.save(path)

# -----------------------------------------------------------------------------------
# CALL FUNCTIONS ACCORDING TO ARGUMENTS
# -----------------------------------------------------------------------------------

# Argument parsing from command line
parser = argparse.ArgumentParser(
    description =   '''
                    Use this piece of software to
                    simulate and visualize superposition
                    of a single qubit as noise patterns
                    on a canvas of variable size.
                    ''',
    epilog      =   '''
                    Your created pattern image will
                    be filed in a directory that sits
                    in the same place as this program.
                    ''')

parser.add_argument('--method',
    type        =   str,
    required    =   True,
    choices     =   ['episodic', 'continuous'],
    help        =   '''
                    Specify if either your canvas
                    will be 'episodic' or 'continous'.
                    ''')

parser.add_argument('--sidelength',
    type        =   int,
    required    =   True,
    help        =   '''
                    Specify the side length of your
                    canvas as an integer such as 4.
                    ''')

parser.add_argument('--width',
    type        =   int,
    required    =   False,
    help        =   '''
                    If you chose the 'continuous' method,
                    you need to specify the width as
                    an integer.
                    ''')

args = parser.parse_args()

# Create directory for output images
path = os.path.join(os.getcwd(), 'experiment1_output')
try:
    os.mkdir(path)

# Make sure directory does not get overwritten
except FileExistsError:
    pass

# -----------------------------------------------------------------------------------
    
# Argument 'episodic'
if args.method == 'episodic':
    sample_noise_episodic(args.sidelength, f"{path}/{args.method}_{args.sidelength}x{args.sidelength}px.png")

# Argument 'continuous'
if args.method == 'continuous':
    if args.width == None:
        sample_noise_continous(args.sidelength, args.sidelength, f"{path}/{args.method}_{args.sidelength}x{args.sidelength}px.png")
    if args.width != None:
        sample_noise_continous(args.sidelength, args.width, f"{path}/{args.method}_{args.sidelength}x{args.width}px.png")