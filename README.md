# README - 分布式点函数 (DPF) 实现

## 项目简介

本项目实现了一个简单的 **分布式点函数（Distributed Point Function, DPF）**，该函数允许通过密钥共享的方式安全地计算一个点函数 \( f<sub>{α, β}</sub>(x) \)。点函数在触发点 \( α \) 返回值 \( β \)，在其他点返回 0。

该实现基于 **AES** 作为伪随机函数（PRF）构造密钥共享，并利用异或（XOR）操作确保在触发点 \( α \) 合并共享值后返回正确的结果。

---

## 功能概述

### 1. DPF 密钥生成（`dpf_gen`）
- 根据给定的触发点 \( α \) 和返回值 \( β \)，生成两方的密钥共享 `share0` 和 `share1`。
- 使用伪随机函数生成伪随机共享值，并调整触发点 \( α \) 的共享值，确保合并结果为 \( β \)。

### 2. DPF 评估（`dpf_eval`）
- 使用共享密钥在查询点 \( x \) 处评估密钥共享，返回对应共享值。

### 3. 共享合并
- 将两方的共享值通过异或操作合并，得到点函数在查询点处的最终结果。

---

## 运行环境

- **Python**：3.7 或更高版本
- **依赖库**：
  - `cryptography`：用于实现 AES 加密

---

## 文件说明

- **`prf` 函数**：实现基于 AES 的伪随机函数，用于生成共享值。
- **`int_to_bytes` 函数**：将整数转换为指定长度的字节串，便于与共享值对齐。
- **`dpf_gen` 函数**：生成分布式点函数的密钥共享。
- **`dpf_eval` 函数**：评估分布式点函数，返回共享值。
- **主程序**：示例演示如何使用上述函数生成密钥共享并评估点函数。

---

## 使用方法

### 1. 设置触发点和返回值
在主程序中，设置触发点 \( α \) 和返回值 \( β \)，例如：

```python
alpha, beta = 3, 10  # 设置触发点 alpha 和返回值 beta
size = 10  # 输入域的大小
```

### 2. 调用密钥生成函数
```python
share0, share1 = dpf_gen(alpha, beta, size)
```

### 3. 评估共享值
对触发点 \( α \) 使用 `dpf_eval` 函数分别评估方 0 和方 1 的共享值：

```python
share0_eval = dpf_eval(share0, alpha)
share1_eval = dpf_eval(share1, alpha)
```

### 4. 合并共享值
将两方共享值异或合并，得到最终的结果：

```python
merged_result = int.from_bytes(share0_eval, 'big') ^ int.from_bytes(share1_eval, 'big')
result = merged_result & 0xFF  # 取最低 8 位
print(f"Result at alpha: {result}")  # 输出: beta 值
```

---

## 函数详细说明

### 1. `prf` 函数
- 使用 AES 加密实现伪随机函数。
- 输入一个密钥 `key` 和一个点索引 `input`，返回一个固定长度的伪随机字节串（8 字节）。

### 2. `int_to_bytes` 函数
- 将整数值转换为固定长度的字节串，便于与 PRF 输出的共享值进行异或操作。

### 3. `dpf_gen` 函数
- 生成两方的密钥共享 `share0` 和 `share1`：
  - 非触发点的共享值通过 PRF 生成。
  - 触发点 \( α \) 的共享值通过调整确保合并后返回 \( β \)。
- 使用 XOR 操作修改 `share0[alpha]`：
  \[
  $\text${share0[alpha]} = β ⊕ $\text${share1[alpha]}
  \]

### 4. `dpf_eval` 函数
- 根据密钥共享 `share` 和查询点 \( x \)，返回该点处的共享值。

---

## 示例输入与输出

### 输入参数
- \( α = 3 \)：触发点
- \( β = 10 \)：触发点的返回值
- 输入域大小 \( size = 10 \)

### 输出结果
```plaintext
Result at alpha: 10
```

---

## 原理解析

### 1. 密钥共享生成
- 使用 PRF 为每个点生成伪随机共享值。
- 通过调整触发点 \( α \) 的共享值，确保两方共享合并后返回 \( β \)。

### 2. 共享合并
- 将两个共享值进行异或操作，通过异或的结合律和自反性确保触发点处的合并结果为 \( β \)。

---

## 注意事项

1. **输入域大小**：需要确保输入域大小 \( size \) 足够覆盖触发点 \( α \)。
2. **字节串长度**：确保 `beta` 转换为字节串后长度与 PRF 输出一致。
3. **依赖库**：需要安装 `cryptography` 库。可以使用以下命令安装：
   ```bash
   pip install cryptography
   ```

---

## 扩展与改进

- **多方扩展**：目前实现的是两方共享，未来可以扩展为多方共享。
- **性能优化**：针对大规模输入域可以优化 PRF 的计算效率。

---

## 联系作者

如有问题或建议，请随时联系开发者！




# **基于 PRP 的 Cuckoo 哈希实现**

## **简介**
本项目实现了基于 PRP（伪随机置换）的 Cuckoo 哈希表。该方法通过伪随机函数将元素映射到二维矩阵的行列索引位置，以实现高效的数据存储和冲突处理。代码支持：
- 构建基于 PRP 的 Cuckoo 哈希表；
- 在冲突发生时驱逐已有元素并重新插入；
- 验证每个元素是否存储在正确的位置。

---

## **功能概览**
### **1. 核心功能**
- **构建哈希表**：使用 PRP 函数为元素生成多个候选位置，插入二维矩阵中。
- **冲突处理**：当目标位置被占用时，驱逐已有元素并重新尝试插入。
- **验证功能**：通过 PRP 函数输出验证矩阵中每个元素的位置是否正确。

### **2. 支持的数据类型**
矩阵采用 `numpy` 的 `object` 类型，支持存储任意 Python 数据类型（如字符串、整数等）。

---

## **代码结构**

### **1. 类与函数**
#### **PRP 类**
- 用于实现伪随机置换，基于 AES-ECB 模式加密生成伪随机输出。
- **输入**：16 字节的密钥和目标数据（字节串）。
- **输出**：加密后的伪随机字节数据，用于计算矩阵的行列索引。

#### **generate_key 函数**
- 生成一个 128 位（16 字节）的随机密钥。
- 用于初始化 PRP 对象。

#### **prp_based_cuckoo_hash 函数**
- 核心函数，用于构建基于 PRP 的 Cuckoo 哈希表。
- **输入**：
  - `elements`：需要插入的元素列表。
  - `m`：矩阵的行数。
  - `d`：矩阵的列数。
  - `kappa`：PRP 函数数量，用于确定每个元素的候选位置数量。
- **输出**：
  - 哈希表矩阵 `matrix`。
  - PRP 函数列表 `prps`，用于后续验证。

#### **verify_prp_output 函数**
- 验证函数，用于检查每个元素是否被正确插入到矩阵中。
- **输入**：
  - `matrix`：构建完成的 Cuckoo 哈希表。
  - `element`：需要验证的目标元素。
  - `prps`：构建过程中使用的 PRP 函数列表。
  - `m, d`：矩阵的行数和列数。
- **输出**：打印验证结果，显示元素的插入位置和对应的 PRP 函数编号。

---

## **代码逻辑**
### **1. 哈希表构建**
- 每个元素通过 \( \kappa \) 个 PRP 函数生成候选位置（行列索引）。
- 检查候选位置是否为空：
  - 如果为空，将元素插入对应位置。
  - 如果已被占用，驱逐已有元素并将其重新插入。

### **2. 冲突处理**
- 每次冲突会尝试重新插入被驱逐的元素。
- 如果尝试次数超过最大限制（`max_attempts`），抛出错误。

### **3. 验证过程**
- 针对每个元素，使用相同的 PRP 函数重新计算行列索引。
- 检查矩阵中对应位置是否存储了目标元素。
- 打印验证结果。

---

## **示例用法**

### **运行示例代码**
以下为完整的使用示例：
```python
elements = ["apple", "banana", "cherry", "date"]  # 待插入的元素
m = 10  # 矩阵行数
d = 10  # 矩阵列数
kappa = 2  # PRP 函数数量

# 构建哈希表
matrix, prps = prp_based_cuckoo_hash(elements, m, d, kappa)

# 打印矩阵
print("Matrix:")
print(matrix)

# 验证每个元素是否正确插入
print("\nVerification:")
for element in elements:
    verify_prp_output(matrix, element, prps, m, d)
```

### **输出示例**
运行上述代码将生成如下输出：
```plaintext
Matrix:
[['date' None None None None None None None None None]
 [None None None None None None None None None None]
 [None 'cherry' None None None None None None None None]
 [None None None None None None None None None None]
 [None 'banana' None None None None None None None None]
 [None None None None None None None None None None]
 [None None None None None None None None None None]
 [None None None None None None None None None None]
 [None None None None None None 'apple' None None None]
 [None None None None None None None None None None]]

Verification:
Element 'apple' is correctly placed at (8, 6) using PRP 1.
Element 'banana' is correctly placed at (4, 1) using PRP 1.
Element 'cherry' is correctly placed at (2, 1) using PRP 1.
Element 'date' is correctly placed at (0, 0) using PRP 1.
```

---

## **注意事项**
1. **矩阵大小与元素数量**：
   - 矩阵的行列数应根据元素数量和冲突概率合理设置。
   - 通常 \( m $\times$ d $\geq$ 1.27 $\times$ n \)（其中 \( n \) 是元素数量），以保证较低的冲突率。

2. **冲突驱逐限制**：
   - 代码设置了最大冲突处理尝试次数（`max_attempts = 100`），以避免陷入无限循环。

3. **PRP 安全性**：
   - PRP 使用 AES-ECB 模式，密钥随机生成，提供良好的随机性和分布特性。
   - 如果有更高的安全性需求，可改用 AES-CBC 或其他模式。

---

## **扩展功能**
1. **支持动态扩展**：
   - 当矩阵空间不足时，可加入自动扩展逻辑，通过增加矩阵大小减少冲突。

2. **支持更多数据类型**：
   - 当前矩阵支持存储任意 Python 对象，可根据需求扩展到更复杂的数据结构。

3. **更高效的验证方法**：
   - 针对大规模数据集，验证过程可并行化以加速性能。

---

## **依赖环境**
- Python 3.x
- `cryptography` 库
- `numpy` 库

安装依赖：
```bash
pip install cryptography numpy
```

---

## **联系与反馈**
如需帮助或改进建议，请随时联系。希望本代码对您有帮助！
