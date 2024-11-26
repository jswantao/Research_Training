import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# 伪随机函数（PRF）实现
def prf(key, input):
    """
    使用 AES 加密算法实现伪随机函数（PRF）。
    参数：
    key: 密钥
    input: 输入数据（通常是点的索引）
    返回：生成的伪随机字节（8 字节）
    """
    cipher = Cipher(algorithms.AES(key), modes.ECB())  # 使用 AES-ECB 模式
    encryptor = cipher.encryptor()
    padded_input = input.ljust(16, b'\0')  # 填充输入至 16 字节（AES 块大小）
    return encryptor.update(padded_input)[:8]  # 返回前 8 字节


# 将整数转换为字节串
def int_to_bytes(value, length):
    """
    将整数转换为指定长度的字节串。
    """
    return value.to_bytes(length, byteorder='big')  # 使用大端字节序


# 生成 DPF 密钥共享
def dpf_gen(alpha, beta, size):
    """
    生成分布式点函数的密钥共享。
    参数：
    alpha: 触发点
    beta: 目标返回值
    size: 输入域的大小
    返回：share0 和 share1 作为两方的密钥共享
    """
    # 随机生成两方的 AES 密钥
    key0 = os.urandom(16)  # 方 0 的 AES 密钥
    key1 = os.urandom(16)  # 方 1 的 AES 密钥

    # 使用 PRF 生成共享值
    share0 = [(i, prf(key0, bytes([i]))) for i in range(size)]  # 方 0 的共享
    share1 = [(i, prf(key1, bytes([i]))) for i in range(size)]  # 方 1 的共享

    # 获取触发点处的伪随机共享值
    share1_at_alpha = share1[alpha][1]  # share1[alpha] 的值

    # 将 beta 转换为字节串
    beta_bytes = int_to_bytes(beta, len(share1_at_alpha))

    # 修改触发点处的 share0，使得合并结果为 beta
    modified_share0 = bytes([b ^ s for b, s in zip(beta_bytes, share1_at_alpha)])

    # 更新 share0[alpha] 为修改后的值
    share0[alpha] = (alpha, modified_share0)

    return share0, share1  # 返回两个参与方的密钥共享


# 评估分布式点函数
def dpf_eval(share, x):
    """
    评估分布式点函数，返回对应共享的值。
    参数：
    share: 一方的密钥共享
    x: 查询点
    返回：查询点对应的共享值（字节串）
    """
    for i, value in share:  # 遍历共享列表
        if i == x:  # 如果查询点匹配当前索引
            return value  # 返回对应的共享值
    return b'\0' * 8  # 如果查询点未匹配，返回全零字节


# 示例：生成 DPF 并进行评估
alpha, beta = 3, 12  # 设置触发点 alpha 和返回值 beta
size = 10  # 输入域的大小

# 调用生成算法，生成两方的密钥共享
share0, share1 = dpf_gen(alpha, beta, size)

# 调用评估算法，在触发点 alpha 进行评估
share0_eval = dpf_eval(share0, alpha)
share1_eval = dpf_eval(share1, alpha)

# 合并结果并限制范围到 8 位
merged_result = int.from_bytes(share0_eval, 'big') ^ int.from_bytes(share1_eval, 'big')
result = merged_result & 0xFF  # 取最低 8 位
print(f"Result at alpha: {result}")  # 应输出 beta = 10
