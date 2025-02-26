import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np


# 定义 PRP（伪随机置换）类
class PRP:
    def __init__(self, key):
        # 使用提供的密钥初始化 AES-ECB 加密器
        self.key = key
        self.cipher = Cipher(algorithms.AES(self.key), modes.ECB())

    def __call__(self, data):
        # 调用 PRP 时，对输入数据进行加密
        encryptor = self.cipher.encryptor()
        # 将数据填充到 16 字节，AES 需要块大小为 16 字节
        padded_data = data.ljust(16, b'\0')[:16]
        return encryptor.update(padded_data)  # 返回加密后的数据


# 生成随机的 128 位（16 字节）AES 密钥
def generate_key():
    return os.urandom(16)


# 基于 PRP 的 Cuckoo 哈希函数
# elements: 要插入的元素列表
# m: 矩阵的行数
# d: 矩阵的列数
# kappa: PRP 函数的数量
def prp_based_cuckoo_hash(elements, m, d, kappa):
    # 生成 kappa 个独立的 PRP 函数，每个函数使用一个随机密钥
    keys = [generate_key() for _ in range(kappa)]
    prps = [PRP(key) for key in keys]

    # 创建一个 m x d 的矩阵，初始化为 None，使用 object 类型以支持存储字符串
    matrix = np.empty((m, d), dtype=object)
    matrix.fill(None)

    max_attempts = 100  # 设置最大冲突尝试次数

    # 插入每一个元素到哈希矩阵中
    for element in elements:
        element_bytes = str(element).encode('utf-8')  # 将元素转换为字节格式
        attempts = 0  # 当前元素的尝试次数

        while attempts < max_attempts:
            # 使用每一个 PRP 函数计算潜在的插入位置
            for i in range(kappa):
                prp_output = prps[i](element_bytes)  # PRP 函数生成的加密输出
                row_index = int.from_bytes(prp_output[:4], 'big') % m  # 计算行索引
                col_index = int.from_bytes(prp_output[4:8], 'big') % d  # 计算列索引

                if matrix[row_index, col_index] is None:
                    # 如果该位置为空，将元素插入矩阵中
                    matrix[row_index, col_index] = element
                    break
            else:
                # 如果所有 PRP 函数计算的位置都已被占用，执行驱逐操作
                old_element = matrix[row_index, col_index]  # 取出原有元素
                matrix[row_index, col_index] = element  # 插入新元素
                element = old_element  # 被驱逐的元素重新插入
                attempts += 1
                continue
            break

        # 如果尝试次数超出最大限制，报错提示插入失败
        if attempts >= max_attempts:
            raise RuntimeError(f"Failed to insert element '{element}' due to excessive collisions.")

    # 返回填充后的哈希矩阵和 PRP 函数列表
    return matrix, prps


# 验证函数：检查元素是否在正确的位置
def verify_prp_output(matrix, element, prps, m, d):
    element_bytes = str(element).encode('utf-8')  # 将元素转换为字节格式
    for i, prp in enumerate(prps):
        prp_output = prp(element_bytes)
        row_index = int.from_bytes(prp_output[:4], 'big') % m
        col_index = int.from_bytes(prp_output[4:8], 'big') % d

        if matrix[row_index, col_index] == element:
            # 如果在计算的位置找到元素，则验证成功
            print(f"Element '{element}' is correctly placed at ({row_index}, {col_index}) using PRP {i + 1}.")
            return

    # 如果所有 PRP 都未找到元素，输出验证失败
    print(f"Element '{element}' was not placed using any PRP.")


# 示例使用
elements = ["apple", "banana", "cherry", "date"]  # 要插入的元素列表
m = 10  # 矩阵行数
d = 10  # 矩阵列数
kappa = 2  # PRP 函数的数量

# 构建 Cuckoo 哈希矩阵
matrix, prps = prp_based_cuckoo_hash(elements, m, d, kappa)
print("Matrix:")
print(matrix)

# 验证每个元素的位置是否正确
print("\nVerification:")
for element in elements:
    verify_prp_output(matrix, element, prps, m, d)
