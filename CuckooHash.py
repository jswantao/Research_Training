# function insert(key, value)
#     bucket = hash(key)  # 计算哈希值确定桶
#     if bucket is full
#         if another bucket is not full
#             move an item from the full bucket to the other
#         else
#             rehash the table, doubling its size
#             insert the (key, value) pair
#     else
#         insert (key, value) into the bucket
#
# function delete(key)
#     bucket = hash(key)
#     if key is found in the bucket
#         remove (key, value) from the bucket
#     else
#         search in nearby buckets and remove if found
#
# function search(key)
#     bucket = hash(key)
#     if key is found in the bucket
#         return value
#     else
#         search in nearby buckets and return if found
#     return not found


class CuckooHash:
    def __init__(self, size):
        self.size = size
        self.buckets1 = [None] * size
        self.buckets2 = [None] * size

    def insert(self, key, value):
        if self.insert_into_bucket(self.buckets1, key, value):
            return
        if self.insert_into_bucket(self.buckets2, key, value):
            return
        self.rehash()
        self.insert(key, value)

    def insert_into_bucket(self, bucket, key, value):
        index = hash(key) % self.size
        if bucket[index] is None:
            bucket[index] = (key, value)
            return True
        return False

    def rehash(self):
        new_size = self.size * 2
        new_buckets1 = [None] * new_size
        new_buckets2 = [None] * new_size
        self.size = new_size
        for bucket, new_bucket in [(self.buckets1, new_buckets1), (self.buckets2, new_buckets2)]:
            for item in bucket:
                if item:
                    key, value = item
                    self.insert_into_bucket(new_bucket, key, value)
        self.buckets1 = new_buckets1
        self.buckets2 = new_buckets2

    def search(self, key):
        index1 = hash(key) % self.size
        if self.buckets1[index1] and self.buckets1[index1][0] == key:
            return self.buckets1[index1][1]
        index2 = hash(key) % self.size
        if self.buckets2[index2] and self.buckets2[index2][0] == key:
            return self.buckets2[index2][1]
        return None
