from collections import defaultdict
from tqdm import tqdm

class unit:
    def __init__(self, val=None):
        self.val = val
        self.next = None
        self.previous = None


class SortedEdges:
    def __init__(self):
        self._data = []
        self._frees = []
        self._head = None
        self._tail = None
        self._byNode = defaultdict(list)

    def __repr__(self):
        cursor = S._head
        ret=''
        while cursor is not None:
            v = S._data[cursor]
            ret=ret+'{0}:  {1}<- {2} ->{3}\n'.format(cursor,v.previous,v.val,v.next)
            cursor=v.next
        return(ret)

    def __len__(self):
        return(len(self._data)-len(self._frees))

    def batch_add(self, values: list):
        vals = sorted(values, key=lambda x: x[0], reverse=True)
        print('batch add')
        for v in tqdm(vals):
            self.add(v)

    # @profile
    def add(self, val: tuple):
        node = unit(val)
        nodes = [val[2], val[3]]

        if not self._frees:
            pos = len(self._data)
            self._data.append(node)
        else:
            pos = self._frees.pop(0)
            self._data[pos] = node

        for n in nodes:
            self._byNode[n].append(pos)

        if self._head is None:
            self._head = pos
            self._tail = pos
        else:
            cursor = self._head
            last = self._head
            while (self._data[cursor].val[0] < val[0]):
                if self._data[cursor].next is not None:
                    last = cursor
                    cursor = self._data[cursor].next
                else: # at the tail
                    self._data[cursor].next = pos
                    self._data[pos].previous = cursor
                    self._tail = pos
                    return

            if (last == cursor):# at head
                self._data[pos].next=self._head
                self._data[self._head].previous=pos
                self._head=pos
                return
                

            self._data[pos].next = cursor
            self._data[pos].previous = last
            self._data[last].next = pos
            self._data[cursor].previous = pos

    def pop(self):
        """Removes and returns the lowest val"""
        if self._head is None:
            raise Exception("The structure is empty")
        val = self._data[self._head].val
        self._frees.append(self._head)
        self._head = self._data[self._head].next
        self._data[self._head].previous = None
        return(val)

    def _remove(self, pos):
        p = self._data[pos].previous
        n = self._data[pos].next
        if n is None:
            self._tail = p
        self._data[p].next = n
        self._data[n].previous = p
        self._frees.append(pos)

    def remove(self, nbunch: list):
        """ Removes all entries corresponding to nodes in  nbunch"""
        for n in nbunch:
            for pos in self._byNode[n]:
                self._remove(pos)
            del(self._byNode[n])

    def minVal(self) -> tuple:
        if self._head is None:
            raise Exception("The structure is empty")
        return(self._data[self._head].val)

    def maxVal(self) -> tuple:
        if self._tail is None:
            raise Exception("The structure is empty")
        return(self._data[self._tail].val)


if __name__ == "__main__":
    # testing
    S = SortedEdges()
    S.add((1, 1, 'a', 'b'))
    print(S)
    print('\n')
    S.add((3, 1, 'a', 'b'))
    print(S)
    print('\n')
    S.add((2, 1, 'a', 'b'))
    print(S)
    print('\n')
    S.add((0, 1, 'a', 'b'))
    print(S)
    print('\n')
    S.add((4, 1, 'a', 'b'))
    print(S)
    print('\n')
