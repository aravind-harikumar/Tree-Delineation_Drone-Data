from numba import jit, cuda
import numpy as np
import time

@jit(nopython=True)
def compute_bin(x, n, xmin, xmax):
    # special case to mirror NumPy behavior for last bin
    if x == xmax:
        return n - 1 # a_max always in last bin

    # SPEEDTIP: Remove the float64 casts if you don't need to exactly reproduce NumPy
    bin = np.int32(n * (np.float64(x) - np.float64(xmin)) / (np.float64(xmax) - np.float64(xmin)))

    if bin < 0 or bin >= n:
        return None
    else:
        return bin

@cuda.jit
def histogram(x, xmin, xmax, histogram_out):
    nbins = histogram_out.shape[0]
    bin_width = (xmax - xmin) / nbins

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, x.shape[0], stride):
        # note that calling a numba.jit function from CUDA automatically
        # compiles an equivalent CUDA device function!
        bin_number = compute_bin(x[i], nbins, xmin, xmax)

        if bin_number >= 0 and bin_number < histogram_out.shape[0]:
            cuda.atomic.add(histogram_out, bin_number, 1)

@cuda.jit
def min_max(x, min_max_array):
    nelements = x.shape[0]

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    # Array already seeded with starting values appropriate for x's dtype
    # Not a problem if this array has already been updated
    local_min = min_max_array[0]
    local_max = min_max_array[1]

    for i in range(start, x.shape[0], stride):
        element = x[i]
        local_min = min(element, local_min)
        local_max = max(element, local_max)

    # Now combine each thread local min and max
    cuda.atomic.min(min_max_array, 0, local_min)
    cuda.atomic.max(min_max_array, 1, local_max)


def dtype_min_max(dtype):
    '''Get the min and max value for a numeric dtype'''
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
    else:
        info = np.finfo(dtype)
    return info.min, info.max


@jit(nopython=True)
def get_bin_edges(a, nbins, a_min, a_max):
    bin_edges = np.empty((nbins+1,), dtype=np.float64)
    delta = (a_max - a_min) / nbins
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point
    return bin_edges


def numba_gpu_histogram(a, bins):
    # Move data to GPU so we can do two operations on it
    a_gpu = cuda.to_device(a)

    ### Find min and max value in array
    dtype_min, dtype_max = dtype_min_max(a.dtype)
    # Put them in the array in reverse order so that they will be replaced by the first element in the array
    min_max_array_gpu = cuda.to_device(np.array([dtype_max, dtype_min], dtype=a.dtype))
    min_max[64, 64](a_gpu, min_max_array_gpu)
    a_min, a_max = min_max_array_gpu.copy_to_host()

    # SPEEDTIP: Skip this step if you don't need to reproduce the NumPy histogram edge array
    bin_edges = get_bin_edges(a, bins, a_min, a_max) # Doing this on CPU for now

    ### Bin the data into a histogram 
    histogram_out = cuda.to_device(np.zeros(shape=(bins,), dtype=np.int32))
    histogram[64, 64](a_gpu, a_min, a_max, histogram_out)

    return histogram_out.copy_to_host(), bin_edges


print(numba_gpu_histogram(np.array(range(1,100000000)),100000000))

# x = np.arange(10000).reshape(100, 100)

# @jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
# def go_fast(a): # Function is compiled to machine code when called the first time
#     trace = 0
#     for i in range(a.shape[0]):   # Numba likes loops
#         trace += np.tanh(a[i, i]) # Numba likes NumPy functions
#     return a + trace              # Numba likes NumPy broadcasting

# # DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
# start = time.time()
# go_fast(x)
# end = time.time()
# print("Elapsed (with compilation) = %s" % (end - start))

# # NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
# start = time.time()
# go_fast(x)
# end = time.time()
# print("Elapsed (after compilation) = %s" % (end - start))







# @jit(nopython=True)
# def get_bin_edges(a, bins):
#     bin_edges = np.zeros((bins+1,), dtype=np.float64)
#     a_min = a.min()
#     a_max = a.max()
#     delta = (a_max - a_min) / bins
#     for i in range(bin_edges.shape[0]):
#         bin_edges[i] = a_min + i * delta

#     bin_edges[-1] = a_max  # Avoid roundoff error on last point
#     return bin_edges


# @jit(nopython=True)
# def compute_bin(x, bin_edges):
#     # assuming uniform bins for now
#     n = bin_edges.shape[0] - 1
#     a_min = bin_edges[0]
#     a_max = bin_edges[-1]

#     # special case to mirror NumPy behavior for last bin
#     if x == a_max:
#         return n - 1 # a_max always in last bin

#     bin = int(n * (x - a_min) / (a_max - a_min))

#     if bin < 0 or bin >= n:
#         return None
#     else:
#         return bin


# @jit(nopython=True)
# def numba_histogram(a, bins):
#     hist = np.zeros((bins,), dtype=np.intp)
#     bin_edges = get_bin_edges(a, bins)

#     for x in a.flat:
#         bin = compute_bin(x, bin_edges)
#         if bin is not None:
#             hist[int(bin)] += 1

#     return hist, bin_edges

# print(numba_histogram(np.array([1,2,3,4,55,6,7,7744,44]),10))