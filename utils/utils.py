
from collections import deque, defaultdict


def topological_sort(relations):
    # Creating a graph
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Filling the graph and in-degree dictionary
    for relation in relations:
        graph[relation.target].append(relation.source)
        in_degree[relation.source] += 1
        if relation.target not in in_degree:
            in_degree[relation.target] = 0

    # Initialize the queue with nodes having in-degree 0
    queue = deque([node for node in in_degree if in_degree[node] == 0])

    sorted_order = []

    # Process until the queue is empty
    while queue:
        node = queue.popleft()
        sorted_order.append(node)

        # Decrease the in-degree of dependent nodes
        for dependent in graph[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Check for cycle in the graph
    if len(sorted_order) != len(in_degree):
        return "Cycle detected in graph, sorting not possible"

    return sorted_order[::]  # reverse to get highest hierarchy first
