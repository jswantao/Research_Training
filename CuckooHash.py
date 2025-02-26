class CuckooHash:
    def __init__(self, size):
        # 初始化哈希表，设置初始大小
        self.size = size
        self.buckets1 = [None] * size  # 创建第一个桶
        self.buckets2 = [None] * size  # 创建第二个桶

    def insert(self, key, value):
        # 尝试将键值对插入到两个桶中，如果两个桶都满了，则进行rehash
        if self.insert_into_bucket(self.buckets1, key, value):
            return  # 成功插入第一个桶，直接返回
        if self.insert_into_bucket(self.buckets2, key, value):
            return  # 成功插入第二个桶，直接返回

        # 如果两个桶都已满，则进行rehash并重新插入
        self.rehash()
        self.insert(key, value)

    def insert_into_bucket(self, bucket, key, value):
        # 计算该键的哈希值，找到在桶中的索引
        index = hash(key) % self.size
        if bucket[index] is None:  # 如果该位置为空
            bucket[index] = (key, value)  # 插入键值对
            return True  # 插入成功，返回True
        return False  # 插入失败（位置已满），返回False

    def rehash(self):
        # 扩展哈希表的大小，并重新哈希所有现有的键值对
        new_size = self.size * 2  # 新的大小为原来大小的2倍
        new_buckets1 = [None] * new_size  # 新的桶1
        new_buckets2 = [None] * new_size  # 新的桶2
        self.size = new_size  # 更新哈希表的大小

        # 重新插入原来两个桶中的所有元素
        for bucket, new_bucket in [(self.buckets1, new_buckets1), (self.buckets2, new_buckets2)]:
            for item in bucket:
                if item:
                    key, value = item
                    # 将每个元素重新插入新的桶中
                    self.insert_into_bucket(new_bucket, key, value)

        # 更新桶的引用
        self.buckets1 = new_buckets1
        self.buckets2 = new_buckets2

    def search(self, key):
        # 计算该键在第一个桶中的索引
        index1 = hash(key) % self.size
        if self.buckets1[index1] and self.buckets1[index1][0] == key:
            return self.buckets1[index1][1]  # 如果找到，返回值

        # 计算该键在第二个桶中的索引
        index2 = hash(key) % self.size
        if self.buckets2[index2] and self.buckets2[index2][0] == key:
            return self.buckets2[index2][1]  # 如果找到，返回值

        return None  # 如果没有找到，返回None
