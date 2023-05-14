# experiment3.py
# EXPERIMENT 3

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

# Retrieving input image data

def img_data(path):

    img = Image.open(path).getdata()
    px_rgb_vals = list(img)
    
    return px_rgb_vals

# -----------------------------------------------------------------------------------

# Output image generating

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

# Serial input and output data processing

def serial_qc_processing(data_in, size_npatch, channel):
    a = int(len(data_in) ** (1/2))
    
    data_out = []
    qb = 1

    for i in range(a ** 2):
        c_to_rad = lin_map(data_in[i][channel], 0, 255, 1.5, 0.5)

        # Quantum circuit
        qc = QuantumCircuit(qb)
        qc.reset(0)
        qc.h(0)
        qc.ry(math.pi * c_to_rad, 0)
        qc.measure_all()
        
        # Measurements
        result = run_qc(qc, 'sim_noise', 'memory', size_npatch ** 2)

        # Output data formatting
        result = np.reshape(result, (size_npatch, size_npatch)).astype(float)
        data_out.append(result)
        
    return data_out

# -----------------------------------------------------------------------------------

# Parallel input and output data processing

def parallel_qc_processing(data_in, size_npatch, channel):
    data_out = []
    qb = len(data_in)

    # Quantum circuit
    qc = QuantumCircuit(qb)
    for i in range(qb):
        c_to_rad = lin_map(data_in[i][channel], 0, 255, 1.5, 0.5)
        qc.reset(i)
        qc.h(i)
        qc.ry(math.pi * c_to_rad, i)
    qc.measure_all()

    # Measurements
    result = run_qc(qc, 'sim_noise', 'memory', size_npatch ** 2)

    # Output data formatting
    for j in range(qb):
        result_form = []
        for k in range(size_npatch ** 2):
            result_form.append(result[k][j]) # ['[0123]']

        result_form = np.reshape(result_form, (size_npatch, size_npatch)).astype(float)
        data_out.append(result_form)

    data_out.reverse()
    
    return data_out

# -----------------------------------------------------------------------------------
# CALL FUNCTIONS ACCORDING TO ARGUMENTS
# -----------------------------------------------------------------------------------


# Argument parsing from command line
parser = argparse.ArgumentParser(
    description =   '''
                    Use this piece of software to process raster
                    images by simulating, visualizing and shifting
                    superposition according to color pixel values
                    of an image instead of defined phases.
                    ''',
    epilog      =   '''
                    Your created noise image will
                    be filed in a directory that sits
                    in the same place as this program.
                    ''')

parser.add_argument('--input',
    type        =   str,
    required    =   True,
    help        =   '''
                    Insert the *absolute* path of your input
                    image. The input image must be *squared*!
                    ''')

parser.add_argument('--resolution',
    type        =   int,
    required    =   False,
    help        =   '''
                    This determines the desity of the noise
                    pattern of each computed pixel.
                    ''')

parser.add_argument('--channel',
    type        =   str,
    required    =   False,
    choices     =   ['r', 'g', 'b'],
    help        =   '''
                    If you want to process color images you
                    need to compute each color channel (rgb)
                    seperately.
                    ''')

parser.add_argument('--method',
    type        =   str,
    required    =   True,
    choices     =   ['serial', 'parallel'],
    help        =   '''
                    Note that using 'parallel' instead of 'serial'
                    makes no difference visually nor in performance.
                    Memory can be easily exceeded by trying
                    to process an image with a side length larger
                    than 32 pixels using 'parallel' method.
                    ''')

args = parser.parse_args()

# Create directory for output images
out_dir = 'experiment3_output'
path = os.path.join(os.getcwd(), out_dir)
try:
    os.mkdir(path)

# Make sure directory does not get overwritten
except FileExistsError:
    pass

# -----------------------------------------------------------------------------------

if args.method == 'serial' or args.method == 'parallel':

    img_test = Image.open(args.input).getdata()
    w, h = img_test.size
    if w != h:
        print(
            '''
            The input image must me *squared*!
            ''')

        exit()

    new_img = img_data(args.input)
    size = len(new_img) 

    # Mapping arguments
    channel = 0
    resolution = args.resolution

    if args.resolution == None:
        resolution = 2
    if args.channel == 'r':
        channel = 0
    if args.channel == 'g':
        channel = 1
    if args.channel == 'b':
        channel = 2
    
    if args.method == 'parallel' and int((size ** (1/2)) * 2) >= 64:
        print(
            '''
            Executing this setting with parallel method
            exceeds memory. Please try input image with
            side length < 32px or execute with serial method.
            ''')

        exit()

    # side length and filename (input image) for naming (output image)
    size = int((size * (args.resolution ** 2)) ** (1/2))
    img_name = os.path.basename(args.input)[:-4]

    # -------------------------------------------------------------------------------

    # Process input image data

    # Argument 'serial'
    if args.method == 'serial':
        new_img = serial_qc_processing(new_img, resolution, channel)

    # Argument 'parallel'
    if args.method == 'parallel':
        new_img = parallel_qc_processing(new_img, args.resolution, channel)
    
    # Generate output image
    img_generating(new_img, f"{path}/{img_name}_{args.method}_{size}x{size}px.png")