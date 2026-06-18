from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Random import get_random_bytes


def split_key(key: bytes, threshold: int = 3, num_shares: int = 5) -> list[str]:
    """
    Split a 32-byte AES key into num_shares hex-string shares.
    Any `threshold` of them can later reconstruct the key.
    """
    if len(key) != 32:
        raise ValueError("Key must be exactly 32 bytes (AES-256)")

    half1, half2 = key[:16], key[16:]

    shares1 = Shamir.split(threshold, num_shares, half1)
    shares2 = Shamir.split(threshold, num_shares, half2)

    combined_shares = []
    for (idx1, part1), (idx2, part2) in zip(shares1, shares2):
        assert idx1 == idx2
        # 1 byte index + 16 bytes (half1 share) + 16 bytes (half2 share) = 33 bytes
        blob = bytes([idx1]) + part1 + part2
        combined_shares.append(blob.hex())

    return combined_shares


def recover_key(share_hexes: list[str]) -> bytes:
    """
    Recover the original 32-byte AES key from at least `threshold` shares.
    """
    parsed1 = []
    parsed2 = []

    for h in share_hexes:
        blob = bytes.fromhex(h)
        index = blob[0]
        part1 = blob[1:17]
        part2 = blob[17:33]
        parsed1.append((index, part1))
        parsed2.append((index, part2))

    half1 = Shamir.combine(parsed1)
    half2 = Shamir.combine(parsed2)

    return half1 + half2


if __name__ == "__main__":
    # Standalone self-test
    original_key = get_random_bytes(32)
    shares = split_key(original_key, threshold=3, num_shares=5)

    print("Original key:", original_key.hex())
    print(f"Generated {len(shares)} shares:")
    for i, s in enumerate(shares, start=1):
        print(f"  Share {i}: {s}")

    # Try recovering using only 3 of the 5 shares (shares 1, 3, 5)
    subset = [shares[0], shares[2], shares[4]]
    recovered_key = recover_key(subset)

    print("\nRecovered key:", recovered_key.hex())
    print("Match:", original_key == recovered_key)