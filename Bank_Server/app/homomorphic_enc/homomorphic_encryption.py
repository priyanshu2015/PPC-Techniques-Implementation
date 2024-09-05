import tenseal as ts
import time


POLY_MODULUS_DEGREE = 4096
# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=POLY_MODULUS_DEGREE,
    plain_modulus=1032193
    #plain_modulus=4294967295,
)
context.generate_galois_keys()


def convert_flot_to_int(value: float) -> int:
    """
    multiply the 2 digit float by 100 and convert to int
    :param value:
    :return:
    """
    return int(value * 100)


def convert_int_to_float(value: int) -> float:
    """
    convert the int to float and divide by 100
    :param value:
    :return:
    """
    return value / 100


def calculate_encrypted_sum_multiple(vector: list) -> int:
    """
    This functions doesn't work! cant compute on vectors of different sizes

    if the vector is too large, we can split it into smaller chunks
    and sum the chunks
    :param vector:
    :return:
    """

    divisor = int(POLY_MODULUS_DEGREE / 2)  # this is the maximum size of the vector that can be encrypted
    # if len(vector) % divisor != 0:
    #    raise ValueError("The vector size must be a multiple of the divisor")

    sums = []
    if len(vector) > divisor:
        for i in range(0, len(vector), divisor):
            chunk = vector[i:i + divisor]
            encrypted_chunk = ts.bfv_vector(context, chunk)
            encrypted_sum = encrypted_chunk.sum()
            sums.append(encrypted_sum)
    else:
        encrypted_vector = ts.bfv_vector(context, vector)
        encrypted_sum = encrypted_vector.sum()
        sums.append(encrypted_sum)

    # print(f"Number of blocks: {len(sums)}")

    encrypted_sum = sums[0]
    for s in sums[1:]:
        encrypted_sum += s

    decrypted_sum = encrypted_sum.decrypt()
    return decrypted_sum[0]


def encrypt_vector_for_sum(vector: list) -> (list, int):
    """
    Encrypt the vector, if the vector is too large, we can split it into smaller chunks and return the encrypted chunks
    and number of chunks
    :Note: This only works for sum operations because the resulting vectors can be of different sizes
    :param vector:
    :return:
    """
    divisor = 100  # the divisor splits the vector into smaller chunks to be encrypted,
    encrypted_chunks = []
    if len(vector) > divisor:
        for i in range(0, len(vector), divisor):
            chunk = vector[i:i + divisor]
            encrypted_chunk = ts.bfv_vector(context, chunk)
            encrypted_chunks.append(encrypted_chunk)
    else:
        encrypted_vector = ts.bfv_vector(context, vector)
        encrypted_chunks.append(encrypted_vector)

    return encrypted_chunks, len(encrypted_chunks)


if __name__ == '__main__':
    for size in range(516000, 516100, 10):
        vector = [1 for i in range(size)]
        s = sum(vector)
        start = time.perf_counter_ns()
        vector_sum = calculate_encrypted_sum_multiple(vector)
        stop = time.perf_counter_ns()
        print(f"vector size: {size}")
        print(f"Time taken: {(stop-start)/1e6} ms")
        print(f"Encrypted sum: {vector_sum} / {sum(vector)}")
        print("-------------------------------------------------")
