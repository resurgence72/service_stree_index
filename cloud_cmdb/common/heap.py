import math


class Heap(object):
    """
    最大堆
    """

    def __init__(self, objs):
        self.cache = objs or []
        self._heapify()

    def __len__(self):
        return len(self.cache)

    def __bool__(self):
        return len(self.cache) > 0

    def __repr__(self):
        return f'heap({self.cache})'

    @property
    def size(self):
        return len(self.cache) - 1

    @property
    def largest(self):
        if not self.cache:
            raise Exception('Empty heap')
        return self.cache[0]

    def show(self):
        """
         调用这个函数绘制一颗二叉树出来,DEBUG用
        :return:
        """
        height = int(math.log2(len(self))) + 1
        for i in range(height):
            width = 2 ** (height - i) - 2
            print(' ' * width, end='')
            blank = ' ' * (width * 2 + 2)
            print(
                blank.join(['{: >2d}'.format(num) for num in self.cache[2 ** i - 1:min(2 ** (i + 1) - 1, len(self))]]))
            print()

    def _swap(self, i, j):
        # 这个方法交换二叉树的两个节点
        self.cache[i], self.cache[j] = self.cache[j], self.cache[i]

    def push(self, num):
        self.cache.append(num)
        self._siftup(self.size)

    def _siftup(self, i):
        while i > 0:
            parent = (i - 1) >> 1
            if self.cache[i] <= self.cache[parent]:
                break
            self._swap(i, parent)
            i = parent

    def pop(self):
        largest = self.largest
        self._swap(0, len(self) - 1)
        self.cache.pop()
        self._siftdown(0)
        return largest

    def reset(self):
        self.cache.clear()

    def _siftdown(self, i):
        while i * 2 + 1 < len(self):
            smaller = i
            if self.cache[i * 2 + 1] > self.cache[smaller]:
                smaller = i * 2 + 1
            if i * 2 + 2 < len(self) and self.cache[i * 2 + 2] > self.cache[smaller]:
                smaller = i * 2 + 2
            if smaller == i:
                return
            self._swap(i, smaller)
            i = smaller

    def _heapify(self):
        """
        构建最大堆
        :return:
        """
        for i in reversed(range(len(self) // 2)):
            self._siftdown(i)

    def top_k(self, k):
        """
        兼容队列总数小于 k 的情况
        :param k:
        :return:
        """
        queue_lens = len(self.cache)
        top = k if queue_lens >= k else queue_lens

        return [self.pop() for _ in range(top)]


if __name__ == '__main__':
    import random

    nums = list(range(20))
    random.shuffle(nums)
    heap = Heap(nums[:])
    heap.show()

    # print(heap.top_k(5))
