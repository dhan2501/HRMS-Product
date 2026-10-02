"""
Face descriptor matching helpers. Detection + 128-d descriptor browser me
face-api.js se hota hai. Django sirf 2 descriptors ka Euclidean distance
nikalta hai — distance < 0.5 matlab same face.
"""
import math

MATCH_THRESHOLD = 0.50
EXPECTED_DESCRIPTOR_LENGTH = 128


class FaceDescriptorError(Exception):
    pass


def validate_descriptor(descriptor):
    if not isinstance(descriptor, (list, tuple)):
        raise FaceDescriptorError("Descriptor must be a list of numbers.")
    if len(descriptor) != EXPECTED_DESCRIPTOR_LENGTH:
        raise FaceDescriptorError(
            f"Descriptor must have {EXPECTED_DESCRIPTOR_LENGTH} values, got {len(descriptor)}."
        )
    try:
        return [float(x) for x in descriptor]
    except (TypeError, ValueError):
        raise FaceDescriptorError("Descriptor contains non-numeric values.")


def euclidean_distance(desc_a, desc_b):
    if len(desc_a) != len(desc_b):
        raise FaceDescriptorError("Descriptor length mismatch.")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(desc_a, desc_b)))


def is_match(stored_descriptor, live_descriptor, threshold=MATCH_THRESHOLD):
    distance = euclidean_distance(stored_descriptor, live_descriptor)
    return distance < threshold, distance