from collections import deque

graph = {}
graph["you"] = ["alice", "bob", "claire"]
graph["bob"] = ["anju", "peggy"]
graph["alice"] = ["peggy"]
graph["claire"] = ["thom", "jonny"]

search_queue = deque()
search_queue += graph["you"]
print(search_queue)