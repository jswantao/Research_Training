import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np


# 定义 PRP 类
class PRP:
    def __init__(self, key):
        self.key = key
        self.cipher = Cipher(algorithms.AES(self.key), modes.ECB())

    def __call__(self, data):
        encryptor = self.cipher.encryptor()
        padded_data = data.ljust(16, b'\0')[:16]  # 保证输入长度为 16 字节
        return encryptor.update(padded_data)


# 生成随机密钥
def generate_key():
    return os.urandom(16)  # AES 的 128 位密钥


# 基于 PRP 的 Cuckoo 哈希函数,prp_based_cuckoo_hash 函数接受元素列表、矩阵的大小和 PRP 函数的数量。
def prp_based_cuckoo_hash(elements, m, d, kappa):
    # 生成 kappa 个独立的 PRP 函数
    keys = [generate_key() for _ in range(kappa)]  # 使用列表推导式生成一个包含 kappa 个随机密钥的列表
    prps = [PRP(key) for key in keys]  # 使用生成的密钥创建 kappa 个独立的 PRP 函数，并将它们存储在一个列表中。

    # 使用 object 类型矩阵以支持存储字符串
    matrix = np.empty((m, d), dtype=object)
    matrix.fill(None)

    # 插入元素
    max_attempts = 100  # 最大尝试次数
    for element in elements:
        element_bytes = str(element).encode('utf-8')
        attempts = 0
        while attempts < max_attempts:
            for i in range(kappa):
                prp_output = prps[i](element_bytes)
                row_index = int.from_bytes(prp_output[:4], 'big') % m
                col_index = int.from_bytes(prp_output[4:8], 'big') % d
                if matrix[row_index, col_index] is None:
                    matrix[row_index, col_index] = element
                    break
            else:
                # 如果所有 PRP 函数都冲突，进行驱逐
                old_element = matrix[row_index, col_index]
                matrix[row_index, col_index] = element
                element = old_element
                attempts += 1
                continue
            break
        if attempts >= max_attempts:
            raise RuntimeError(f"Failed to insert element '{element}' due to excessive collisions.")
    return matrix, prps


# 验证函数：检查元素是否在正确的位置
def verify_prp_output(matrix, element, prps, m, d):
    element_bytes = str(element).encode('utf-8')
    for i, prp in enumerate(prps):
        prp_output = prp(element_bytes)
        row_index = int.from_bytes(prp_output[:4], 'big') % m
        col_index = int.from_bytes(prp_output[4:8], 'big') % d
        if matrix[row_index, col_index] == element:
            print(f"Element '{element}' is correctly placed at ({row_index}, {col_index}) using PRP {i + 1}.")
            return
    print(f"Element '{element}' was not placed using any PRP.")


# 示例使用
elements = ["apple", "banana", "cherry", "date"]
m = 10  # 矩阵行数
d = 10  # 矩阵列数
kappa = 2  # PRP 函数数量

# 构建 Cuckoo 哈希矩阵
matrix, prps = prp_based_cuckoo_hash(elements, m, d, kappa)
print("Matrix:")
print(matrix)

# 验证每个元素的位置
print("\nVerification:")
for element in elements:
    verify_prp_output(matrix, element, prps, m, d)
