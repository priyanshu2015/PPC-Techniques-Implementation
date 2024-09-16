import tenseal as ts
import time
import base64

POLY_MODULUS_DEGREE = 16384
#POLY_MODULUS_DEGREE = 8192
#POLY_MODULUS_DEGREE = 4096

# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=POLY_MODULUS_DEGREE,
    #plain_modulus=1032193
    plain_modulus=536903681
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
    divisor = int(POLY_MODULUS_DEGREE / 2)  # the divisor splits the vector into smaller chunks to be encrypted,
    encrypted_chunks = []
    if len(vector) > divisor:
        for i in range(0, len(vector), divisor):
            chunk = vector[i:i + divisor]
            encrypted_chunk = ts.bfv_vector(context, chunk)
            encrypted_chunks.append(encrypted_chunk)
    else:
        encrypted_vector = ts.bfv_vector(context, vector)
        encrypted_chunks.append(encrypted_vector)

    return encrypted_chunks, len(vector)


def serialize_encrypted_vector(encrypted_vectors: ts.bfv_vector) -> str:
    """
    Serialize the encrypted vector to bytes and then to base64
    :param encrypted_vectors: encrypted vector
    :return: serialized encrypted vector
    """
    bytes = encrypted_vectors.serialize()
    serialized = base64.b64encode(bytes).decode('utf-8')
    return serialized


def serialize_encrypted_vectors(encrypted_vectors: list[ts.bfv_vector]) -> list[str]:
    """
    Serialize the encrypted vectors to bytes and then to base64
    :param encrypted_vectors: list of encrypted vectors
    :return: list of serialized encrypted vectors
    """


    serialized_vectors = []
    for v in encrypted_vectors:
        serialized = serialize_encrypted_vector(v)
        serialized_vectors.append(serialized)
    return serialized_vectors


def deserialize_encrypted_vector(serialized_vector: bytes) -> ts.bfv_vector:
    """
    Deserialize the encrypted vector from base 64 to bytes to ts.bfv_vector
    :param serialized_vector: serialized encrypted vector
    :return: encrypted vector
    """
    bytes = base64.b64decode(serialized_vector)
    return ts.bfv_vector_from(context, bytes)


def deserialize_encrypted_vectors(serialized_vectors: list[bytes]) -> list[ts.bfv_vector]:
    """
    Deserialize the encrypted vectors from base 64 to bytes to ts.bfv_vector
    :param serialized_vectors: list of serialized encrypted vectors
    :return: list of encrypted vectors
    """
    encrypted_vectors = []
    for s in serialized_vectors:
        bfv_vector = deserialize_encrypted_vector(s)
        encrypted_vectors.append(bfv_vector)
    return encrypted_vectors


def get_serialized_context():
    context_serialized = context.serialize(save_public_key=True, save_secret_key=False, save_galois_keys=True)
    context_encoded = base64.b64encode(context_serialized).decode('utf-8')
    return context_encoded


if __name__ == '__main__':
    vector = [
        758.44, -42.17, -131.62, 335.83, 713.28, 926.36, 322.87, 427.88, -402.07,
        -187.94, -57.61, 941.3, 573.78, 374.23, -112.35, -99.83, -106.83, -106.1,
        302.22, -167.31, -325.4, 352.88, 408.14, -455.52, 131.08, -266.86, -158.13,
        436.95, 734.76, -66.03, 269.47, 251.3, -76.69, 776.45, 576.62, 502.76,
        -425.05, 204.42, -392.02, 651.18, 956.07, -122.1, -398.93, 589.15, -226.54,
        -112.51, -498.89, -378.42, 501.34, -172.22
    ]
    vector = [convert_flot_to_int(val) for val in vector[:30]]
    print(vector)
    #vector = [100 for i in range(50)] + [-100 for i in range(50)]
    encrypted_vectors, number_of_elements = encrypt_vector_for_sum(vector)

    serialized_vectors = serialize_encrypted_vectors(encrypted_vectors)
    for s in serialized_vectors:
        # print byte size of s
        size_bytes = len(s)
        kb = size_bytes / 1024

        print(f"Size: {kb} Kb")

    deserialized_vectors = deserialize_encrypted_vectors(serialized_vectors)
    encrypted_sum = deserialized_vectors[0].sum()
    for s in deserialized_vectors[1:]:
        encrypted_sum += s.sum()

    decrypted_sum = encrypted_sum.decrypt()
    real_sum = convert_int_to_float(decrypted_sum[0])
    print(f"Decrypted sum: {decrypted_sum[0]}, converted sum: {real_sum}, real sum: {sum(vector)/100}")
    """
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
    """