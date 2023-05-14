# experiment2.py
# EXPERIMENT 2

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

# Map output values linear accoring to input values of x

def lin_map(x, in_min, in_max, out_min, out_max):
    if in_min == in_max:
        return out_max / 2
    else:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# -----------------------------------------------------------------------------------

# Generate output image

def img_generating(data_vals, path):
    a = int(len(data_vals) ** (1/2))
    b = int(len(data_vals) ** (1/2))
    c = int(len(data_vals[0]))
    d = int(len(data_vals[0][0]))
    img = Image.new('RGB', (a * c, b * d))

    for i in range(a):
        for j in range(b):
            for k in range(c):
                for l in range(d):
                    color = int(data_vals[j + (a * i)][k][l] * 255) # [npatch index][npatch col][npatch row]
                    img.putpixel(((k + (j * c)), l + (i * d)), (color, color, color)) # (x, y, rgb color)

    #img.show()
    img.save(path)

# -----------------------------------------------------------------------------------

# Generate episodic image of radiant-regulated noise pattern

def sample_noise(phase, size, n_frames, path):
    for m in range(n_frames):
        data_out = []
        
        # Quantum circuit
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.ry(math.pi * phase, 0)
        qc.measure_all()

        # Measurements
        result = run_qc(qc, 'sim', 'memory', size ** 2)
        result = np.reshape(result, (size, size)).astype(float)
        data_out.append(result)
        
        # Image assembling
        img_generating(data_out, path)

# -----------------------------------------------------------------------------------
# CALL FUNCTIONS ACCORDING TO ARGUMENTS
# -----------------------------------------------------------------------------------

# Argument parsing from command line
parser = argparse.ArgumentParser(
    description =   '''
                    Use this piece of software to simulate,
                    visulize, and *shift* superposition of
                    a single qubit as noise patterns on a
                    square canvas.
                    ''',
    epilog      =   '''
                    Your created pattern image(s) will
                    be filed in a directory that sits
                    in the same place as this program.
                    ''')

parser.add_argument('--method',
    type        =   str,
    required    =   True,
    choices     =   ['episodic', 'range'],
    help        =   '''
                    Choosing 'episodic' will give you a
                    single image, while 'range' renders
                    a whole array.
                    ''')

parser.add_argument('--phase',
    type        =   float,
    required    =   False,
    help        =   '''
                    Specify the phase that determines
                    the ratio of black and white in the
                    noise pattern.
                    ''')

parser.add_argument('--samples',
    type        =   int,
    required    =   False,
    help        =   '''
                    Choosing the 'range' method will give
                    you a whole array of images with
                    *shifting* ratios visible in the
                    noise patterns. You need to specify
                    the steps that determine the
                    subdivisions inside the range as
                    an integer such as 25 (giving you
                    25 images).
                    ''')

parser.add_argument('--sidelength',
    type        =   int,
    required    =   True,
    help        =   '''
                    Specify the side length of your
                    canvas as an integer such as 4.
                    ''')

args = parser.parse_args()

# Create directory for output images
out_dir = 'experiment2_output'
path = os.path.join(os.getcwd(), out_dir)
try:
    os.mkdir(path)

# Make sure directory does not get overwritten
except FileExistsError:
    pass

# -----------------------------------------------------------------------------------

# Number of frames
n_frames = 1

# Argument 'episodic'
if args.method == 'episodic':
    phase_as_str = str(args.phase).replace('.', 'pt')
    sample_noise(args.phase, args.sidelength, n_frames, f"{path}/{args.method}_{phase_as_str}_{args.sidelength}x{args.sidelength}px.png")

# Argument 'range'
if args.method == 'range':

    # Create directory for range
    path = os.path.join(f"{os.getcwd()}/{out_dir}", f"{args.method}_{args.samples}_samples_{args.sidelength}x{args.sidelength}px")
    try:
        os.mkdir(path)

    # Make sure directory does not get overwritten
    except FileExistsError:
        pass

    # Calculate decimal range
    phases = np.linspace(0, 2.0, num=args.samples, endpoint=True)

    # Perform computation for every phase in range
    for i in range(len(phases)):
        phase_as_str = str('{:.2f}'.format(round(phases[i], 2))).replace('.', 'pt')
        sample_noise(phases[i], args.sidelength, n_frames, f"{path}/{args.method}_{phase_as_str}_{args.sidelength}x{args.sidelength}px.png")