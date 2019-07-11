from collections import defaultdict
from tqdm import tqdm
from numpy import floor

class unit:
    def __init__(self, val=None):
        self.val = val
        self.next = None
        self.previous = None


N_INDEX=1000

class SortedEdges:
    def __init__(self):
        self._data = []
        self._frees = []
        self._head = None
        self._tail = None
        self._byNode = defaultdict(list)
        self._index = [{'val':None,'loc':-1} for _ in range(N_INDEX)]

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
        """
            Adds to the structure.
            val: -> ((v,#),x,y)
            v = 0-1 priority value (smaller first)
            # = tie breaking
            (x,y) related info (see .remove)
        """
        node = unit(val)
        nodes = list(val[1:])


        if not self._frees:
            pos = len(self._data)
            self._data.append(node)
        else:
            pos = self._frees.pop()
            self._data[pos] = node


        priority = val[0][0]
        hint = self._head
        bin = int(floor(priority/(1/N_INDEX)))
        if (self._index[bin]['val'] is not None):
            hint = self._index[bin]['loc']
            #if we dont have values, or the value belongs to the bin, but it is larger (or it doesn't belong to the bin)
        if (self._index[bin]['val'] is None) or (self._index[bin]['val']>priority) or (self._index[bin]['val']<(bin*(1/N_INDEX))):
            self._index[bin]['val']=priority
            self._index[bin]['loc']=pos


        for n in nodes:
            self._byNode[n].append(pos)

        if self._head is None:
            self._head = pos
            self._tail = pos
            return
        if self._data[self._head].val[0] >= val[0]: #at the head
            self._data[pos].next=self._head
            self._data[self._head].previous=pos
            self._head=pos
            return
        if self._data[self._tail].val[0] < val[0]: #at the tail
            self._data[self._tail].next = pos
            self._data[pos].previous = self._tail
            self._tail = pos
            return

        cursor = hint
        while (self._data[cursor].val[0] < val[0]):
            cursor = self._data[cursor].next

        last = self._data[cursor].previous
        self._data[pos].next = cursor
        self._data[pos].previous = last
        if last is not None:
            self._data[last].next = pos
        self._data[cursor].previous = pos

    def pop(self):
        """Removes and returns the lowest val"""
        if (self._head is None) or (len(self)==0):
            raise Exception("The structure is empty")
        val = self._data[self._head].val
        self._frees.append(self._head)
        if len(self)==0:
            self._head=None
            self._tail=None
        else:
            self._head = self._data[self._head].next
            self._data[self._head].previous = None
        return(val)

    def _remove(self, pos):
        """Removes an entry. If it is already marked as removed, do nothing (and don't fail)"""
        if pos in self._frees:
            return
        self._frees.append(pos)

        if len(self)==0:
            self._head=None
            self._tail=None
            self._index= [{'val':None,'loc':-1} for _ in range(N_INDEX)]
        else:
            if self._data[pos].previous is None:
                p=self._head
            else:
                p = self._data[pos].previous

            bin = int(floor(self._data[pos].val[0][0]/(1/N_INDEX)))
            if pos == self._index[bin]['loc']:
                self._index[bin]['val']=self._data[p].val[0][0]
                self._index[bin]['loc']=p


            if pos == self._head:
                self._head=self._data[pos].next
            elif pos == self._tail:
                self._tail=self._data[pos].previous   
            else:
                n = self._data[pos].next
                p = self._data[pos].previous
                if n is not None:
                    self._data[n].previous=p
                if p is not None:
                    self._data[p].next=n        

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
    S.add(((0.05, 1), 'a', 'b'))
    S.add(((0.515, 1), 'a', 'b'))
    S.add(((0.52, 1), 'a', 'b'))
    S.add(((0.510, 1), 'a', 'b'))
    print(S)
