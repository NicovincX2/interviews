#!/usr/bin/env python3

"""
knight_dialer.py
From https://alexgolec.dev/google-interview-questions-deconstructed-the-knights-dialer/
and https://alexgolec.dev/knights-dialer-logarithmic-time-edition/

Imagine you place a knight chess piece on a phone dial pad. This chess 
piece moves in an uppercase “L” shape: two steps horizontally followed 
by one vertically, or one step horizontally then two vertically:
1 2 3
4 5 6
7 8 9
  0

Suppose you dial keys on the keypad using only hops a knight can make. 
Every time the knight lands on a key, we dial that key and make another hop. 
The starting position counts as being dialed.

How many distinct numbers can you dial in N hops from a particular starting position?
"""

"""
This is a fine representation for a number of reasons. First off, it’s compact: 
we represent only the nodes and edges that exist in the graph (I include number 5 
for completeness, but we can remove it without any repercussions). Second off, 
it’s efficient to access: we can get the set of neighbors in constant time via a 
map lookup, we can iterate over all neighbors of a particular node in time linear 
to the number of neighbors by iterating over the result of that lookup. We can also 
easily modify this structure to determine the existence of an edge in constant time 
by using a sets instead of tuples.

This data structure is known as an adjacency list, named after the explicit listing 
of adjacent nodes to represent edges. This representation is by far the most common 
method of representing graphs, chiefly because of its linear-in-nodes-and-edges space 
complexity as well as its time-optimal access patterns. 
"""
NEIGHBORS_MAP = {
    1: (6, 8),
    2: (7, 9),
    3: (4, 8),
    4: (3, 9, 0),
    5: tuple(),  # 5 has no neighbors
    6: (1, 7, 0),
    7: (2, 6),
    8: (1, 3),
    9: (2, 4),
    0: (4, 6),
}

"""
There is another, more fruitful, way to represent a graph, though. You’ll notice a graph 
is all about relationships between nodes. In the case of an adjacency list, we relate each 
node with the nodes it’s connected to. Why not instead focus on pairs of nodes? Instead of 
asking “what nodes are connected to one another with an edge,” you can ask “given a pair 
of nodes, is there an edge that connects them?”

If this seems like a sort of “six of one, half dozen of another” situation, it is. But the 
second formulation is magical because it calls into focus something that’s invisible in the 
adjacency list representation: suddenly we’re very interested in pairs of nodes that don’t 
have edges. Rather than starting with nodes and computing only the relevant pairs, we start 
with all possible pairs, and decide whether or not they are relevant later.

We can reframe the adjacency list as follows. Note for each pair (A, B), NEIGHBORS_MATRIX[A][B] 
will be 1 if that pair represents an edge in the graph and 0 otherwise.

Why would we do this? Certainly not to create a more efficient data structure. Our space 
complexity has gone from being proportional to the number of edges to the number of possible 
edges, which means N squared, where N is the number of nodes. Iterating over neighbors also 
just got more expensive: for a given node we get a bunch of irrelevant zeros that we have 
to filter through.

In this matrix, each row represents the destinations accessible from each key: row 0 has a 1 
in position 4 to show you can hop from 0 to 4. It has a 0 in position 9 to show you can’t hop 
from 0 to 9.

The rows also have a meaning. While the rows represent where you can go from the corresponding 
position, the columns represent how can get to each position. If you look closely, you’ll notice 
that the rows and columns look strikingly similar: the i-th position in each row is the same as 
the i-th position in each column. This is because this graph is undirected: each edge can be 
traversed in both directions. As a result, the entire matrix can be flipped along its main 
diagonal and emerge unchanged (the main diagonal is formed by the positions where the row and 
column numbers are equal).

Each row represents the numbers you can reach from that row’s corresponding key. With this in 
mind, matrix multiplication is no longer an abstract algebraic operation, it’s a means of 
summing values corresponding to destinations from a given key on the dialpad.

This is nothing more than a weighted sum of values corresponding to destinations from a given 
key on a dialpad! This framing ignores edges that aren’t in the graph by not even considering 
them in the iteration, whereas the matrix-oriented one includes them, but only as multiplications 
by zero that don’t affect the final sum. The two statements are equivalent!
"""

NEIGHBORS_MATRIX = {
    0: (0, 0, 0, 0, 1, 0, 1, 0, 0, 0),
    1: (0, 0, 0, 0, 0, 0, 1, 0, 1, 0),
    2: (0, 0, 0, 0, 0, 0, 0, 1, 0, 1),
    3: (0, 0, 0, 1, 0, 0, 0, 0, 1, 0),
    4: (1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    5: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    6: (1, 1, 0, 0, 0, 0, 0, 1, 0, 0),
    7: (0, 0, 1, 0, 0, 0, 1, 0, 0, 0),
    8: (0, 1, 0, 1, 0, 0, 0, 0, 0, 0),
    9: (0, 0, 1, 0, 1, 0, 0, 0, 0, 0),
}


def neighbors(position):
    return NEIGHBORS_MAP[position]


"""
This problem can be solved by enumerating all possible numbers and counting them. 
You can use recursion to generate these values.

Notice, however, that we generate the numbers and never actually use them. 
This problem asks for the count of numbers, not the numbers themselves. 
Once we count a number we never revisit it. 
"""


def yield_sequences(starting_position, num_hops, sequence=None):
    if sequence is None:
        sequence = [starting_position]

    if num_hops == 0:
        yield sequence
        return

    for neighbor in neighbors(starting_position):
        yield from yield_sequences(neighbor, num_hops - 1, sequence + [neighbor])


def count_sequences(starting_position, num_hops):
    num_sequences = 0
    for sequence in yield_sequences(starting_position, num_hops):
        print(sequence)
        num_sequences += 1
    return num_sequences


"""
How can we count phone numbers without generating them? It can be done, but not 
without an additional insight. Notice how the count of numbers that can be generated 
from a given starting position in N hops is equal to the sum of the counts of hops 
that can be generated starting from each of its neighbors in N-1 hops.

For this implementation, every call to count_sequences() recursively calls 
count_sequences() at least twice, because each key has at least two neighbors. 
Since we recurse a number of times equal to the desired number of hops, and 
the number of calls to count_sequences() at least doubles with each call, 
we’re left with a runtime complexity of at least exponential time.
"""


def count_sequences_rec(start_position, num_hops):
    if num_hops == 0:
        return 1

    num_sequences = 0
    for position in neighbors(start_position):
        num_sequences += count_sequences_rec(position, num_hops - 1)
        print(
            "Position:", position, "Count:", num_sequences, "Nombre de sauts:", num_hops
        )
    return num_sequences


"""
We can use memoization (not memorization), which basically means we record results 
of function calls we’ve seen before and use those instead of redoing the work. 
This way, when we encounter a place in the call graph where we would unnecessarily 
recompute an entire subtree, we instead immediately return the result we already computed.

Each function call’s result is stored in the cache, and it’s inserted there exactly once. 
This allows us to reframe the question as “how does the size of the cache grow with the 
size of the input?” Given that the cache is keyed by position and number of hops, and 
there are exactly ten positions, we can conclude that the cache grows in direct proportion 
to the number of requested hops. This follows from the pigeonhole principle: once we have 
an entry in the cache for every combination of position and jump count, all calls will hit 
the cache rather than result in a new function call.

Linear time! That’s not bad. In fact, it’s remarkable: the addition of a simple cache 
changed the algorithm’s runtime from exponential to linear.

The major-ish drawback is that it’s recursive. 
"""


def count_sequences_mem(start_position, num_hops):
    cache = {}

    def helper(position, num_hops):
        if (position, num_hops) in cache:
            return cache[(position, num_hops)]

        if num_hops == 0:
            return 1

        else:
            num_sequences = 0
            for neighbor in neighbors(position):
                num_sequences += helper(neighbor, num_hops - 1)
                print(
                    "Position:",
                    position,
                    "Count:",
                    num_sequences,
                    "Nombre de sauts:",
                    num_hops,
                )
            cache[(position, num_hops)] = num_sequences
            return num_sequences

    res = helper(start_position, num_hops)
    return res


"""
Notice that the results for N hops depend only on the results for calls with N-1 hops. 
Meanwhile, the cache contains entries for every (nonzero) number of hops. I call this 
a minor issue because it doesn’t actually cause any real problems, given that the cache 
grows only linearly with the number of hops. Requiring linear space isn’t the end of 
the world, but still, it’s inefficient.

If you imagine the entire function call graph as a sort of virtual tree, you’ll quickly 
see we’re performing a depth-first traversal. This is fine, it gives a proper solution, 
but it doesn’t take advantage of the shallow dependency property I pointed out above.

Can you perform a breadth-first traversal instead, where you start at the top and “visit” 
function calls for N-1 hops only after you’ve visited those for N hops? Sadly, no. The 
values of function calls with nonzero hops absolutely require the values from smaller 
hop counts, so you won’t get any results until you reach the zero-hop layer and start 
returning numbers rather than additional function calls (note the zero-hop layer isn’t 
depicted here).

You can however, reverse the order: visit layers with N hops only after you’ve visited 
layers with N-1 hops. Those of you who studied or are studying discrete mathematics will 
recognize all the necessary ingredients for an induction: we know that the values of 
zero-hop function calls are always one (the base case). We also know how to combine 
N-1 hop values to get N hop values, using the recurrence relation (the inductive step). 
We can start with a base case of zero hops and induce all values greater than zero.

So what’s better about this version than the recursive, depth-first solution? Not a ton, 
but it has a few benefits. First off, it’s not recursive, meaning it can run for extremely 
large values without crashing. Second off, it uses constant memory, because it only ever 
needs two arrays of fixed size rather than the ever-growing cache of the memoization solution. 
Finally, it’s still linear time.
"""


def count_sequences_dyn(start_position, num_hops):
    prior_case = [1] * 10
    current_case = [0] * 10
    current_num_hops = 1

    while current_num_hops <= num_hops:
        current_case = [0] * 10
        current_num_hops += 1

        for position in range(0, 10):
            for neighbor in neighbors(position):
                print(current_case, position, prior_case)
                current_case[position] += prior_case[neighbor]
        prior_case = current_case

    return current_case[start_position]


"""
On the face of it, this solution seems awesome. It features logarithmic time complexity 
and constant space complexity. You might think it really doesn’t get any better than that, 
and for this particular problem you would be right.

However, this matrix exponentiation-based approach has one glaring drawback: we need to 
represent the entire graph as a (potentially very sparse) matrix. This implies we’ll have 
to explicitly store a value of every possible pair of nodes, which requires space quadratic 
in the number of nodes. For a 10-node graph like this one, that isn’t a problem, but for more 
realistic graphs which might have thousands if not millions of nodes, it becomes hopelessly 
infeasible.

What’s worse, the matrix multiplication I gave up there is actually cubic in the number of 
rows (for square matrices). The best-known matrix multiplication algorithms like Strassen or 
Coppersmith–Winograd have sub-cubic runtimes, but either require extreme memory overhead or 
feature constant factors that negate the effects for matrices of reasonable size. A cubic-time 
matrix multiplication starts to become unreasonable with graphs with sizes around the ten 
thousand range.

At the end of the day, none of these limitations really matter in my mind. Let’s be honest: 
how often are you going to be computing this on any realistic graph? Feel free to correct me 
in the comments, but I personally can’t think of any practical application of this algorithm.
"""


def matrix_multiply(A, B):
    A_rows, _ = len(A), len(A[0])
    B_rows, B_cols = len(B), len(B[0])
    result = list(map(lambda i: [0] * B_cols, range(A_rows)))

    for row in range(A_rows):
        for col in range(B_cols):
            for i in range(B_rows):
                result[row][col] += A[row][i] * B[i][col]

    return result


def count_sequences_log(start_position, num_hops):
    # Start off with a 10x10 identity matrix
    accum = [[1 if i == j else 0 for i in range(10)] for j in range(10)]

    # bin(num_hops) starts with "0b", slice it off with [2:]
    for bit_num, bit in enumerate(reversed(bin(num_hops)[2:])):
        if bit_num == 0:
            import copy

            power_of_2 = copy.deepcopy(NEIGHBORS_MATRIX)
        else:
            power_of_2 = matrix_multiply(power_of_2, power_of_2)

        if bit == "1":
            accum = matrix_multiply(accum, power_of_2)

    return matrix_multiply(accum, [[1]] * 10)[start_position][0]


def main():
    print("Generate sequences and count them:")
    print(count_sequences(6, 2))
    print("Recursive count:")
    print(count_sequences_rec(6, 2))
    print("Memoization of the recursive count:")
    print(count_sequences_mem(6, 2))
    print("Dynamic programming solution:")
    print(count_sequences_dyn(6, 2))
    print("Logarithmic matrix power solution:")
    print(count_sequences_log(6, 2))


if __name__ == "__main__":
    main()
